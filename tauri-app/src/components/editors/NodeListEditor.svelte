<script lang="ts">
  import DialogWrapper from "../dialogs/DialogWrapper.svelte";
  import { currentTheme, activeDialog } from "../../lib/stores/uiStore";
  import {
    nodes,
    updateNode,
    removeNode,
    addNode,
    vlanLabels,
    vlanLabelOrder,
  } from "../../lib/stores/networkStore";
  import { effectiveColors } from "../../lib/theme/colors";

  let colors = $derived($effectiveColors);
  let isIronclad = $derived($currentTheme === "ironclad");

  let sortColumn = $state<string | null>(null);
  let sortDirection = $state<'asc' | 'desc'>('asc');

  let sortedNodesWithIndex = $derived.by(() => {
    const nodesWithIndex = $nodes.map((node, index) => ({ node, index }));

    if (!sortColumn) return nodesWithIndex;

    const sorted = [...nodesWithIndex];
    sorted.sort((a, b) => {
      const nodeA = a.node;
      const nodeB = b.node;
      let aVal: any;
      let bVal: any;

      if (sortColumn === 'name') {
        aVal = nodeA.name.toLowerCase();
        bVal = nodeB.name.toLowerCase();
      } else if (sortColumn === 'x') {
        aVal = nodeA.x;
        bVal = nodeB.x;
      } else if (sortColumn === 'y') {
        aVal = nodeA.y;
        bVal = nodeB.y;
      } else if (sortColumn.startsWith('VLAN_')) {
        aVal = (nodeA.vlans[sortColumn] || '').toLowerCase();
        bVal = (nodeB.vlans[sortColumn] || '').toLowerCase();
      } else if (sortColumn === 'rdp') {
        aVal = nodeA.remote_desktop_address.toLowerCase();
        bVal = nodeB.remote_desktop_address.toLowerCase();
      } else if (sortColumn === 'file') {
        aVal = nodeA.file_path.toLowerCase();
        bVal = nodeB.file_path.toLowerCase();
      } else if (sortColumn === 'web') {
        aVal = nodeA.web_config_url.toLowerCase();
        bVal = nodeB.web_config_url.toLowerCase();
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

  function handleAddNode() {
    addNode({
      name: "New Node",
      x: 400,
      y: 300,
      vlans: Object.fromEntries(
        $vlanLabelOrder.map((k) => [k, ""])
      ),
      remote_desktop_address: "",
      file_path: "",
      web_config_url: "",
    });
  }

  function handleDelete(index: number) {
    removeNode(index);
  }

  function handleFieldChange(
    index: number,
    field: string,
    value: string
  ) {
    const node = $nodes[index];
    if (!node) return;

    if (field === "name") {
      updateNode(index, { name: value });
    } else if (field === "x") {
      updateNode(index, { x: parseFloat(value) || 0 });
    } else if (field === "y") {
      updateNode(index, { y: parseFloat(value) || 0 });
    } else if (field === "rdp") {
      updateNode(index, { remote_desktop_address: value });
    } else if (field === "file") {
      updateNode(index, { file_path: value });
    } else if (field === "web") {
      updateNode(index, { web_config_url: value });
    } else if (field.startsWith("VLAN_")) {
      const newVlans = { ...node.vlans, [field]: value };
      updateNode(index, { vlans: newVlans });
    }
  }

  let inputClass = "w-full px-1 py-0.5 text-xs border outline-none";
</script>

<DialogWrapper title="Node List Editor" width={900} onClose={close}>
  <div class="overflow-auto max-h-[60vh]">
    <table class="w-full text-xs border-collapse">
      <thead>
        <tr>
          <th
            class="sticky top-0 px-2 py-1 text-left cursor-pointer hover:opacity-80"
            style:background-color={colors.HEADER_BG}
            style:color={colors.HEADER_TEXT}
            onclick={() => handleSort('name')}
          >Name{getSortIndicator('name')}</th>
          <th
            class="sticky top-0 px-2 py-1 text-left cursor-pointer hover:opacity-80"
            style:background-color={colors.HEADER_BG}
            style:color={colors.HEADER_TEXT}
            onclick={() => handleSort('x')}
          >X{getSortIndicator('x')}</th>
          <th
            class="sticky top-0 px-2 py-1 text-left cursor-pointer hover:opacity-80"
            style:background-color={colors.HEADER_BG}
            style:color={colors.HEADER_TEXT}
            onclick={() => handleSort('y')}
          >Y{getSortIndicator('y')}</th>
          {#each $vlanLabelOrder as vk}
            <th
              class="sticky top-0 px-2 py-1 text-left cursor-pointer hover:opacity-80"
              style:background-color={colors.HEADER_BG}
              style:color={colors.HEADER_TEXT}
              onclick={() => handleSort(vk)}
            >{$vlanLabels[vk] ?? vk}{getSortIndicator(vk)}</th>
          {/each}
          <th
            class="sticky top-0 px-2 py-1 text-left cursor-pointer hover:opacity-80"
            style:background-color={colors.HEADER_BG}
            style:color={colors.HEADER_TEXT}
            onclick={() => handleSort('rdp')}
          >RDP{getSortIndicator('rdp')}</th>
          <th
            class="sticky top-0 px-2 py-1 text-left cursor-pointer hover:opacity-80"
            style:background-color={colors.HEADER_BG}
            style:color={colors.HEADER_TEXT}
            onclick={() => handleSort('file')}
          >File{getSortIndicator('file')}</th>
          <th
            class="sticky top-0 px-2 py-1 text-left cursor-pointer hover:opacity-80"
            style:background-color={colors.HEADER_BG}
            style:color={colors.HEADER_TEXT}
            onclick={() => handleSort('web')}
          >Web{getSortIndicator('web')}</th>
          <th
            class="sticky top-0 px-2 py-1"
            style:background-color={colors.HEADER_BG}
            style:color={colors.HEADER_TEXT}
          ></th>
        </tr>
      </thead>
      <tbody>
        {#each sortedNodesWithIndex as { node, index }, displayIndex}
          <tr
            style:background-color={displayIndex % 2 === 0
              ? colors.ROW_BG_EVEN
              : colors.ROW_BG_ODD}
          >
            <td class="px-1 py-0.5"
              style:border="1px solid {colors.CELL_BORDER}"
            >
              <input
                type="text"
                value={node.name}
                class={inputClass}
                style:background-color={colors.ENTRY_FOCUS_BG}
                style:color={colors.ENTRY_TEXT}
                style:border-color={colors.CELL_BORDER}
                onchange={(e) =>
                  handleFieldChange(index, "name", (e.target as HTMLInputElement).value)}
              />
            </td>
            <td class="px-1 py-0.5" style:border="1px solid {colors.CELL_BORDER}">
              <input
                type="text"
                value={Math.round(node.x)}
                class="{inputClass} w-16"
                style:background-color={colors.ENTRY_FOCUS_BG}
                style:color={colors.ENTRY_TEXT}
                style:border-color={colors.CELL_BORDER}
                onchange={(e) =>
                  handleFieldChange(index, "x", (e.target as HTMLInputElement).value)}
              />
            </td>
            <td class="px-1 py-0.5" style:border="1px solid {colors.CELL_BORDER}">
              <input
                type="text"
                value={Math.round(node.y)}
                class="{inputClass} w-16"
                style:background-color={colors.ENTRY_FOCUS_BG}
                style:color={colors.ENTRY_TEXT}
                style:border-color={colors.CELL_BORDER}
                onchange={(e) =>
                  handleFieldChange(index, "y", (e.target as HTMLInputElement).value)}
              />
            </td>
            {#each $vlanLabelOrder as vk}
              <td class="px-1 py-0.5" style:border="1px solid {colors.CELL_BORDER}">
                <input
                  type="text"
                  value={node.vlans[vk] ?? ""}
                  class={inputClass}
                  style:background-color={colors.ENTRY_FOCUS_BG}
                  style:color={colors.ENTRY_TEXT}
                  style:border-color={colors.CELL_BORDER}
                  onchange={(e) =>
                    handleFieldChange(index, vk, (e.target as HTMLInputElement).value)}
                />
              </td>
            {/each}
            <td class="px-1 py-0.5" style:border="1px solid {colors.CELL_BORDER}">
              <input
                type="text"
                value={node.remote_desktop_address}
                class={inputClass}
                style:background-color={colors.ENTRY_FOCUS_BG}
                style:color={colors.ENTRY_TEXT}
                style:border-color={colors.CELL_BORDER}
                onchange={(e) =>
                  handleFieldChange(index, "rdp", (e.target as HTMLInputElement).value)}
              />
            </td>
            <td class="px-1 py-0.5" style:border="1px solid {colors.CELL_BORDER}">
              <input
                type="text"
                value={node.file_path}
                class={inputClass}
                style:background-color={colors.ENTRY_FOCUS_BG}
                style:color={colors.ENTRY_TEXT}
                style:border-color={colors.CELL_BORDER}
                onchange={(e) =>
                  handleFieldChange(index, "file", (e.target as HTMLInputElement).value)}
              />
            </td>
            <td class="px-1 py-0.5" style:border="1px solid {colors.CELL_BORDER}">
              <input
                type="text"
                value={node.web_config_url}
                class={inputClass}
                style:background-color={colors.ENTRY_FOCUS_BG}
                style:color={colors.ENTRY_TEXT}
                style:border-color={colors.CELL_BORDER}
                onchange={(e) =>
                  handleFieldChange(index, "web", (e.target as HTMLInputElement).value)}
              />
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

  <div class="mt-3">
    <button
      class="px-3 py-1.5 text-xs rounded {isIronclad ? 'ironclad-btn' : ''}"
      style:background-color={isIronclad ? undefined : colors.BUTTON_BG}
      style:color={colors.BUTTON_TEXT}
      onclick={handleAddNode}
    >
      Add Node
    </button>
  </div>
</DialogWrapper>
