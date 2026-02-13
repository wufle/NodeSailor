<script lang="ts">
  import DialogWrapper from "./DialogWrapper.svelte";
  import { currentTheme, activeDialog } from "../../lib/stores/uiStore";
  import type { ThemeName } from "../../lib/stores/uiStore";
  import { getThemeColors } from "../../lib/theme/colors";
  import type { ThemeColors } from "../../lib/theme/colors";
  import { settings } from "../../lib/stores/settingsStore";
  import { invoke } from "@tauri-apps/api/core";

  const themeOptions: { name: ThemeName; label: string }[] = [
    { name: "light", label: "Light" },
    { name: "dark", label: "Dark" },
    { name: "ironclad", label: "Ironclad" },
  ];

  let colors = $derived(getThemeColors($currentTheme));
  let isIronclad = $derived($currentTheme === "ironclad");
  let themeKeys = $derived(Object.keys(colors) as (keyof ThemeColors)[]);

  function close() {
    activeDialog.set(null);
  }

  async function toggleStrobeEffects() {
    const newValue = !$settings.disable_strobe_effects;
    await invoke("save_settings", {
      settings: { ...$settings, disable_strobe_effects: newValue },
    });
    settings.update((s) => ({ ...s, disable_strobe_effects: newValue }));
  }
</script>

<DialogWrapper title="Display Options" width={400} onClose={close}>
  <div class="space-y-4">
    <!-- Theme Selector -->
    <div>
      <div class="text-xs font-medium mb-2" style:color={colors.BUTTON_TEXT}>
        Color Scheme
      </div>
      <div class="flex gap-2">
        {#each themeOptions as opt}
          <button
            class="px-3 py-1.5 text-xs rounded flex-1 {isIronclad ? 'ironclad-btn' : ''}"
            style:background-color={isIronclad ? undefined : ($currentTheme === opt.name
              ? colors.BUTTON_ACTIVE_BG
              : colors.BUTTON_BG)}
            style:color={$currentTheme === opt.name
              ? colors.BUTTON_ACTIVE_TEXT
              : colors.BUTTON_TEXT}
            style:border-color={$currentTheme === opt.name && isIronclad ? "#e09240" : undefined}
            onclick={() => currentTheme.set(opt.name)}
          >
            {opt.label}
          </button>
        {/each}
      </div>
    </div>

    <!-- Strobe Effects Toggle -->
    <div>
      <label
        class="flex items-center gap-2 text-xs cursor-pointer"
        style:color={colors.BUTTON_TEXT}
      >
        <input
          type="checkbox"
          checked={$settings.disable_strobe_effects ?? false}
          onchange={toggleStrobeEffects}
          class="cursor-pointer"
        />
        <span>Disable strobe effects</span>
      </label>
      <div class="text-xs mt-1 opacity-50" style:color={colors.BUTTON_TEXT}>
        Turns off glow animations on ping and host detection
      </div>
    </div>

    <!-- Color Preview -->
    <div>
      <div class="text-xs font-medium mb-2" style:color={colors.BUTTON_TEXT}>
        Current Theme Colors
      </div>
      <div class="space-y-1">
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
    </div>
  </div>
</DialogWrapper>
