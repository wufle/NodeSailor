<script lang="ts">
  import DialogWrapper from "./DialogWrapper.svelte";
  import { currentTheme, activeDialog } from "../../lib/stores/uiStore";
  import {
    connections,
    addConnection,
    updateConnection,
  } from "../../lib/stores/networkStore";
  import { effectiveColors } from "../../lib/theme/colors";

  let colors = $derived($effectiveColors);
  let isIronclad = $derived($currentTheme === "ironclad");

  let editIndex: number | null =
    (window as any).__editConnectionIndex ?? null;
  let fromIndex: number =
    (window as any).__connectionFromIndex ?? 0;
  let toIndex: number =
    (window as any).__connectionToIndex ?? 0;

  let existingConn = $derived(
    editIndex !== null ? $connections[editIndex] : null
  );

  let label = $state(existingConn?.label ?? "");
  let info = $state(existingConn?.connectioninfo ?? "");

  function save() {
    if (editIndex !== null) {
      updateConnection(editIndex, {
        label,
        connectioninfo: info || undefined,
      });
    } else {
      addConnection({
        from: fromIndex,
        to: toIndex,
        label,
        connectioninfo: info || undefined,
        label_pos: 0.5,
      });
    }
    close();
  }

  function close() {
    (window as any).__editConnectionIndex = null;
    (window as any).__connectionFromIndex = null;
    (window as any).__connectionToIndex = null;
    activeDialog.set(null);
  }

  let inputClass =
    "w-full px-2 py-1 text-sm rounded border outline-none";
</script>

<DialogWrapper
  title="Connection Details"
  width={400}
  onClose={close}
>
  <div class="space-y-3">
    <div>
      <label
        class="block text-xs mb-1"
        style:color={colors.BUTTON_TEXT}>Label:</label
      >
      <input
        type="text"
        bind:value={label}
        class={inputClass}
        style:background-color={colors.ENTRY_FOCUS_BG}
        style:color={colors.ENTRY_TEXT}
        style:border-color={colors.CELL_BORDER}
      />
    </div>

    <div>
      <label
        class="block text-xs mb-1"
        style:color={colors.BUTTON_TEXT}>Info (on hover):</label
      >
      <input
        type="text"
        bind:value={info}
        class={inputClass}
        style:background-color={colors.ENTRY_FOCUS_BG}
        style:color={colors.ENTRY_TEXT}
        style:border-color={colors.CELL_BORDER}
      />
    </div>

    <button
      class="w-full py-2 text-sm rounded {isIronclad ? 'ironclad-btn' : ''}"
      style:background-color={isIronclad ? undefined : colors.BUTTON_BG}
      style:color={colors.BUTTON_TEXT}
      onclick={save}
    >
      OK
    </button>
  </div>
</DialogWrapper>
