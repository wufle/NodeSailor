<script lang="ts">
  import { zoom, panX, panY, zoomPercent, currentTheme } from "../../lib/stores/uiStore";
  import { displayOptions, vlanLabels } from "../../lib/stores/networkStore";
  import { getThemeColors } from "../../lib/theme/colors";

  let colors = $derived(getThemeColors($currentTheme));
  let isIronclad = $derived($currentTheme === "ironclad");

  let isExpanded = $state(false);

  // Local state synced with store
  let showConnections = $state($displayOptions.show_connections !== false);
  let showConnectionLabels = $state($displayOptions.show_connection_labels !== false);
  let showNotes = $state($displayOptions.show_notes !== false);
  let showGroups = $state($displayOptions.show_groups !== false);
  let nodeSize = $state($displayOptions.node_size ?? 14);
  let visibleVlans = $state<string[] | null>($displayOptions.visible_vlans ?? null);

  // Update store when local state changes
  $effect(() => {
    displayOptions.update((opts) => ({
      ...opts,
      show_connections: showConnections,
      show_connection_labels: showConnectionLabels,
      show_notes: showNotes,
      show_groups: showGroups,
      node_size: nodeSize,
      visible_vlans: visibleVlans,
    }));
  });

  function zoomIn() {
    zoom.update((z) => z * 1.1);
  }

  function zoomOut() {
    zoom.update((z) => z * 0.9);
  }

  function resetZoom() {
    zoom.set(1);
    panX.set(0);
    panY.set(0);
  }

  function toggleVlan(vlanKey: string) {
    if (visibleVlans === null) {
      // Currently showing all, switch to showing only this one
      visibleVlans = [vlanKey];
    } else {
      const idx = visibleVlans.indexOf(vlanKey);
      if (idx === -1) {
        // Add this VLAN
        visibleVlans = [...visibleVlans, vlanKey];
      } else {
        // Remove this VLAN
        visibleVlans = visibleVlans.filter(k => k !== vlanKey);
      }
    }
  }

  function showAllVlans() {
    visibleVlans = null;
  }

  function hideAllVlans() {
    visibleVlans = [];
  }

  let vlanKeys = $derived(Object.keys($vlanLabels));
  let allVlansVisible = $derived(visibleVlans === null);
</script>

<div
  class="absolute bottom-2 left-2 rounded {isIronclad ? 'ironclad-zoom' : 'shadow'}"
  style:background-color={isIronclad ? undefined : colors.FRAME_BG}
  style:color={colors.BUTTON_TEXT}
  style:border={isIronclad ? undefined : `1px solid ${colors.BORDER_COLOR}`}
  style:max-width="300px"
>
  <!-- Header with zoom controls -->
  <div class="flex items-center gap-1 px-2 py-1">
    <button
      class="px-2 py-0.5 text-sm cursor-pointer hover:opacity-70 {isIronclad ? 'ironclad-btn rounded' : ''}"
      onclick={zoomIn}
    >
      +
    </button>
    <button
      class="px-2 py-0.5 text-sm cursor-pointer hover:opacity-70 min-w-[3rem] text-center {isIronclad ? 'ironclad-btn rounded' : ''}"
      onclick={resetZoom}
    >
      {$zoomPercent}%
    </button>
    <button
      class="px-2 py-0.5 text-sm cursor-pointer hover:opacity-70 {isIronclad ? 'ironclad-btn rounded' : ''}"
      onclick={zoomOut}
    >
      &ndash;
    </button>

    <div class="flex-1"></div>

    <button
      class="px-2 py-0.5 text-xs cursor-pointer hover:opacity-70"
      onclick={() => isExpanded = !isExpanded}
      title="Display options"
    >
      {isExpanded ? "▼" : "▲"}
    </button>
  </div>

  <!-- Collapsible options -->
  {#if isExpanded}
    <div
      class="px-3 py-2 space-y-2 border-t"
      style:border-color={colors.BORDER_COLOR}
    >
      <!-- Visibility toggles -->
      <div class="text-xs font-semibold mb-1" style:color={colors.TEXT_PRIMARY}>
        Visibility
      </div>

      <label class="flex items-center gap-2 text-xs" style:color={colors.BUTTON_TEXT}>
        <input type="checkbox" bind:checked={showConnections} />
        Connections
      </label>

      <label class="flex items-center gap-2 text-xs" style:color={colors.BUTTON_TEXT}>
        <input type="checkbox" bind:checked={showConnectionLabels} />
        Connection Labels
      </label>

      <label class="flex items-center gap-2 text-xs" style:color={colors.BUTTON_TEXT}>
        <input type="checkbox" bind:checked={showNotes} />
        Sticky Notes
      </label>

      <label class="flex items-center gap-2 text-xs" style:color={colors.BUTTON_TEXT}>
        <input type="checkbox" bind:checked={showGroups} />
        Groups
      </label>

      <!-- Node size -->
      <div class="pt-2">
        <div class="text-xs mb-1" style:color={colors.TEXT_PRIMARY}>
          Node Size: {nodeSize}
        </div>
        <input
          type="range"
          min="8"
          max="32"
          bind:value={nodeSize}
          class="w-full"
        />
      </div>

      <!-- VLAN filtering -->
      {#if vlanKeys.length > 0}
        <div class="pt-2 border-t" style:border-color={colors.BORDER_COLOR}>
          <div class="flex items-center justify-between mb-1">
            <div class="text-xs font-semibold" style:color={colors.TEXT_PRIMARY}>
              Filter by VLAN
            </div>
            <div class="flex gap-1">
              <button
                class="text-xs px-1 py-0.5 hover:opacity-70"
                style:color={colors.TEXT_SECONDARY}
                onclick={showAllVlans}
              >
                All
              </button>
              <button
                class="text-xs px-1 py-0.5 hover:opacity-70"
                style:color={colors.TEXT_SECONDARY}
                onclick={hideAllVlans}
              >
                None
              </button>
            </div>
          </div>

          <div class="space-y-1 max-h-32 overflow-y-auto">
            {#each vlanKeys as vlanKey}
              {@const label = $vlanLabels[vlanKey] || vlanKey}
              {@const isChecked = allVlansVisible || visibleVlans?.includes(vlanKey)}
              <label class="flex items-center gap-2 text-xs" style:color={colors.BUTTON_TEXT}>
                <input
                  type="checkbox"
                  checked={isChecked}
                  onchange={() => toggleVlan(vlanKey)}
                />
                {label}
              </label>
            {/each}
          </div>
        </div>
      {/if}
    </div>
  {/if}
</div>
