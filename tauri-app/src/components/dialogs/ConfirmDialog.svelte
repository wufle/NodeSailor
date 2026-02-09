<script lang="ts">
  import DialogWrapper from "./DialogWrapper.svelte";
  import { currentTheme, activeDialog } from "../../lib/stores/uiStore";
  import { getThemeColors } from "../../lib/theme/colors";

  let colors = $derived(getThemeColors($currentTheme));
  let isIronclad = $derived($currentTheme === "ironclad");

  let message: string =
    (window as any).__confirmMessage ?? "Are you sure?";
  let onYes: (() => void) | undefined =
    (window as any).__confirmOnYes;
  let onNo: (() => void) | undefined =
    (window as any).__confirmOnNo;

  function close() {
    (window as any).__confirmMessage = null;
    (window as any).__confirmOnYes = null;
    (window as any).__confirmOnNo = null;
    activeDialog.set(null);
  }

  function handleYes() {
    onYes?.();
    close();
  }

  function handleNo() {
    onNo?.();
    close();
  }
</script>

<DialogWrapper title="" width={300} onClose={close}>
  <div class="text-center">
    <p class="text-sm mb-4" style:color={colors.BUTTON_TEXT}>
      {message}
    </p>
    <div class="flex justify-center gap-3">
      <button
        class="px-4 py-1.5 text-sm rounded {isIronclad ? 'ironclad-btn' : ''}"
        style:background-color={isIronclad ? undefined : colors.BUTTON_BG}
        style:color={colors.BUTTON_TEXT}
        onclick={handleYes}
      >
        Yes
      </button>
      <button
        class="px-4 py-1.5 text-sm rounded {isIronclad ? 'ironclad-btn' : ''}"
        style:background-color={isIronclad ? undefined : colors.BUTTON_BG}
        style:color={colors.BUTTON_TEXT}
        onclick={handleNo}
      >
        No
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
