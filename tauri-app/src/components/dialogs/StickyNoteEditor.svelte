<script lang="ts">
  import DialogWrapper from "./DialogWrapper.svelte";
  import { currentTheme, activeDialog } from "../../lib/stores/uiStore";
  import { addStickyNote } from "../../lib/stores/networkStore";
  import { effectiveColors } from "../../lib/theme/colors";

  let colors = $derived($effectiveColors);
  let isIronclad = $derived($currentTheme === "ironclad");
  let text = $state("");

  let position: { x: number; y: number } =
    (window as any).__stickyNotePosition ?? { x: 50, y: 50 };

  function save() {
    if (text.trim()) {
      addStickyNote({ text: text.trim(), x: position.x, y: position.y });
    }
    close();
  }

  function close() {
    (window as any).__stickyNotePosition = null;
    activeDialog.set(null);
  }
</script>

<DialogWrapper title="Sticky Note" width={320} onClose={close}>
  <div class="space-y-3">
    <label
      class="block text-xs"
      style:color={colors.BUTTON_TEXT}
    >
      Enter note text:
    </label>
    <input
      type="text"
      bind:value={text}
      class="w-full px-2 py-1 text-sm rounded border outline-none"
      style:background-color={colors.ENTRY_FOCUS_BG}
      style:color={colors.ENTRY_TEXT}
      style:border-color={colors.CELL_BORDER}
    />
    <div class="flex gap-2 justify-center">
      <button
        class="px-4 py-1.5 text-sm rounded {isIronclad ? 'ironclad-btn' : ''}"
        style:background-color={isIronclad ? undefined : colors.BUTTON_BG}
        style:color={colors.BUTTON_TEXT}
        onclick={save}
      >
        OK
      </button>
      <button
        class="px-4 py-1.5 text-sm rounded {isIronclad ? 'ironclad-btn' : ''}"
        style:background-color={isIronclad ? undefined : colors.BUTTON_BG}
        style:color={colors.BUTTON_TEXT}
        onclick={close}
      >
        Cancel
      </button>
    </div>
  </div>
</DialogWrapper>
