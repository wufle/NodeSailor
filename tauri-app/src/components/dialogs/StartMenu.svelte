<script lang="ts">
  import {
    isDark,
    currentTheme,
    showStartMenu,
    activeDialog,
  } from "../../lib/stores/uiStore";
  import { effectiveColors } from "../../lib/theme/colors";
  import {
    loadFile,
    saveFile,
    newNetwork,
  } from "../../lib/actions/fileActions";
  import { highlightMatchingNodes } from "../../lib/actions/systemActions";
  import { settings } from "../../lib/stores/settingsStore";
  import { invoke } from "@tauri-apps/api/core";

  let colors = $derived($effectiveColors);
  let isIronclad = $derived($currentTheme === "ironclad");

  function close() {
    showStartMenu.set(false);
  }

  function handleNewNetwork() {
    newNetwork();
    close();
  }

  async function handleSave() {
    await saveFile();
    close();
  }

  async function handleLoad() {
    await loadFile();
    close();
    highlightMatchingNodes();
  }

  function openConfigMenu() {
    close();
    activeDialog.set("customCommands");
  }

  function openDisplayOptions() {
    close();
    activeDialog.set("displayOptionsDialog");
  }

  function openHelp() {
    close();
    activeDialog.set("help");
  }

  function openTutorial() {
    close();
    activeDialog.set("tutorial");
  }

  async function toggleAutoLoad() {
    const newValue = !$settings.auto_load_last_file;
    await invoke("save_settings", {
      settings: { ...$settings, auto_load_last_file: newValue },
    });
    settings.update((s) => ({ ...s, auto_load_last_file: newValue }));
  }

  let buttonClass = $derived(
    "w-full py-2 text-sm rounded hover:opacity-80 transition-opacity" +
    (isIronclad ? " ironclad-btn" : "")
  );
</script>

<!-- Backdrop -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
  class="fixed inset-0 z-40"
  style:background-color="rgba(0,0,0,0.3)"
  onclick={close}
></div>

<!-- Menu -->
<div
  class="fixed z-50 top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[320px] rounded-lg overflow-hidden {isIronclad ? 'ironclad-start-menu' : 'shadow-xl'}"
  style:border={isIronclad ? undefined : `2px solid ${colors.BORDER_COLOR}`}
  style:background-color={isIronclad ? undefined : colors.FRAME_BG}
  onclick={(e) => e.stopPropagation()}
>
  <!-- Logo placeholder -->
  <div class="flex flex-col items-center py-4 gap-2">
    <div
      class="w-20 h-20 rounded-lg flex items-center justify-center text-2xl font-bold {isIronclad ? 'ironclad-logo' : ''}"
      style:background-color={isIronclad ? undefined : colors.BUTTON_BG}
      style:color={isIronclad ? "#e09240" : colors.BUTTON_TEXT}
    >
      NS
    </div>
    <div class="text-xs opacity-60" style:color={colors.BUTTON_TEXT}>
      Version 1.1.3
    </div>
  </div>

  <div class="px-4 pb-4 space-y-2">
    <button
      class={buttonClass}
      style:background-color={colors.BUTTON_BG}
      style:color={colors.BUTTON_TEXT}
      onclick={handleNewNetwork}
    >
      Create New Network
    </button>

    <button
      class={buttonClass}
      style:background-color={colors.BUTTON_BG}
      style:color={colors.BUTTON_TEXT}
      onclick={handleSave}
    >
      Save
    </button>

    <button
      class={buttonClass}
      style:background-color={colors.BUTTON_BG}
      style:color={colors.BUTTON_TEXT}
      onclick={handleLoad}
    >
      Load
    </button>

    <!-- Auto-load checkbox -->
    <label
      class="flex items-center gap-2 px-3 py-2 text-xs cursor-pointer"
      style:color={colors.BUTTON_TEXT}
    >
      <input
        type="checkbox"
        checked={$settings.auto_load_last_file ?? false}
        onchange={toggleAutoLoad}
        class="cursor-pointer"
      />
      <span>Auto-load last file on startup</span>
    </label>

    <button
      class={buttonClass}
      style:background-color={colors.BUTTON_BG}
      style:color={colors.BUTTON_TEXT}
      onclick={openDisplayOptions}
    >
      Display Options
    </button>

    <button
      class={buttonClass}
      style:background-color={colors.BUTTON_BG}
      style:color={colors.BUTTON_TEXT}
      onclick={openConfigMenu}
    >
      Custom Commands
    </button>

    <button
      class={buttonClass}
      style:background-color={colors.BUTTON_BG}
      style:color={colors.BUTTON_TEXT}
      onclick={openTutorial}
    >
      Tutorial
    </button>

    <button
      class={buttonClass}
      style:background-color={colors.BUTTON_BG}
      style:color={colors.BUTTON_TEXT}
      onclick={openHelp}
    >
      Help
    </button>

    <button
      class={buttonClass}
      style:background-color={colors.BUTTON_BG}
      style:color={colors.BUTTON_TEXT}
      onclick={close}
    >
      Close
    </button>
  </div>
</div>
