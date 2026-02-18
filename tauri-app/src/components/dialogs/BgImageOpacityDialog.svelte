<script lang="ts">
  import DialogWrapper from "./DialogWrapper.svelte";
  import { activeDialog, currentTheme } from "../../lib/stores/uiStore";
  import { backgroundImages, updateBackgroundImage } from "../../lib/stores/networkStore";
  import { effectiveColors } from "../../lib/theme/colors";

  let colors = $derived($effectiveColors);
  let isIronclad = $derived($currentTheme === "ironclad");

  let imageIndex: number = (window as any).__bgImageOpacityIndex ?? 0;
  let currentImage = $derived($backgroundImages[imageIndex]);
  let opacity = $state(currentImage?.opacity ?? 1.0);

  function save() {
    updateBackgroundImage(imageIndex, { opacity });
    close();
  }

  function close() {
    (window as any).__bgImageOpacityIndex = undefined;
    activeDialog.set(null);
  }
</script>

<DialogWrapper title="Image Opacity" width={300} onClose={close}>
  <div class="space-y-3">
    {#if currentImage}
      <div class="text-xs truncate" style:color={colors.BUTTON_TEXT}>
        {currentImage.filename}
      </div>
    {/if}
    <label class="block text-xs" style:color={colors.BUTTON_TEXT}>
      Opacity: {Math.round(opacity * 100)}%
    </label>
    <input
      type="range"
      min="0"
      max="1"
      step="0.05"
      bind:value={opacity}
      class="w-full"
    />
    <div class="flex gap-2 justify-center pt-2">
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
