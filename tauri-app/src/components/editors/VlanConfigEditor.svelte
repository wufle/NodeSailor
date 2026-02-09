<script lang="ts">
  import DialogWrapper from "../dialogs/DialogWrapper.svelte";
  import { currentTheme, activeDialog } from "../../lib/stores/uiStore";
  import {
    vlanLabels,
    vlanLabelOrder,
    nodes,
    updateNode,
  } from "../../lib/stores/networkStore";
  import { getThemeColors } from "../../lib/theme/colors";

  let colors = $derived(getThemeColors($currentTheme));

  function close() {
    activeDialog.set(null);
  }

  function handleLabelChange(key: string, newLabel: string) {
    vlanLabels.update((labels) => ({
      ...labels,
      [key]: newLabel,
    }));
  }

  function addVlan() {
    const existingKeys = Object.keys($vlanLabels);
    // Find the next VLAN number
    let num = 1;
    while (existingKeys.includes(`VLAN_${num}`)) num++;
    const key = `VLAN_${num}`;

    vlanLabels.update((labels) => ({ ...labels, [key]: key }));
    vlanLabelOrder.update((order) => [...order, key]);

    // Add empty VLAN to all nodes
    const allNodes = $nodes;
    allNodes.forEach((node, i) => {
      if (!(key in node.vlans)) {
        updateNode(i, {
          vlans: { ...node.vlans, [key]: "" },
        });
      }
    });
  }

  function removeVlan(key: string) {
    vlanLabels.update((labels) => {
      const copy = { ...labels };
      delete copy[key];
      return copy;
    });
    vlanLabelOrder.update((order) =>
      order.filter((k) => k !== key)
    );
  }

  function moveVlan(key: string, direction: "up" | "down") {
    vlanLabelOrder.update((order) => {
      const idx = order.indexOf(key);
      if (idx < 0) return order;
      const newOrder = [...order];
      const targetIdx =
        direction === "up" ? idx - 1 : idx + 1;
      if (targetIdx < 0 || targetIdx >= newOrder.length)
        return order;
      [newOrder[idx], newOrder[targetIdx]] = [
        newOrder[targetIdx],
        newOrder[idx],
      ];
      return newOrder;
    });
  }

  let inputClass =
    "w-full px-2 py-1 text-xs rounded border outline-none";
</script>

<DialogWrapper
  title="VLAN Configuration"
  width={400}
  onClose={close}
>
  <div class="space-y-2">
    {#each $vlanLabelOrder as key, i}
      <div class="flex items-center gap-2">
        <span
          class="text-xs opacity-60 w-20 shrink-0"
          style:color={colors.INFO_TEXT}>{key}:</span
        >
        <input
          type="text"
          value={$vlanLabels[key] ?? key}
          class={inputClass}
          style:background-color={colors.ENTRY_FOCUS_BG}
          style:color={colors.ENTRY_TEXT}
          style:border-color={colors.CELL_BORDER}
          onchange={(e) =>
            handleLabelChange(
              key,
              (e.target as HTMLInputElement).value
            )}
        />
        <button
          class="text-xs px-1 hover:opacity-70"
          style:color={colors.BUTTON_TEXT}
          onclick={() => moveVlan(key, "up")}
          disabled={i === 0}
        >
          &#9650;
        </button>
        <button
          class="text-xs px-1 hover:opacity-70"
          style:color={colors.BUTTON_TEXT}
          onclick={() => moveVlan(key, "down")}
          disabled={i === $vlanLabelOrder.length - 1}
        >
          &#9660;
        </button>
        <button
          class="text-xs text-red-500 hover:text-red-400 px-1"
          onclick={() => removeVlan(key)}
        >
          X
        </button>
      </div>
    {/each}
  </div>

  <div class="mt-4">
    <button
      class="px-3 py-1.5 text-xs rounded"
      style:background-color={colors.BUTTON_BG}
      style:color={colors.BUTTON_TEXT}
      onclick={addVlan}
    >
      Add VLAN
    </button>
  </div>
</DialogWrapper>
