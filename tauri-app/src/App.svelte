<script lang="ts">
  import { onMount } from "svelte";
  import { get } from "svelte/store";
  import { isDark, currentTheme, mode, showStartMenu, unsavedChanges, activeDialog, panX, panY, activeTool, connectionStartNodeIndex, selectedNodeIndex } from "./lib/stores/uiStore";
  import type { ThemeName } from "./lib/stores/uiStore";
  import { effectiveColors, loadColorOverrides, loadCustomThemes, matrixTheme, registerCustomTheme } from "./lib/theme/colors";
  import { matrixMode, previousTheme } from "./lib/stores/matrixStore";
  import MatrixRain from "./components/canvas/MatrixRain.svelte";
  import TopologyCanvas from "./components/canvas/TopologyCanvas.svelte";
  import Toolbar from "./components/layout/Toolbar.svelte";
  import ToolSidebar from "./components/layout/ToolSidebar.svelte";
  import InfoPanel from "./components/layout/InfoPanel.svelte";
  import DisplayOptionsPanel from "./components/layout/DisplayOptionsPanel.svelte";
  import ModeBanner from "./components/layout/ModeBanner.svelte";
  import ContextMenu from "./components/canvas/ContextMenu.svelte";
  import StartMenu from "./components/dialogs/StartMenu.svelte";
  import HelpWindow from "./components/dialogs/HelpWindow.svelte";
  import TutorialWalkthrough from "./components/dialogs/TutorialWalkthrough.svelte";
  import NodeEditor from "./components/dialogs/NodeEditor.svelte";
  import ConnectionEditor from "./components/dialogs/ConnectionEditor.svelte";
  import ConfirmDialog from "./components/dialogs/ConfirmDialog.svelte";
  import StickyNoteEditor from "./components/dialogs/StickyNoteEditor.svelte";
  import DialogWrapper from "./components/dialogs/DialogWrapper.svelte";
  import NodeListEditor from "./components/editors/NodeListEditor.svelte";
  import ConnectionListEditor from "./components/editors/ConnectionListEditor.svelte";
  import GroupEditor from "./components/editors/GroupEditor.svelte";
  import VlanConfigEditor from "./components/editors/VlanConfigEditor.svelte";
  import DisplayOptionsEditor from "./components/editors/DisplayOptions.svelte";
  import CustomCommandsEditor from "./components/editors/CustomCommandsEditor.svelte";
  import DisplayOptionsDialog from "./components/dialogs/DisplayOptionsDialog.svelte";
  import NetworkDiscoveryDialog from "./components/dialogs/NetworkDiscoveryDialog.svelte";
  import BgImageOpacityDialog from "./components/dialogs/BgImageOpacityDialog.svelte";
  import TerminalPane from "./components/layout/TerminalPane.svelte";
  import { terminalVisible } from "./lib/stores/terminalStore";
  import { removeNode } from "./lib/stores/networkStore";
  import { loadFile, saveFile } from "./lib/actions/fileActions";
  import { highlightMatchingNodes } from "./lib/actions/systemActions";
  import { settings } from "./lib/stores/settingsStore";
  import { invoke } from "@tauri-apps/api/core";

  // Reactive theme application
  $effect(() => {
    const el = document.documentElement;
    el.classList.remove("light", "dark", "theme-ironclad", "theme-matrix");
    if ($currentTheme === "matrix") {
      el.classList.add("theme-matrix");
    } else if ($currentTheme === "ironclad") {
      el.classList.add("theme-ironclad");
    } else if ($currentTheme === "light") {
      el.classList.add("light");
    } else {
      el.classList.add("dark");
    }
  });

  // Persist current theme to settings (skip matrix — it's a secret easter egg)
  $effect(() => {
    if ($currentTheme === "matrix") return;
    settings.update((s) => ({ ...s, last_custom_theme: $currentTheme }));
    invoke("save_settings", { settings: { last_custom_theme: $currentTheme } }).catch((e) =>
      console.error("Failed to save theme setting:", e)
    );
  });

  // Keyboard shortcuts
  function handleKeydown(e: KeyboardEvent) {
    // Don't handle shortcuts if focus is in an input
    const tag = (e.target as HTMLElement)?.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;

    // Arrow keys for panning
    if (e.key === "ArrowUp" || e.key === "ArrowDown" || e.key === "ArrowLeft" || e.key === "ArrowRight") {
      e.preventDefault();
      const panAmount = 50;

      switch (e.key) {
        case "ArrowUp":
          panY.update((y) => y + panAmount);
          break;
        case "ArrowDown":
          panY.update((y) => y - panAmount);
          break;
        case "ArrowLeft":
          panX.update((x) => x + panAmount);
          break;
        case "ArrowRight":
          panX.update((x) => x - panAmount);
          break;
      }
      return;
    }

    // Escape: revert to select tool, cancel connection
    if (e.key === "Escape") {
      e.preventDefault();
      activeTool.set("select");
      connectionStartNodeIndex.set(null);
      return;
    }

    // Delete: delete selected node (Configuration mode only)
    if ((e.key === "Delete" || e.key === "Backspace") && $mode === "Configuration") {
      const idx = get(selectedNodeIndex);
      if (idx !== null) {
        e.preventDefault();
        removeNode(idx);
        selectedNodeIndex.set(null);
        return;
      }
    }

    // Tool shortcuts (Configuration mode only, no modifier keys)
    if (!e.ctrlKey && !e.altKey && !e.shiftKey && $mode === "Configuration") {
      switch (e.key.toLowerCase()) {
        case "v":
          e.preventDefault();
          activeTool.set("select");
          connectionStartNodeIndex.set(null);
          return;
        case "n":
          e.preventDefault();
          activeTool.set("addNode");
          return;
        case "c":
          e.preventDefault();
          activeTool.set("connect");
          return;
        case "t":
          e.preventDefault();
          activeTool.set("addNote");
          return;
      }
    }

    const key = e.key.toLowerCase();

    if (e.ctrlKey && e.shiftKey && key === "m") {
      e.preventDefault();
      matrixMode.update((m) => {
        if (!m) {
          previousTheme.set(get(currentTheme));
          currentTheme.set("matrix");
        } else {
          currentTheme.set(get(previousTheme));
        }
        return !m;
      });
    } else if (e.ctrlKey && e.shiftKey && key === "c") {
      e.preventDefault();
      const cycle: ThemeName[] = ["dark", "light"];
      currentTheme.update((t) => {
        const idx = cycle.indexOf(t);
        return cycle[(idx + 1) % cycle.length];
      });
    } else if (e.ctrlKey && key === "s") {
      e.preventDefault();
      saveFile();
    } else if (e.ctrlKey && key === "l") {
      e.preventDefault();
      loadFile().then(() => {
        highlightMatchingNodes();
      });
    } else if (e.key === "F1") {
      e.preventDefault();
      activeDialog.set("help");
    } else if (e.shiftKey && key === "i") {
      e.preventDefault();
      currentTheme.set("ironclad");
    } else if (e.ctrlKey && e.key === "`") {
      e.preventDefault();
      terminalVisible.update((v) => !v);
    }
  }

  onMount(async () => {
    // Load settings first
    try {
      const loadedSettings = await invoke("load_settings") as any;
      settings.set(loadedSettings);
      if (loadedSettings.custom_themes) {
        loadCustomThemes(loadedSettings.custom_themes);
      }
      if (loadedSettings.custom_theme_colors) {
        loadColorOverrides(loadedSettings.custom_theme_colors);
      }
      if (loadedSettings.last_custom_theme) {
        currentTheme.set(loadedSettings.last_custom_theme);
      }
    } catch (e) {
      console.error("Failed to load settings:", e);
    }

    // Register matrix easter egg theme after settings load (loadCustomThemes replaces all custom themes)
    registerCustomTheme("matrix", matrixTheme);

    // Auto-load last file if enabled
    const currentSettings = get(settings);
    if (currentSettings.auto_load_last_file && currentSettings.last_file_path) {
      try {
        await loadFile(currentSettings.last_file_path);
        highlightMatchingNodes();
      } catch (e) {
        console.error("Auto-load failed:", e);
        showStartMenu.set(true);
      }
    } else {
      showStartMenu.set(true);
    }

    // Auto-launch tutorial on first run
    if (!currentSettings.tutorial_completed) {
      // Small delay to ensure UI is ready
      setTimeout(() => {
        activeDialog.set("tutorial");
      }, 500);
    }
  });

  let colors = $derived($effectiveColors);

  function onContextMenu(e: MouseEvent) {
    const target = e.target as HTMLElement;
    if (
      target.tagName === "INPUT" ||
      target.tagName === "TEXTAREA" ||
      target.isContentEditable ||
      target.closest(".terminal-pane-body")
    ) {
      return;
    }
    e.preventDefault();
  }
</script>

<svelte:window onkeydown={handleKeydown} />

<div
  class="flex flex-col w-full h-full"
  style:background-color={colors.FRAME_BG}
  oncontextmenu={onContextMenu}
>
  <Toolbar />
  <ModeBanner />

  <div class="relative flex-1 overflow-hidden">
    {#if $matrixMode}
      <MatrixRain />
    {/if}
    <TopologyCanvas />
    <ToolSidebar />
    <InfoPanel />
    <DisplayOptionsPanel />
    <ContextMenu />
  </div>
  <TerminalPane />
</div>

<!-- Dialogs -->
{#if $showStartMenu}
  <StartMenu />
{/if}

{#if $activeDialog === "help"}
  <HelpWindow />
{/if}

{#if $activeDialog === "tutorial"}
  <TutorialWalkthrough />
{/if}

{#if $activeDialog === "nodeEditor"}
  <NodeEditor />
{/if}

{#if $activeDialog === "connectionEditor"}
  <ConnectionEditor />
{/if}

{#if $activeDialog === "confirm"}
  <ConfirmDialog />
{/if}

{#if $activeDialog === "stickyNote"}
  <StickyNoteEditor />
{/if}

{#if $activeDialog === "nodeList"}
  <NodeListEditor />
{/if}

{#if $activeDialog === "connectionList"}
  <ConnectionListEditor />
{/if}

{#if $activeDialog === "groupEditor"}
  <GroupEditor />
{/if}

{#if $activeDialog === "vlanConfig"}
  <VlanConfigEditor />
{/if}

{#if $activeDialog === "displayOptions"}
  <DisplayOptionsEditor />
{/if}

{#if $activeDialog === "customCommands"}
  <CustomCommandsEditor />
{/if}

{#if $activeDialog === "displayOptionsDialog"}
  <DisplayOptionsDialog />
{/if}

{#if $activeDialog === "networkDiscovery"}
  <NetworkDiscoveryDialog />
{/if}

{#if $activeDialog === "bgImageOpacity"}
  <BgImageOpacityDialog />
{/if}
