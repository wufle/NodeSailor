<script lang="ts">
  import DialogWrapper from "./DialogWrapper.svelte";
  import {
    isDark,
    activeDialog,
    mode,
    selectedNodeIndex,
  } from "../../lib/stores/uiStore";
  import {
    nodes,
    addNode,
    updateNode,
    vlanLabels,
    vlanLabelOrder,
    displayOptions,
  } from "../../lib/stores/networkStore";
  import { getThemeColors } from "../../lib/theme/colors";

  let colors = $derived(getThemeColors($isDark));

  let editIndex: number | null =
    (window as any).__editNodeIndex ?? null;
  let position: { x: number; y: number } | null =
    (window as any).__newNodePosition ?? null;

  let existingNode = $derived(
    editIndex !== null ? $nodes[editIndex] : null
  );

  let name = $state(existingNode?.name ?? "");
  let remoteDesktop = $state(
    existingNode?.remote_desktop_address ?? ""
  );
  let filePath = $state(existingNode?.file_path ?? "");
  let webUrl = $state(existingNode?.web_config_url ?? "");

  // VLAN entries
  let vlanValues = $state<Record<string, string>>({});

  // Initialize VLAN values
  import { onMount } from "svelte";
  onMount(() => {
    const vals: Record<string, string> = {};
    for (const key of $vlanLabelOrder) {
      vals[key] = existingNode?.vlans[key] ?? "";
    }
    vlanValues = vals;
  });

  let saveMessage = $state("");

  function save() {
    if ($mode !== "Configuration") {
      saveMessage = "Switch to Configuration mode to save.";
      return;
    }

    if (editIndex !== null) {
      updateNode(editIndex, {
        name,
        vlans: { ...vlanValues },
        remote_desktop_address: remoteDesktop,
        file_path: filePath,
        web_config_url: webUrl,
      });
      selectedNodeIndex.set(editIndex);
    } else if (name && position) {
      addNode({
        name,
        x: position.x,
        y: position.y,
        vlans: { ...vlanValues },
        remote_desktop_address: remoteDesktop,
        file_path: filePath,
        web_config_url: webUrl,
      });
      selectedNodeIndex.set($nodes.length - 1);
    }

    activeDialog.set(null);
  }

  function close() {
    (window as any).__editNodeIndex = null;
    (window as any).__newNodePosition = null;
    activeDialog.set(null);
  }

  let inputClass =
    "w-full px-2 py-1 text-sm rounded border outline-none";
</script>

<DialogWrapper
  title={editIndex !== null ? "Edit Node" : "Create Node"}
  width={400}
  onClose={close}
>
  <div class="space-y-3">
    <div>
      <label
        class="block text-xs mb-1"
        style:color={colors.BUTTON_TEXT}
      >
        Node Name:
      </label>
      <input
        type="text"
        bind:value={name}
        class={inputClass}
        style:background-color={colors.ENTRY_FOCUS_BG}
        style:color={colors.ENTRY_TEXT}
        style:border-color={colors.CELL_BORDER}
      />
    </div>

    {#each $vlanLabelOrder as vlanKey}
      <div>
        <label
          class="block text-xs mb-1"
          style:color={colors.BUTTON_TEXT}
        >
          {$vlanLabels[vlanKey] ?? vlanKey}:
        </label>
        <input
          type="text"
          bind:value={vlanValues[vlanKey]}
          class={inputClass}
          style:background-color={colors.ENTRY_FOCUS_BG}
          style:color={colors.ENTRY_TEXT}
          style:border-color={colors.CELL_BORDER}
        />
      </div>
    {/each}

    <div>
      <label
        class="block text-xs mb-1"
        style:color={colors.BUTTON_TEXT}
      >
        Remote Desktop Address:
      </label>
      <input
        type="text"
        bind:value={remoteDesktop}
        class={inputClass}
        style:background-color={colors.ENTRY_FOCUS_BG}
        style:color={colors.ENTRY_TEXT}
        style:border-color={colors.CELL_BORDER}
      />
    </div>

    <div>
      <label
        class="block text-xs mb-1"
        style:color={colors.BUTTON_TEXT}
      >
        File Path:
      </label>
      <input
        type="text"
        bind:value={filePath}
        class={inputClass}
        style:background-color={colors.ENTRY_FOCUS_BG}
        style:color={colors.ENTRY_TEXT}
        style:border-color={colors.CELL_BORDER}
      />
    </div>

    <div>
      <label
        class="block text-xs mb-1"
        style:color={colors.BUTTON_TEXT}
      >
        Web Config URL:
      </label>
      <input
        type="text"
        bind:value={webUrl}
        class={inputClass}
        style:background-color={colors.ENTRY_FOCUS_BG}
        style:color={colors.ENTRY_TEXT}
        style:border-color={colors.CELL_BORDER}
      />
    </div>

    {#if saveMessage}
      <p class="text-xs text-orange-400">{saveMessage}</p>
    {/if}

    <button
      class="w-full py-2 text-sm rounded"
      style:background-color={colors.BUTTON_BG}
      style:color={colors.BUTTON_TEXT}
      onclick={save}
    >
      Save
    </button>
  </div>
</DialogWrapper>
