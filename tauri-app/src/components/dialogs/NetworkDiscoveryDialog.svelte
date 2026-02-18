<script lang="ts">
  import DialogWrapper from "./DialogWrapper.svelte";
  import { activeDialog } from "../../lib/stores/uiStore";
  import { effectiveColors } from "../../lib/theme/colors";
  import { currentTheme } from "../../lib/stores/uiStore";
  import { invoke } from "@tauri-apps/api/core";
  import { listen } from "@tauri-apps/api/event";
  import {
    createNodesFromDiscovery,
    createNodesFromMergedDiscovery,
    mergeDevicesByMac,
    type DiscoveredDevice,
    type MergedDevice,
    type RangeResult,
  } from "../../lib/actions/discoveryActions";

  interface SubnetInfo {
    ip: string;
    subnet_mask: string;
    cidr: string;
    interface_name: string;
  }

  interface DiscoveryProgress {
    phase: string;
    current: number;
    total: number;
    found_so_far: number;
    message: string;
  }

  interface IpRange {
    startIp: string;
    endIp: string;
    label: string;
  }

  let colors = $derived($effectiveColors);
  let isIronclad = $derived($currentTheme === "ironclad");

  // Wizard step
  let step = $state<"config" | "scanning" | "results">("config");

  // Scan mode
  let scanMode = $state<"autodetect" | "custom">("autodetect");

  // Config step state
  let subnets = $state<SubnetInfo[]>([]);
  let selectedSubnetIdx = $state(0);
  let scanDepth = $state<"minimal" | "basic" | "ports">("basic");
  let layout = $state<"grid" | "circle">("grid");
  let clearExisting = $state(true);
  let loadingSubnets = $state(true);
  let subnetError = $state("");

  // Custom ranges
  let customRanges = $state<IpRange[]>([
    { startIp: "", endIp: "", label: "Range 1" },
  ]);

  // Scanning step state
  let progressPhase = $state("");
  let progressCurrent = $state(0);
  let progressTotal = $state(1);
  let progressFound = $state(0);
  let progressMessage = $state("Starting scan...");
  let currentRangeIndex = $state(0);

  // Results step state
  let devices = $state<DiscoveredDevice[]>([]);
  let mergedDevices = $state<MergedDevice[]>([]);
  let mergedVlanConfig = $state<{
    labels: Record<string, string>;
    order: string[];
  } | null>(null);
  let selected = $state<boolean[]>([]);
  let scanError = $state("");

  function close() {
    activeDialog.set(null);
  }

  // Load subnets on mount
  import { onMount } from "svelte";
  onMount(async () => {
    try {
      const result = await invoke<SubnetInfo[]>("get_subnets");
      subnets = result;
      if (result.length > 0) {
        selectedSubnetIdx = 0;
      }
    } catch (e) {
      subnetError = `Failed to detect network interfaces: ${e}`;
    } finally {
      loadingSubnets = false;
    }
  });

  // IP utility functions
  function ipToNumber(ip: string): number | null {
    const parts = ip.split(".").map(Number);
    if (
      parts.length !== 4 ||
      parts.some((p) => isNaN(p) || p < 0 || p > 255)
    )
      return null;
    return ((parts[0] << 24) | (parts[1] << 16) | (parts[2] << 8) | parts[3]) >>> 0;
  }

  function rangeIpCount(start: string, end: string): number | null {
    const s = ipToNumber(start);
    const e = ipToNumber(end);
    if (s === null || e === null || e < s) return null;
    return e - s + 1;
  }

  function isValidIp(ip: string): boolean {
    return ipToNumber(ip) !== null;
  }

  // Time estimation
  function estimateSeconds(totalIps: number, depth: string): number {
    // Ping sweep: ~1s per 30 IPs
    let seconds = Math.ceil(totalIps / 30);

    if (depth === "basic" || depth === "ports") {
      const liveEstimate = Math.max(1, Math.ceil(totalIps * 0.1));
      seconds += 1; // ARP
      seconds += Math.ceil(liveEstimate / 10); // hostname
    }

    if (depth === "ports") {
      const liveEstimate = Math.max(1, Math.ceil(totalIps * 0.1));
      seconds += Math.ceil((liveEstimate * 8) / 20);
    }

    return seconds;
  }

  function formatTime(seconds: number): string {
    if (seconds < 60) return `~${seconds} seconds`;
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    if (secs === 0) return `~${mins} minute${mins > 1 ? "s" : ""}`;
    return `~${mins}m ${secs}s`;
  }

  // Computed: total IPs for current config
  let totalIps = $derived.by(() => {
    if (scanMode === "autodetect") {
      if (subnets.length === 0) return 0;
      const subnet = subnets[selectedSubnetIdx];
      if (!subnet) return 0;
      // Estimate from CIDR
      const cidrMatch = subnet.cidr.match(/\/(\d+)$/);
      if (!cidrMatch) return 254;
      const prefix = parseInt(cidrMatch[1]);
      return Math.max(1, Math.pow(2, 32 - prefix) - 2);
    } else {
      let total = 0;
      for (const range of customRanges) {
        const count = rangeIpCount(range.startIp, range.endIp);
        if (count !== null) total += count;
      }
      return total;
    }
  });

  let estimatedTime = $derived(estimateSeconds(totalIps, scanDepth));
  let showTimeWarning = $derived(estimatedTime > 120);

  // Custom range validation
  let rangeErrors = $derived.by(() => {
    return customRanges.map((range) => {
      if (!range.startIp && !range.endIp) return "";
      if (range.startIp && !isValidIp(range.startIp)) return "Invalid start IP";
      if (range.endIp && !isValidIp(range.endIp)) return "Invalid end IP";
      if (range.startIp && range.endIp) {
        const count = rangeIpCount(range.startIp, range.endIp);
        if (count === null) return "End IP must be >= start IP";
        if (count > 4094) return "Range too large (max 4094)";
      }
      return "";
    });
  });

  let hasValidRanges = $derived.by(() => {
    if (scanMode === "autodetect") return subnets.length > 0;
    return customRanges.some(
      (r, i) =>
        r.startIp &&
        r.endIp &&
        !rangeErrors[i] &&
        rangeIpCount(r.startIp, r.endIp) !== null
    );
  });

  function addRange() {
    customRanges = [
      ...customRanges,
      { startIp: "", endIp: "", label: `Range ${customRanges.length + 1}` },
    ];
  }

  function removeRange(index: number) {
    customRanges = customRanges.filter((_, i) => i !== index);
  }

  async function startScan() {
    step = "scanning";
    scanError = "";
    progressPhase = "ping_sweep";
    progressCurrent = 0;
    progressTotal = 1;
    progressFound = 0;
    progressMessage = "Starting scan...";
    currentRangeIndex = 0;
    mergedVlanConfig = null;
    mergedDevices = [];

    const unlisten = await listen<DiscoveryProgress>(
      "discovery-progress",
      (event) => {
        progressPhase = event.payload.phase;
        progressCurrent = event.payload.current;
        progressTotal = event.payload.total;
        progressFound = event.payload.found_so_far;
        progressMessage = event.payload.message;
      }
    );

    try {
      if (scanMode === "autodetect") {
        const subnet = subnets[selectedSubnetIdx];
        const result = await invoke<DiscoveredDevice[]>("discover_network", {
          subnetIp: subnet.ip,
          subnetMask: subnet.subnet_mask,
          scanDepth: scanDepth,
        });
        devices = result;
        selected = result.map(() => true);
        step = "results";
      } else {
        // Custom ranges: scan sequentially
        const validRanges = customRanges.filter(
          (r, i) =>
            r.startIp &&
            r.endIp &&
            !rangeErrors[i] &&
            rangeIpCount(r.startIp, r.endIp) !== null
        );

        const allResults: RangeResult[] = [];

        for (let i = 0; i < validRanges.length; i++) {
          currentRangeIndex = i;
          const range = validRanges[i];

          const ipList = await invoke<string[]>("generate_range_ips", {
            startIp: range.startIp,
            endIp: range.endIp,
          });

          const result = await invoke<DiscoveredDevice[]>(
            "discover_ip_range",
            {
              ipList: ipList,
              scanDepth: scanDepth,
              rangeLabel: range.label,
            }
          );

          allResults.push({ label: range.label, devices: result });
        }

        // Merge by MAC
        const merged = mergeDevicesByMac(allResults);
        mergedDevices = merged.devices;
        mergedVlanConfig = {
          labels: merged.vlanLabels,
          order: merged.vlanLabelOrder,
        };
        selected = merged.devices.map(() => true);
        step = "results";
      }
    } catch (e) {
      scanError = `Scan failed: ${e}`;
      step = "config";
    } finally {
      unlisten();
    }
  }

  function handleCreateMap() {
    if (mergedVlanConfig) {
      // Custom range mode — use merged devices
      const selectedMerged = mergedDevices.filter((_, i) => selected[i]);
      if (selectedMerged.length === 0) return;
      createNodesFromMergedDiscovery(
        selectedMerged,
        mergedVlanConfig,
        layout,
        clearExisting
      );
    } else {
      // Auto-detect mode — use flat devices
      const selectedDevices = devices.filter((_, i) => selected[i]);
      if (selectedDevices.length === 0) return;
      createNodesFromDiscovery(selectedDevices, layout, clearExisting);
    }
  }

  function toggleAll() {
    const allSelected = selected.every((s) => s);
    selected = selected.map(() => !allSelected);
  }

  let selectedCount = $derived(selected.filter((s) => s).length);
  let resultCount = $derived(
    mergedVlanConfig ? mergedDevices.length : devices.length
  );

  let progressPercent = $derived(
    progressTotal > 0
      ? Math.round((progressCurrent / progressTotal) * 100)
      : 0
  );

  let phaseLabel = $derived(
    progressPhase === "ping_sweep"
      ? "Ping Sweep"
      : progressPhase === "arp_lookup"
        ? "ARP Lookup"
        : progressPhase === "hostname_resolution"
          ? "Hostname Resolution"
          : progressPhase === "port_scan"
            ? "Port Scan"
            : progressPhase === "complete"
              ? "Complete"
              : "Starting..."
  );

  let buttonClass = $derived(
    "px-4 py-2 text-sm rounded hover:opacity-80 transition-opacity" +
      (isIronclad ? " ironclad-btn" : "")
  );

  let smallBtnClass = $derived(
    "px-3 py-1 text-xs rounded hover:opacity-80 transition-opacity" +
      (isIronclad ? " ironclad-btn" : "")
  );

  let inputClass = $derived(
    "px-2 py-1 text-xs rounded border" + (isIronclad ? " ironclad-btn" : "")
  );

  function portBadges(ports: number[]): { label: string; title: string }[] {
    const badges: { label: string; title: string }[] = [];
    if (ports.includes(80) || ports.includes(443))
      badges.push({ label: "Web", title: "HTTP/HTTPS" });
    if (ports.includes(8080))
      badges.push({ label: "Alt Web", title: "Alternate HTTP (8080)" });
    if (ports.includes(3389))
      badges.push({ label: "RDP", title: "Remote Desktop" });
    if (ports.includes(22))
      badges.push({ label: "SSH", title: "Secure Shell" });
    if (ports.includes(631) || ports.includes(9100))
      badges.push({ label: "Printer", title: "IPP/JetDirect" });
    if (ports.includes(5353))
      badges.push({ label: "mDNS", title: "mDNS/Bonjour" });
    return badges;
  }

  // How many ranges a merged device appears in
  function mergedRangeCount(device: MergedDevice): number {
    return Object.keys(device.ips).length;
  }
</script>

<DialogWrapper title="Network Discovery" width={780} onClose={close}>
  {#if step === "config"}
    <!-- Configuration Step -->
    <div class="space-y-4">
      <p class="text-sm opacity-70" style:color={colors.BUTTON_TEXT}>
        Scan your local network to automatically discover devices and create a
        topology map.
      </p>

      <!-- Scan Mode Toggle -->
      <div>
        <label
          class="block text-xs font-medium mb-2"
          style:color={colors.BUTTON_TEXT}
        >
          Scan Mode
        </label>
        <div class="flex gap-4">
          <label
            class="flex items-center gap-2 cursor-pointer"
            style:color={colors.BUTTON_TEXT}
          >
            <input
              type="radio"
              bind:group={scanMode}
              value="autodetect"
            />
            <span class="text-sm">Auto-detect subnet</span>
          </label>
          <label
            class="flex items-center gap-2 cursor-pointer"
            style:color={colors.BUTTON_TEXT}
          >
            <input type="radio" bind:group={scanMode} value="custom" />
            <span class="text-sm">Custom IP ranges</span>
          </label>
        </div>
      </div>

      <!-- Auto-detect: Subnet Selection -->
      {#if scanMode === "autodetect"}
        <div>
          <label
            class="block text-xs font-medium mb-1"
            style:color={colors.BUTTON_TEXT}
          >
            Network Interface
          </label>
          {#if loadingSubnets}
            <p class="text-xs opacity-60" style:color={colors.BUTTON_TEXT}>
              Detecting network interfaces...
            </p>
          {:else if subnetError}
            <p class="text-xs text-red-400">{subnetError}</p>
          {:else if subnets.length === 0}
            <p class="text-xs text-red-400">
              No network interfaces found. Make sure you are connected to a
              network.
            </p>
          {:else}
            <select
              class="w-full px-3 py-2 text-sm rounded border"
              style:background-color={colors.FRAME_BG}
              style:color={colors.BUTTON_TEXT}
              style:border-color={colors.BORDER_COLOR}
              bind:value={selectedSubnetIdx}
            >
              {#each subnets as subnet, i}
                <option value={i}>
                  {subnet.interface_name} — {subnet.cidr} (Your IP: {subnet.ip})
                </option>
              {/each}
            </select>
          {/if}
        </div>
      {/if}

      <!-- Custom: IP Range Editor -->
      {#if scanMode === "custom"}
        <div>
          <label
            class="block text-xs font-medium mb-2"
            style:color={colors.BUTTON_TEXT}
          >
            IP Ranges
          </label>
          <div class="space-y-2">
            {#each customRanges as range, i}
              <div
                class="flex items-start gap-2 p-2 rounded border"
                style:border-color={rangeErrors[i]
                  ? "#ef4444"
                  : colors.BORDER_COLOR}
                style:background-color={colors.FRAME_BG}
              >
                <div class="flex-1 space-y-1">
                  <div class="flex gap-2 items-center">
                    <input
                      type="text"
                      class={inputClass}
                      style:background-color={colors.FRAME_BG}
                      style:color={colors.BUTTON_TEXT}
                      style:border-color={range.startIp &&
                      !isValidIp(range.startIp)
                        ? "#ef4444"
                        : colors.BORDER_COLOR}
                      placeholder="Start IP (e.g. 192.168.1.1)"
                      bind:value={range.startIp}
                    />
                    <span
                      class="text-xs opacity-60"
                      style:color={colors.BUTTON_TEXT}>to</span
                    >
                    <input
                      type="text"
                      class={inputClass}
                      style:background-color={colors.FRAME_BG}
                      style:color={colors.BUTTON_TEXT}
                      style:border-color={range.endIp &&
                      !isValidIp(range.endIp)
                        ? "#ef4444"
                        : colors.BORDER_COLOR}
                      placeholder="End IP (e.g. 192.168.1.254)"
                      bind:value={range.endIp}
                    />
                  </div>
                  <div class="flex gap-2 items-center">
                    <input
                      type="text"
                      class="{inputClass} flex-1"
                      style:background-color={colors.FRAME_BG}
                      style:color={colors.BUTTON_TEXT}
                      style:border-color={colors.BORDER_COLOR}
                      placeholder="Label (e.g. Office Network)"
                      bind:value={range.label}
                    />
                    {#if rangeIpCount(range.startIp, range.endIp) !== null}
                      <span
                        class="text-[10px] opacity-50"
                        style:color={colors.BUTTON_TEXT}
                      >
                        {rangeIpCount(range.startIp, range.endIp)} IPs
                      </span>
                    {/if}
                  </div>
                  {#if rangeErrors[i]}
                    <p class="text-[10px] text-red-400">{rangeErrors[i]}</p>
                  {/if}
                </div>
                {#if customRanges.length > 1}
                  <button
                    class="text-xs px-2 py-1 rounded hover:opacity-80"
                    style:color={colors.BUTTON_TEXT}
                    style:background-color={colors.BUTTON_BG}
                    onclick={() => removeRange(i)}
                  >
                    &times;
                  </button>
                {/if}
              </div>
            {/each}
          </div>
          <button
            class="{smallBtnClass} mt-2"
            style:background-color={colors.BUTTON_BG}
            style:color={colors.BUTTON_TEXT}
            onclick={addRange}
          >
            + Add Range
          </button>
        </div>
      {/if}

      <!-- Scan Depth -->
      <div>
        <label
          class="block text-xs font-medium mb-2"
          style:color={colors.BUTTON_TEXT}
        >
          Scan Depth
        </label>
        <div class="space-y-2">
          <label
            class="flex items-start gap-2 cursor-pointer"
            style:color={colors.BUTTON_TEXT}
          >
            <input
              type="radio"
              bind:group={scanDepth}
              value="minimal"
              class="mt-0.5"
            />
            <div>
              <span class="text-sm font-medium">Quick Scan</span>
              <p class="text-xs opacity-60">Find live devices only (fastest)</p>
            </div>
          </label>
          <label
            class="flex items-start gap-2 cursor-pointer"
            style:color={colors.BUTTON_TEXT}
          >
            <input
              type="radio"
              bind:group={scanDepth}
              value="basic"
              class="mt-0.5"
            />
            <div>
              <span class="text-sm font-medium">Standard Scan</span>
              <p class="text-xs opacity-60">
                Devices + hostnames + MAC addresses
              </p>
            </div>
          </label>
          <label
            class="flex items-start gap-2 cursor-pointer"
            style:color={colors.BUTTON_TEXT}
          >
            <input
              type="radio"
              bind:group={scanDepth}
              value="ports"
              class="mt-0.5"
            />
            <div>
              <span class="text-sm font-medium">Full Scan</span>
              <p class="text-xs opacity-60">
                Also detect web interfaces & remote desktop (slowest)
              </p>
            </div>
          </label>
        </div>
      </div>

      <!-- Time Estimate -->
      {#if totalIps > 0}
        <div
          class="text-xs px-3 py-2 rounded"
          style:background-color={showTimeWarning
            ? "rgba(234, 179, 8, 0.15)"
            : "rgba(100, 100, 100, 0.1)"}
          style:color={showTimeWarning ? "#eab308" : colors.BUTTON_TEXT}
          style:border={showTimeWarning
            ? "1px solid rgba(234, 179, 8, 0.3)"
            : "none"}
        >
          <span class="font-medium">Estimated scan time:</span>
          {formatTime(estimatedTime)}
          ({totalIps.toLocaleString()} IPs)
          {#if showTimeWarning}
            <p class="mt-1 opacity-80">
              This may take a while. Consider using Quick Scan or reducing the
              IP range.
            </p>
          {/if}
        </div>
      {/if}

      <!-- Layout Choice -->
      <div>
        <label
          class="block text-xs font-medium mb-2"
          style:color={colors.BUTTON_TEXT}
        >
          Node Layout
        </label>
        <div class="flex gap-4">
          <label
            class="flex items-center gap-2 cursor-pointer"
            style:color={colors.BUTTON_TEXT}
          >
            <input type="radio" bind:group={layout} value="grid" />
            <span class="text-sm">Grid</span>
          </label>
          <label
            class="flex items-center gap-2 cursor-pointer"
            style:color={colors.BUTTON_TEXT}
          >
            <input type="radio" bind:group={layout} value="circle" />
            <span class="text-sm">Circle</span>
          </label>
        </div>
      </div>

      <!-- Clear existing -->
      <label
        class="flex items-center gap-2 cursor-pointer"
        style:color={colors.BUTTON_TEXT}
      >
        <input type="checkbox" bind:checked={clearExisting} />
        <span class="text-xs">Clear existing map first</span>
      </label>

      {#if scanError}
        <p class="text-xs text-red-400">{scanError}</p>
      {/if}

      <!-- Actions -->
      <div class="flex gap-2 pt-2">
        <button
          class={buttonClass + " flex-1"}
          style:background-color={colors.BUTTON_BG}
          style:color={colors.BUTTON_TEXT}
          onclick={startScan}
          disabled={!hasValidRanges || loadingSubnets}
        >
          Start Scan
        </button>
        <button
          class={buttonClass}
          style:background-color={colors.BUTTON_BG}
          style:color={colors.BUTTON_TEXT}
          onclick={close}
        >
          Cancel
        </button>
      </div>
    </div>
  {:else if step === "scanning"}
    <!-- Scanning Step -->
    <div class="space-y-4">
      {#if scanMode === "custom" && customRanges.length > 1}
        <p
          class="text-xs text-center opacity-60"
          style:color={colors.BUTTON_TEXT}
        >
          Range {currentRangeIndex + 1} of {customRanges.filter((r, i) => r.startIp && r.endIp && !rangeErrors[i]).length}
        </p>
      {/if}

      <div class="text-center">
        <p class="text-sm font-medium mb-1" style:color={colors.BUTTON_TEXT}>
          {phaseLabel}
        </p>
        <p class="text-xs opacity-60 mb-3" style:color={colors.BUTTON_TEXT}>
          {progressMessage}
        </p>
      </div>

      <!-- Progress Bar -->
      <div
        class="w-full h-3 rounded-full overflow-hidden"
        style:background-color={colors.BORDER_COLOR}
      >
        <div
          class="h-full rounded-full transition-all duration-300"
          style:width="{progressPercent}%"
          style:background-color={colors.BUTTON_ACTIVE_BG ?? colors.BUTTON_BG}
        ></div>
      </div>

      <div
        class="flex justify-between text-xs opacity-60"
        style:color={colors.BUTTON_TEXT}
      >
        <span>{progressPercent}%</span>
        <span>{progressFound} devices found</span>
      </div>

      <div class="flex justify-center pt-2">
        <button
          class={buttonClass}
          style:background-color={colors.BUTTON_BG}
          style:color={colors.BUTTON_TEXT}
          onclick={close}
        >
          Cancel
        </button>
      </div>
    </div>
  {:else if step === "results"}
    <!-- Results Step -->
    <div class="space-y-3">
      {#if resultCount === 0}
        <p
          class="text-sm text-center py-4"
          style:color={colors.BUTTON_TEXT}
        >
          No devices found. Try a different network interface or check your
          connection.
        </p>
        <div class="flex gap-2">
          <button
            class={buttonClass + " flex-1"}
            style:background-color={colors.BUTTON_BG}
            style:color={colors.BUTTON_TEXT}
            onclick={() => (step = "config")}
          >
            Back
          </button>
          <button
            class={buttonClass}
            style:background-color={colors.BUTTON_BG}
            style:color={colors.BUTTON_TEXT}
            onclick={close}
          >
            Close
          </button>
        </div>
      {:else}
        <div class="flex items-center justify-between">
          <p class="text-xs" style:color={colors.BUTTON_TEXT}>
            {selectedCount} of {resultCount} devices selected
          </p>
          <button
            class={smallBtnClass}
            style:background-color={colors.BUTTON_BG}
            style:color={colors.BUTTON_TEXT}
            onclick={toggleAll}
          >
            {selected.every((s) => s) ? "Deselect All" : "Select All"}
          </button>
        </div>

        <!-- Results Table -->
        <div
          class="border rounded overflow-auto"
          style:border-color={colors.BORDER_COLOR}
          style:max-height="350px"
        >
          {#if mergedVlanConfig}
            <!-- Merged results table (custom ranges) -->
            <table
              class="w-full text-xs"
              style:color={colors.BUTTON_TEXT}
            >
              <thead>
                <tr
                  class="sticky top-0"
                  style:background-color={colors.FRAME_BG}
                  style:border-bottom="1px solid {colors.BORDER_COLOR}"
                >
                  <th class="px-2 py-1.5 text-left w-8"></th>
                  {#each mergedVlanConfig.order as vlanKey}
                    <th class="px-2 py-1.5 text-left"
                      >{mergedVlanConfig.labels[vlanKey]}</th
                    >
                  {/each}
                  <th class="px-2 py-1.5 text-left">Hostname</th>
                  <th class="px-2 py-1.5 text-left">Vendor</th>
                  <th class="px-2 py-1.5 text-left">MAC</th>
                  <th class="px-2 py-1.5 text-left">Services</th>
                </tr>
              </thead>
              <tbody>
                {#each mergedDevices as device, i}
                  <tr
                    class="hover:opacity-80 cursor-pointer"
                    style:border-bottom="1px solid {colors.BORDER_COLOR}"
                    onclick={() => (selected[i] = !selected[i])}
                  >
                    <td class="px-2 py-1.5">
                      <input
                        type="checkbox"
                        checked={selected[i]}
                        onclick={(e: MouseEvent) => e.stopPropagation()}
                        onchange={() => (selected[i] = !selected[i])}
                      />
                    </td>
                    {#each mergedVlanConfig.order as vlanKey}
                      <td class="px-2 py-1.5 font-mono">
                        {device.ips[vlanKey] || "—"}
                      </td>
                    {/each}
                    <td class="px-2 py-1.5 truncate max-w-[150px]">
                      {device.hostname || "—"}
                    </td>
                    <td class="px-2 py-1.5 truncate max-w-[120px]">
                      {device.vendor || "—"}
                    </td>
                    <td class="px-2 py-1.5 font-mono text-[10px]">
                      {#if device.mac_address}
                        {device.mac_address}
                        {#if mergedRangeCount(device) > 1}
                          <span
                            class="ml-1 px-1 py-0.5 rounded text-[9px]"
                            style:background-color={colors.BUTTON_ACTIVE_BG ??
                              colors.BUTTON_BG}
                            title="Found on {mergedRangeCount(device)} ranges — same physical device"
                          >
                            {mergedRangeCount(device)} ranges
                          </span>
                        {/if}
                      {:else}
                        —
                      {/if}
                    </td>
                    <td class="px-2 py-1.5">
                      <div class="flex gap-1">
                        {#each portBadges(device.open_ports) as badge}
                          <span
                            class="px-1.5 py-0.5 rounded text-[10px] font-medium"
                            style:background-color={colors.BUTTON_BG}
                            title={badge.title}
                          >
                            {badge.label}
                          </span>
                        {/each}
                      </div>
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          {:else}
            <!-- Standard results table (auto-detect) -->
            <table
              class="w-full text-xs"
              style:color={colors.BUTTON_TEXT}
            >
              <thead>
                <tr
                  class="sticky top-0"
                  style:background-color={colors.FRAME_BG}
                  style:border-bottom="1px solid {colors.BORDER_COLOR}"
                >
                  <th class="px-2 py-1.5 text-left w-8"></th>
                  <th class="px-2 py-1.5 text-left">IP Address</th>
                  <th class="px-2 py-1.5 text-left">Hostname</th>
                  <th class="px-2 py-1.5 text-left">Vendor</th>
                  <th class="px-2 py-1.5 text-left">MAC</th>
                  <th class="px-2 py-1.5 text-left">Services</th>
                </tr>
              </thead>
              <tbody>
                {#each devices as device, i}
                  <tr
                    class="hover:opacity-80 cursor-pointer"
                    style:border-bottom="1px solid {colors.BORDER_COLOR}"
                    onclick={() => (selected[i] = !selected[i])}
                  >
                    <td class="px-2 py-1.5">
                      <input
                        type="checkbox"
                        checked={selected[i]}
                        onclick={(e: MouseEvent) => e.stopPropagation()}
                        onchange={() => (selected[i] = !selected[i])}
                      />
                    </td>
                    <td class="px-2 py-1.5 font-mono">{device.ip}</td>
                    <td class="px-2 py-1.5 truncate max-w-[150px]">
                      {device.hostname || "—"}
                    </td>
                    <td class="px-2 py-1.5 truncate max-w-[120px]">
                      {device.vendor || "—"}
                    </td>
                    <td class="px-2 py-1.5 font-mono text-[10px]">
                      {device.mac_address || "—"}
                    </td>
                    <td class="px-2 py-1.5">
                      <div class="flex gap-1">
                        {#each portBadges(device.open_ports) as badge}
                          <span
                            class="px-1.5 py-0.5 rounded text-[10px] font-medium"
                            style:background-color={colors.BUTTON_BG}
                            title={badge.title}
                          >
                            {badge.label}
                          </span>
                        {/each}
                      </div>
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          {/if}
        </div>

        <!-- Layout reminder -->
        <p
          class="text-xs opacity-50"
          style:color={colors.BUTTON_TEXT}
        >
          Layout: {layout === "grid" ? "Grid" : "Circle"}
          {clearExisting
            ? "(existing map will be cleared)"
            : "(adding to existing map)"}
        </p>

        <!-- Actions -->
        <div class="flex gap-2 pt-1">
          <button
            class={buttonClass + " flex-1"}
            style:background-color={colors.BUTTON_BG}
            style:color={colors.BUTTON_TEXT}
            onclick={handleCreateMap}
            disabled={selectedCount === 0}
          >
            Create Map ({selectedCount} nodes)
          </button>
          <button
            class={buttonClass}
            style:background-color={colors.BUTTON_BG}
            style:color={colors.BUTTON_TEXT}
            onclick={() => (step = "config")}
          >
            Back
          </button>
        </div>
      {/if}
    </div>
  {/if}
</DialogWrapper>
