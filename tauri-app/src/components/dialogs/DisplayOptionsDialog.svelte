<script lang="ts">
  import DialogWrapper from "./DialogWrapper.svelte";
  import { currentTheme, activeDialog } from "../../lib/stores/uiStore";
  import type { ThemeName } from "../../lib/stores/uiStore";
  import {
    getThemeColors,
    setColorOverride,
    resetColorOverrides,
    getColorOverrides,
    registerCustomTheme,
    removeCustomTheme,
    getCustomThemeNames,
    getCustomThemes,
    isBuiltInTheme,
  } from "../../lib/theme/colors";
  import type { ThemeColors } from "../../lib/theme/colors";
  import { settings } from "../../lib/stores/settingsStore";
  import { invoke } from "@tauri-apps/api/core";

  const builtInOptions: { name: ThemeName; label: string }[] = [
    { name: "light", label: "Light" },
    { name: "dark", label: "Dark" },
  ];

  const colorLabels: Record<keyof ThemeColors, string> = {
    FRAME_BG: "Frame Background",
    BUTTON_BG: "Button Background",
    BUTTON_TEXT: "Button Text",
    BUTTON_ACTIVE_BG: "Active Button Background",
    BUTTON_ACTIVE_TEXT: "Active Button Text",
    BUTTON_CONFIGURATION_MODE: "Config Mode Accent",
    CELL_BORDER: "Cell Border",
    BORDER_COLOR: "Border",
    ENTRY_FOCUS_BG: "Input Background",
    ENTRY_TEXT: "Input Text",
    INFO_NOTE_BG: "Info Panel Background",
    INFO_TEXT: "Info Text",
    HEADER_BG: "Header Background",
    HEADER_TEXT: "Header Text",
    ROW_BG_EVEN: "Table Row Even",
    ROW_BG_ODD: "Table Row Odd",
    NODE_DEFAULT: "Node Default",
    NODE_HIGHLIGHT: "Node Highlight",
    NODE_OUTLINE_DEFAULT: "Node Outline",
    NODE_PING_SUCCESS: "Ping Success",
    NODE_PING_FAILURE: "Ping Failure",
    NODE_PING_PARTIAL_SUCCESS: "Ping Partial",
    Connections: "Connections",
    GROUP_TEXT: "Group Text",
    GROUP_OUTLINE: "Group Outline",
  };

  let colors = $derived(getThemeColors($currentTheme));
  let isIronclad = $derived($currentTheme === "ironclad");
  let themeKeys = $derived(Object.keys(colors) as (keyof ThemeColors)[]);
  let customNames = $state(getCustomThemeNames());
  let isCustomTheme = $derived(!isBuiltInTheme($currentTheme));

  let showSaveInput = $state(false);
  let newThemeName = $state("");

  async function close() {
    // Persist any unsaved color overrides on close
    await saveOverrides();
    activeDialog.set(null);
  }

  function selectTheme(name: ThemeName) {
    currentTheme.set(name);
    persistLastTheme(name);
  }

  async function toggleStrobeEffects() {
    const newValue = !$settings.disable_strobe_effects;
    await invoke("save_settings", {
      settings: { ...$settings, disable_strobe_effects: newValue },
    });
    settings.update((s) => ({ ...s, disable_strobe_effects: newValue }));
  }

  function handleColorChange(key: keyof ThemeColors, value: string) {
    setColorOverride($currentTheme, key, value);
    currentTheme.refresh();
  }

  async function handleReset() {
    resetColorOverrides($currentTheme);
    currentTheme.refresh();
    await saveOverrides();
  }

  async function saveOverrides() {
    const overrides = getColorOverrides();
    await invoke("save_settings", {
      settings: { ...$settings, custom_theme_colors: overrides },
    });
    settings.update((s) => ({ ...s, custom_theme_colors: overrides }));
  }

  function startSaveCustom() {
    newThemeName = "";
    showSaveInput = true;
  }

  async function confirmSaveCustom() {
    const name = newThemeName.trim();
    if (!name || isBuiltInTheme(name) || name === "ironclad") return;

    // Snapshot current effective colors (base + overrides) as a new custom theme
    const snapshot = { ...getThemeColors($currentTheme) };
    registerCustomTheme(name, snapshot);

    // Clear overrides for the current theme since they're baked into the custom one
    resetColorOverrides($currentTheme);

    // Persist custom themes
    await persistCustomThemes();

    // Switch to the new custom theme
    currentTheme.set(name as ThemeName);
    await persistLastTheme(name);

    customNames = getCustomThemeNames();
    showSaveInput = false;
    newThemeName = "";
  }

  async function deleteCustomTheme(name: string) {
    removeCustomTheme(name);
    customNames = getCustomThemeNames();
    await persistCustomThemes();

    // If we were on that theme, switch back to dark
    if ($currentTheme === name) {
      currentTheme.set("dark");
      await persistLastTheme("dark");
    }
  }

  async function persistCustomThemes() {
    const themes = getCustomThemes();
    await invoke("save_settings", {
      settings: { ...$settings, custom_themes: themes },
    });
    settings.update((s) => ({ ...s, custom_themes: themes as any }));
  }

  async function persistLastTheme(name: string) {
    const isCustom = !isBuiltInTheme(name) && name !== "ironclad";
    const lastCustom = isCustom ? name : undefined;
    await invoke("save_settings", {
      settings: { ...$settings, last_custom_theme: lastCustom },
    });
    settings.update((s) => ({ ...s, last_custom_theme: lastCustom }));
  }

  function handleSaveKeydown(e: KeyboardEvent) {
    if (e.key === "Enter") {
      confirmSaveCustom();
    } else if (e.key === "Escape") {
      showSaveInput = false;
    }
  }
</script>

<DialogWrapper title="Display Options" width={420} onClose={close}>
  <div class="space-y-4">
    <!-- Theme Selector -->
    <div>
      <div class="text-xs font-medium mb-2" style:color={colors.BUTTON_TEXT}>
        Color Scheme
      </div>
      <!-- Built-in themes -->
      <div class="flex gap-2 mb-1">
        {#each builtInOptions as opt}
          <button
            class="px-3 py-1.5 text-xs rounded flex-1 {isIronclad ? 'ironclad-btn' : ''}"
            style:background-color={isIronclad ? undefined : ($currentTheme === opt.name
              ? colors.BUTTON_ACTIVE_BG
              : colors.BUTTON_BG)}
            style:color={$currentTheme === opt.name
              ? colors.BUTTON_ACTIVE_TEXT
              : colors.BUTTON_TEXT}
            onclick={() => selectTheme(opt.name)}
          >
            {opt.label}
          </button>
        {/each}
      </div>
      <!-- Custom themes -->
      {#if customNames.length > 0}
        <div class="flex flex-wrap gap-1 mt-2">
          {#each customNames as name}
            <div class="flex items-center gap-0.5">
              <button
                class="px-3 py-1.5 text-xs rounded"
                style:background-color={$currentTheme === name
                  ? colors.BUTTON_ACTIVE_BG
                  : colors.BUTTON_BG}
                style:color={$currentTheme === name
                  ? colors.BUTTON_ACTIVE_TEXT
                  : colors.BUTTON_TEXT}
                onclick={() => selectTheme(name)}
              >
                {name}
              </button>
              <button
                class="px-1 py-1.5 text-xs rounded hover:opacity-70"
                style:color={colors.BUTTON_TEXT}
                title="Delete theme"
                onclick={() => deleteCustomTheme(name)}
              >
                x
              </button>
            </div>
          {/each}
        </div>
      {/if}
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

    <!-- Color Editor -->
    <div>
      <div class="flex items-center justify-between mb-2">
        <div class="text-xs font-medium" style:color={colors.BUTTON_TEXT}>
          Theme Colors
        </div>
        <div class="flex gap-1">
          <button
            class="px-2 py-1 text-xs rounded hover:opacity-80 {isIronclad ? 'ironclad-btn' : ''}"
            style:background-color={colors.BUTTON_BG}
            style:color={colors.BUTTON_TEXT}
            onclick={startSaveCustom}
          >
            Save As Custom
          </button>
          <button
            class="px-2 py-1 text-xs rounded hover:opacity-80 {isIronclad ? 'ironclad-btn' : ''}"
            style:background-color={colors.BUTTON_BG}
            style:color={colors.BUTTON_TEXT}
            onclick={handleReset}
          >
            Reset
          </button>
        </div>
      </div>

      <!-- Save custom theme input -->
      {#if showSaveInput}
        <div class="flex gap-1 mb-2">
          <input
            type="text"
            bind:value={newThemeName}
            placeholder="Theme name..."
            class="flex-1 px-2 py-1 text-xs rounded border"
            style:background-color={colors.ENTRY_FOCUS_BG}
            style:color={colors.ENTRY_TEXT}
            style:border-color={colors.CELL_BORDER}
            onkeydown={handleSaveKeydown}
          />
          <button
            class="px-2 py-1 text-xs rounded hover:opacity-80"
            style:background-color={colors.BUTTON_ACTIVE_BG}
            style:color={colors.BUTTON_ACTIVE_TEXT}
            onclick={confirmSaveCustom}
          >
            Save
          </button>
          <button
            class="px-2 py-1 text-xs rounded hover:opacity-80"
            style:background-color={colors.BUTTON_BG}
            style:color={colors.BUTTON_TEXT}
            onclick={() => (showSaveInput = false)}
          >
            Cancel
          </button>
        </div>
      {/if}

      <div class="space-y-1">
        {#each themeKeys as key}
          <div class="flex items-center gap-2 text-xs">
            <input
              type="color"
              value={colors[key].substring(0, 7)}
              oninput={(e) => handleColorChange(key, (e.target as HTMLInputElement).value)}
              class="w-6 h-6 rounded border cursor-pointer shrink-0 p-0"
              style:border-color={colors.CELL_BORDER}
            />
            <span style:color={colors.BUTTON_TEXT}>{colorLabels[key] ?? key}</span>
          </div>
        {/each}
      </div>
    </div>
  </div>
</DialogWrapper>
