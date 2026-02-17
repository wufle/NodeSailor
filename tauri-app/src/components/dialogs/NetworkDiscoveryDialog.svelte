<script lang="ts">
  import DialogWrapper from "./DialogWrapper.svelte";
  import { activeDialog } from "../../lib/stores/uiStore";
  import { effectiveColors } from "../../lib/theme/colors";
  import { currentTheme } from "../../lib/stores/uiStore";
  import { invoke } from "@tauri-apps/api/core";
  import { listen } from "@tauri-apps/api/event";
  import {
    createNodesFromDiscovery,
    type DiscoveredDevice,
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

  let colors = $derived($effectiveColors);
  let isIronclad = $derived($currentTheme === "ironclad");

  // Wizard step
  let step = $state<"config" | "scanning" | "results">("config");

  // Config step state
  let subnets = $state<SubnetInfo[]>([]);
  let selectedSubnetIdx = $state(0);
  let scanDepth = $state<"minimal" | "basic" | "ports">("basic");
  let layout = $state<"grid" | "circle">("grid");
  let clearExisting = $state(true);
  let loadingSubnets = $state(true);
  let subnetError = $state("");

  // Scanning step state
  let progressPhase = $state("");
  let progressCurrent = $state(0);
  let progressTotal = $state(1);
  let progressFound = $state(0);
  let progressMessage = $state("Starting scan...");

  // Results step state
  let devices = $state<DiscoveredDevice[]>([]);
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

  async function startScan() {
    if (subnets.length === 0) return;

    step = "scanning";
    scanError = "";
    progressPhase = "ping_sweep";
    progressCurrent = 0;
    progressTotal = 1;
    progressFound = 0;
    progressMessage = "Starting scan...";

    const subnet = subnets[selectedSubnetIdx];

    // Listen for progress events
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
      const result = await invoke<DiscoveredDevice[]>("discover_network", {
        subnetIp: subnet.ip,
        subnetMask: subnet.subnet_mask,
        scanDepth: scanDepth,
      });

      devices = result;
      selected = result.map(() => true);
      step = "results";
    } catch (e) {
      scanError = `Scan failed: ${e}`;
      step = "config";
    } finally {
      unlisten();
    }
  }

  function handleCreateMap() {
    const selectedDevices = devices.filter((_, i) => selected[i]);
    if (selectedDevices.length === 0) return;
    createNodesFromDiscovery(selectedDevices, layout, clearExisting);
  }

  function toggleAll() {
    const allSelected = selected.every((s) => s);
    selected = selected.map(() => !allSelected);
  }

  let selectedCount = $derived(selected.filter((s) => s).length);

  let progressPercent = $derived(
    progressTotal > 0 ? Math.round((progressCurrent / progressTotal) * 100) : 0
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

  function portBadges(ports: number[]): { label: string; title: string }[] {
    const badges: { label: string; title: string }[] = [];
    if (ports.includes(80) || ports.includes(443)) badges.push({ label: "Web", title: "HTTP/HTTPS" });
    if (ports.includes(3389)) badges.push({ label: "RDP", title: "Remote Desktop" });
    if (ports.includes(22)) badges.push({ label: "SSH", title: "Secure Shell" });
    return badges;
  }
</script>

<DialogWrapper title="Network Discovery" width={620} onClose={close}>
  {#if step === "config"}
    <!-- Configuration Step -->
    <div class="space-y-4">
      <p class="text-sm opacity-70" style:color={colors.BUTTON_TEXT}>
        Scan your local network to automatically discover devices and create a topology map.
      </p>

      <!-- Subnet Selection -->
      <div>
        <label class="block text-xs font-medium mb-1" style:color={colors.BUTTON_TEXT}>
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
            No network interfaces found. Make sure you are connected to a network.
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

      <!-- Scan Depth -->
      <div>
        <label class="block text-xs font-medium mb-2" style:color={colors.BUTTON_TEXT}>
          Scan Depth
        </label>
        <div class="space-y-2">
          <label class="flex items-start gap-2 cursor-pointer" style:color={colors.BUTTON_TEXT}>
            <input type="radio" bind:group={scanDepth} value="minimal" class="mt-0.5" />
            <div>
              <span class="text-sm font-medium">Quick Scan</span>
              <p class="text-xs opacity-60">Find live devices only (fastest)</p>
            </div>
          </label>
          <label class="flex items-start gap-2 cursor-pointer" style:color={colors.BUTTON_TEXT}>
            <input type="radio" bind:group={scanDepth} value="basic" class="mt-0.5" />
            <div>
              <span class="text-sm font-medium">Standard Scan</span>
              <p class="text-xs opacity-60">Devices + hostnames + MAC addresses</p>
            </div>
          </label>
          <label class="flex items-start gap-2 cursor-pointer" style:color={colors.BUTTON_TEXT}>
            <input type="radio" bind:group={scanDepth} value="ports" class="mt-0.5" />
            <div>
              <span class="text-sm font-medium">Full Scan</span>
              <p class="text-xs opacity-60">Also detect web interfaces & remote desktop (slowest)</p>
            </div>
          </label>
        </div>
      </div>

      <!-- Layout Choice -->
      <div>
        <label class="block text-xs font-medium mb-2" style:color={colors.BUTTON_TEXT}>
          Node Layout
        </label>
        <div class="flex gap-4">
          <label class="flex items-center gap-2 cursor-pointer" style:color={colors.BUTTON_TEXT}>
            <input type="radio" bind:group={layout} value="grid" />
            <span class="text-sm">Grid</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer" style:color={colors.BUTTON_TEXT}>
            <input type="radio" bind:group={layout} value="circle" />
            <span class="text-sm">Circle</span>
          </label>
        </div>
      </div>

      <!-- Clear existing -->
      <label class="flex items-center gap-2 cursor-pointer" style:color={colors.BUTTON_TEXT}>
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
          disabled={subnets.length === 0 || loadingSubnets}
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

      <div class="flex justify-between text-xs opacity-60" style:color={colors.BUTTON_TEXT}>
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
      {#if devices.length === 0}
        <p class="text-sm text-center py-4" style:color={colors.BUTTON_TEXT}>
          No devices found on this subnet. Try a different network interface or check your connection.
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
            {selectedCount} of {devices.length} devices selected
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
          <table class="w-full text-xs" style:color={colors.BUTTON_TEXT}>
            <thead>
              <tr
                class="sticky top-0"
                style:background-color={colors.FRAME_BG}
                style:border-bottom="1px solid {colors.BORDER_COLOR}"
              >
                <th class="px-2 py-1.5 text-left w-8"></th>
                <th class="px-2 py-1.5 text-left">IP Address</th>
                <th class="px-2 py-1.5 text-left">Hostname</th>
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
        </div>

        <!-- Layout reminder -->
        <p class="text-xs opacity-50" style:color={colors.BUTTON_TEXT}>
          Layout: {layout === "grid" ? "Grid" : "Circle"}
          {clearExisting ? "(existing map will be cleared)" : "(adding to existing map)"}
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
