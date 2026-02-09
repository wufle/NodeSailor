<script lang="ts">
  import DialogWrapper from "../dialogs/DialogWrapper.svelte";
  import { currentTheme, activeDialog } from "../../lib/stores/uiStore";
  import {
    nodes,
    connections,
    updateConnection,
    removeConnection,
  } from "../../lib/stores/networkStore";
  import { getThemeColors } from "../../lib/theme/colors";

  let colors = $derived(getThemeColors($currentTheme));

  function close() {
    activeDialog.set(null);
  }

  function handleFieldChange(
    index: number,
    field: string,
    value: string
  ) {
    if (field === "label") {
      updateConnection(index, { label: value });
    } else if (field === "info") {
      updateConnection(index, { connectioninfo: value || undefined });
    }
  }

  function handleDelete(index: number) {
    removeConnection(index);
  }

  let inputClass = "w-full px-1 py-0.5 text-xs border outline-none";
</script>

<DialogWrapper
  title="Connections List Editor"
  width={700}
  onClose={close}
>
  <div class="overflow-auto max-h-[60vh]">
    <table class="w-full text-xs border-collapse">
      <thead>
        <tr>
          <th
            class="sticky top-0 px-2 py-1 text-left"
            style:background-color={colors.HEADER_BG}
            style:color={colors.HEADER_TEXT}
          >From</th>
          <th
            class="sticky top-0 px-2 py-1 text-left"
            style:background-color={colors.HEADER_BG}
            style:color={colors.HEADER_TEXT}
          >To</th>
          <th
            class="sticky top-0 px-2 py-1 text-left"
            style:background-color={colors.HEADER_BG}
            style:color={colors.HEADER_TEXT}
          >Label</th>
          <th
            class="sticky top-0 px-2 py-1 text-left"
            style:background-color={colors.HEADER_BG}
            style:color={colors.HEADER_TEXT}
          >Info</th>
          <th
            class="sticky top-0 px-2 py-1 text-left"
            style:background-color={colors.HEADER_BG}
            style:color={colors.HEADER_TEXT}
          >Waypoints</th>
          <th
            class="sticky top-0 px-2 py-1"
            style:background-color={colors.HEADER_BG}
            style:color={colors.HEADER_TEXT}
          ></th>
        </tr>
      </thead>
      <tbody>
        {#each $connections as conn, i}
          <tr
            style:background-color={i % 2 === 0
              ? colors.ROW_BG_EVEN
              : colors.ROW_BG_ODD}
          >
            <td class="px-2 py-0.5" style:border="1px solid {colors.CELL_BORDER}"
              style:color={colors.ENTRY_TEXT}
            >
              {$nodes[conn.from]?.name ?? `Node ${conn.from}`}
            </td>
            <td class="px-2 py-0.5" style:border="1px solid {colors.CELL_BORDER}"
              style:color={colors.ENTRY_TEXT}
            >
              {$nodes[conn.to]?.name ?? `Node ${conn.to}`}
            </td>
            <td class="px-1 py-0.5" style:border="1px solid {colors.CELL_BORDER}">
              <input
                type="text"
                value={conn.label}
                class={inputClass}
                style:background-color={colors.ENTRY_FOCUS_BG}
                style:color={colors.ENTRY_TEXT}
                style:border-color={colors.CELL_BORDER}
                onchange={(e) =>
                  handleFieldChange(
                    i,
                    "label",
                    (e.target as HTMLInputElement).value
                  )}
              />
            </td>
            <td class="px-1 py-0.5" style:border="1px solid {colors.CELL_BORDER}">
              <input
                type="text"
                value={conn.connectioninfo ?? ""}
                class={inputClass}
                style:background-color={colors.ENTRY_FOCUS_BG}
                style:color={colors.ENTRY_TEXT}
                style:border-color={colors.CELL_BORDER}
                onchange={(e) =>
                  handleFieldChange(
                    i,
                    "info",
                    (e.target as HTMLInputElement).value
                  )}
              />
            </td>
            <td class="px-2 py-0.5 text-center" style:border="1px solid {colors.CELL_BORDER}"
              style:color={colors.ENTRY_TEXT}
            >
              {conn.waypoints?.length ?? 0}
            </td>
            <td class="px-1 py-0.5 text-center" style:border="1px solid {colors.CELL_BORDER}">
              <button
                class="text-red-500 hover:text-red-400 text-xs"
                onclick={() => handleDelete(i)}
              >
                Del
              </button>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</DialogWrapper>
