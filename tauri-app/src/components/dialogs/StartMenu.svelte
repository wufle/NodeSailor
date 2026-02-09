<script lang="ts">
  import {
    isDark,
    showStartMenu,
    activeDialog,
  } from "../../lib/stores/uiStore";
  import { getThemeColors } from "../../lib/theme/colors";
  import {
    loadFile,
    saveFile,
    newNetwork,
  } from "../../lib/actions/fileActions";
  import { settings } from "../../lib/stores/settingsStore";

  let colors = $derived(getThemeColors($isDark));

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
  }

  function toggleTheme() {
    isDark.update((d) => !d);
  }

  function openConfigMenu() {
    close();
    activeDialog.set("customCommands");
  }

  function openHelp() {
    close();
    activeDialog.set("help");
  }

  let buttonClass =
    "w-full py-2 text-sm rounded hover:opacity-80 transition-opacity";
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
  class="fixed z-50 top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[320px] rounded-lg shadow-xl overflow-hidden"
  style:border="2px solid {colors.BORDER_COLOR}"
  style:background-color={colors.FRAME_BG}
  onclick={(e) => e.stopPropagation()}
>
  <!-- Logo placeholder -->
  <div class="flex justify-center py-4">
    <div
      class="w-20 h-20 rounded-lg flex items-center justify-center text-2xl font-bold"
      style:background-color={colors.BUTTON_BG}
      style:color={colors.BUTTON_TEXT}
    >
      NS
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

    <button
      class={buttonClass}
      style:background-color={colors.BUTTON_BG}
      style:color={colors.BUTTON_TEXT}
      onclick={toggleTheme}
    >
      {$isDark ? "Light Mode" : "Dark Mode"}
    </button>

    <button
      class={buttonClass}
      style:background-color={colors.BUTTON_BG}
      style:color={colors.BUTTON_TEXT}
      onclick={openConfigMenu}
    >
      Configuration Menu
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
