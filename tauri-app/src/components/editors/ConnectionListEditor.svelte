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

  let sortColumn = $state<string | null>(null);
  let sortDirection = $state<'asc' | 'desc'>('asc');

  let sortedConnectionsWithIndex = $derived.by(() => {
    const connsWithIndex = $connections.map((conn, index) => ({ conn, index }));

    if (!sortColumn) return connsWithIndex;

    const sorted = [...connsWithIndex];
    sorted.sort((a, b) => {
      const connA = a.conn;
      const connB = b.conn;
      let aVal: any;
      let bVal: any;

      if (sortColumn === 'from') {
        aVal = ($nodes[connA.from]?.name || '').toLowerCase();
        bVal = ($nodes[connB.from]?.name || '').toLowerCase();
      } else if (sortColumn === 'to') {
        aVal = ($nodes[connA.to]?.name || '').toLowerCase();
        bVal = ($nodes[connB.to]?.name || '').toLowerCase();
      } else if (sortColumn === 'label') {
        aVal = (connA.label || '').toLowerCase();
        bVal = (connB.label || '').toLowerCase();
      } else if (sortColumn === 'info') {
        aVal = (connA.connectioninfo || '').toLowerCase();
        bVal = (connB.connectioninfo || '').toLowerCase();
      } else if (sortColumn === 'waypoints') {
        aVal = connA.waypoints?.length || 0;
        bVal = connB.waypoints?.length || 0;
      } else {
        return 0;
      }

      if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });

    return sorted;
  });

  function handleSort(column: string) {
    if (sortColumn === column) {
      sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      sortColumn = column;
      sortDirection = 'asc';
    }
  }

  function getSortIndicator(column: string): string {
    if (sortColumn !== column) return '';
    return sortDirection === 'asc' ? ' ▲' : ' ▼';
  }

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
            class="sticky top-0 px-2 py-1 text-left cursor-pointer hover:opacity-80"
            style:background-color={colors.HEADER_BG}
            style:color={colors.HEADER_TEXT}
            onclick={() => handleSort('from')}
          >From{getSortIndicator('from')}</th>
          <th
            class="sticky top-0 px-2 py-1 text-left cursor-pointer hover:opacity-80"
            style:background-color={colors.HEADER_BG}
            style:color={colors.HEADER_TEXT}
            onclick={() => handleSort('to')}
          >To{getSortIndicator('to')}</th>
          <th
            class="sticky top-0 px-2 py-1 text-left cursor-pointer hover:opacity-80"
            style:background-color={colors.HEADER_BG}
            style:color={colors.HEADER_TEXT}
            onclick={() => handleSort('label')}
          >Label{getSortIndicator('label')}</th>
          <th
            class="sticky top-0 px-2 py-1 text-left cursor-pointer hover:opacity-80"
            style:background-color={colors.HEADER_BG}
            style:color={colors.HEADER_TEXT}
            onclick={() => handleSort('info')}
          >Info{getSortIndicator('info')}</th>
          <th
            class="sticky top-0 px-2 py-1 text-left cursor-pointer hover:opacity-80"
            style:background-color={colors.HEADER_BG}
            style:color={colors.HEADER_TEXT}
            onclick={() => handleSort('waypoints')}
          >Waypoints{getSortIndicator('waypoints')}</th>
          <th
            class="sticky top-0 px-2 py-1"
            style:background-color={colors.HEADER_BG}
            style:color={colors.HEADER_TEXT}
          ></th>
        </tr>
      </thead>
      <tbody>
        {#each sortedConnectionsWithIndex as { conn, index }, displayIndex}
          <tr
            style:background-color={displayIndex % 2 === 0
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
                    index,
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
                    index,
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
                onclick={() => handleDelete(index)}
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
