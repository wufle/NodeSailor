<script lang="ts">
  import DialogWrapper from "../dialogs/DialogWrapper.svelte";
  import { isDark, activeDialog } from "../../lib/stores/uiStore";
  import { getThemeColors, lightTheme, darkTheme } from "../../lib/theme/colors";
  import type { ThemeColors } from "../../lib/theme/colors";

  let colors = $derived(getThemeColors($isDark));

  function close() {
    activeDialog.set(null);
  }

  // Color scheme editing is read-only for now - shows current colors
  let themeKeys = $derived(
    Object.keys(colors) as (keyof ThemeColors)[]
  );
</script>

<DialogWrapper
  title="Color Scheme"
  width={400}
  onClose={close}
>
  <div class="space-y-1">
    <div class="flex gap-2 mb-3">
      <button
        class="px-3 py-1.5 text-xs rounded"
        style:background-color={$isDark
          ? colors.BUTTON_ACTIVE_BG
          : colors.BUTTON_BG}
        style:color={colors.BUTTON_TEXT}
        onclick={() => isDark.set(true)}
      >
        Dark
      </button>
      <button
        class="px-3 py-1.5 text-xs rounded"
        style:background-color={!$isDark
          ? colors.BUTTON_ACTIVE_BG
          : colors.BUTTON_BG}
        style:color={colors.BUTTON_TEXT}
        onclick={() => isDark.set(false)}
      >
        Light
      </button>
    </div>

    {#each themeKeys as key}
      <div class="flex items-center gap-2 text-xs">
        <div
          class="w-5 h-5 rounded border shrink-0"
          style:background-color={colors[key]}
          style:border-color={colors.CELL_BORDER}
        ></div>
        <span style:color={colors.BUTTON_TEXT}>{key}</span>
      </div>
    {/each}
  </div>
</DialogWrapper>
