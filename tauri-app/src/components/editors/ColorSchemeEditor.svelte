<script lang="ts">
  import DialogWrapper from "../dialogs/DialogWrapper.svelte";
  import { currentTheme, activeDialog } from "../../lib/stores/uiStore";
  import type { ThemeName } from "../../lib/stores/uiStore";
  import { getThemeColors, lightTheme, darkTheme } from "../../lib/theme/colors";
  import type { ThemeColors } from "../../lib/theme/colors";

  const themeOptions: { name: ThemeName; label: string }[] = [
    { name: "light", label: "Light" },
    { name: "dark", label: "Dark" },
    { name: "ironclad", label: "Ironclad" },
  ];

  let colors = $derived(getThemeColors($currentTheme));
  let isIronclad = $derived($currentTheme === "ironclad");

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
      {#each themeOptions as opt}
        <button
          class="px-3 py-1.5 text-xs rounded {isIronclad ? 'ironclad-btn' : ''}"
          style:background-color={isIronclad ? undefined : ($currentTheme === opt.name
            ? colors.BUTTON_ACTIVE_BG
            : colors.BUTTON_BG)}
          style:color={colors.BUTTON_TEXT}
          style:border-color={$currentTheme === opt.name && isIronclad ? "#e09240" : undefined}
          onclick={() => currentTheme.set(opt.name)}
        >
          {opt.label}
        </button>
      {/each}
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
