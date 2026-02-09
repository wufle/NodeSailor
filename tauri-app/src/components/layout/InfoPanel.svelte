<script lang="ts">
  import {
    selectedNodeIndex,
    isDark,
  } from "../../lib/stores/uiStore";
  import {
    nodes,
    vlanLabels,
    vlanLabelOrder,
    pingResults,
  } from "../../lib/stores/networkStore";
  import { getThemeColors } from "../../lib/theme/colors";
  import { getPopulatedVlans } from "../../lib/utils/vlanUtils";

  let colors = $derived(getThemeColors($isDark));

  let selectedNode = $derived(
    $selectedNodeIndex !== null ? $nodes[$selectedNodeIndex] : null
  );

  let vlans = $derived(
    selectedNode
      ? getPopulatedVlans(selectedNode, $vlanLabelOrder)
      : []
  );

  let nodeResults = $derived(
    $selectedNodeIndex !== null
      ? $pingResults[$selectedNodeIndex]
      : undefined
  );

  // Map VLAN index to ping result
  function getVlanColor(vlanIdx: number): string | null {
    if (!nodeResults || vlanIdx >= nodeResults.length) return null;
    return nodeResults[vlanIdx]
      ? colors.NODE_PING_SUCCESS
      : colors.NODE_PING_FAILURE;
  }
</script>

{#if selectedNode}
  <div
    class="absolute top-2 right-2 p-3 rounded shadow-lg min-w-[180px]"
    style:background-color={colors.INFO_NOTE_BG}
    style:color={colors.INFO_TEXT}
    style:border="1px solid {colors.BORDER_COLOR}"
  >
    <div class="text-sm font-medium mb-2">
      <span class="opacity-60">Name:</span>
      <span class="ml-2">{selectedNode.name}</span>
    </div>

    {#each vlans as vlan, i}
      <div class="text-sm flex items-center gap-2 py-0.5">
        <span class="opacity-60">
          {$vlanLabels[vlan.key] ?? vlan.key}:
        </span>
        <span
          class="px-1 rounded"
          style:background-color={getVlanColor(i) ?? "transparent"}
          style:color={getVlanColor(i) ? "#fff" : colors.INFO_TEXT}
        >
          {vlan.value}
        </span>
      </div>
    {/each}
  </div>
{/if}
