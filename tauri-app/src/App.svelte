<script lang="ts">
  import { onMount } from "svelte";
  import { isDark, mode, showStartMenu, unsavedChanges, activeDialog } from "./lib/stores/uiStore";
  import { getThemeColors } from "./lib/theme/colors";
  import TopologyCanvas from "./components/canvas/TopologyCanvas.svelte";
  import Toolbar from "./components/layout/Toolbar.svelte";
  import InfoPanel from "./components/layout/InfoPanel.svelte";
  import ZoomControls from "./components/layout/ZoomControls.svelte";
  import ModeBanner from "./components/layout/ModeBanner.svelte";
  import ContextMenu from "./components/canvas/ContextMenu.svelte";
  import StartMenu from "./components/dialogs/StartMenu.svelte";
  import HelpWindow from "./components/dialogs/HelpWindow.svelte";
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
  import ColorSchemeEditor from "./components/editors/ColorSchemeEditor.svelte";
  import { loadFile, saveFile } from "./lib/actions/fileActions";

  // Reactive theme application
  $effect(() => {
    if ($isDark) {
      document.documentElement.classList.add("dark");
      document.documentElement.classList.remove("light");
    } else {
      document.documentElement.classList.add("light");
      document.documentElement.classList.remove("dark");
    }
  });

  // Keyboard shortcuts
  function handleKeydown(e: KeyboardEvent) {
    // Don't handle shortcuts if focus is in an input
    const tag = (e.target as HTMLElement)?.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;

    if (e.ctrlKey && e.shiftKey && e.key === "C") {
      e.preventDefault();
      isDark.update((d) => !d);
    } else if (e.ctrlKey && e.key === "s") {
      e.preventDefault();
      saveFile();
    } else if (e.ctrlKey && e.key === "l") {
      e.preventDefault();
      loadFile();
    } else if (e.key === "F1") {
      e.preventDefault();
      activeDialog.set("help");
    }
  }

  onMount(async () => {
    try {
      await loadFile("/Users/mark/Code/3rd-party/NodeSailor-Vibed/NodeSailor/example network.json");
    } catch (e) {
      console.error("Auto-load failed:", e);
      showStartMenu.set(true);
    }
  });

  let colors = $derived(getThemeColors($isDark));
</script>

<svelte:window onkeydown={handleKeydown} />

<div
  class="flex flex-col w-full h-full"
  style:background-color={colors.FRAME_BG}
>
  <Toolbar />
  <ModeBanner />

  <div class="relative flex-1 overflow-hidden">
    <TopologyCanvas />
    <InfoPanel />
    <ZoomControls />
    <ContextMenu />
  </div>
</div>

<!-- Dialogs -->
{#if $showStartMenu}
  <StartMenu />
{/if}

{#if $activeDialog === "help"}
  <HelpWindow />
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

{#if $activeDialog === "colorScheme"}
  <ColorSchemeEditor />
{/if}
