<script lang="ts">
  import {
    mode,
    isDark,
    currentTheme,
    groupsModeActive,
    activeDialog,
    showStartMenu,
  } from "../../lib/stores/uiStore";
  import { effectiveColors } from "../../lib/theme/colors";
  import { pingAllNodes, clearPingResults } from "../../lib/actions/pingActions";
  import { addBackgroundImage } from "../../lib/stores/networkStore";
  import { open } from "@tauri-apps/plugin-dialog";
  import { invoke } from "@tauri-apps/api/core";
  import TooltipWrapper from "../common/TooltipWrapper.svelte";

  let colors = $derived($effectiveColors);
  let isIronclad = $derived($currentTheme === "ironclad");
  let valveTurning = $state(false);

  function toggleMode() {
    mode.update((m) => (m === "Operator" ? "Configuration" : "Operator"));
    if ($groupsModeActive) {
      groupsModeActive.set(false);
    }
    if (isIronclad) {
      valveTurning = true;
      setTimeout(() => (valveTurning = false), 300);
    }
  }

  function toggleGroupsMode() {
    groupsModeActive.update((g) => !g);
  }

  async function addBackgroundImageFromFile() {
    const selected = await open({
      filters: [{ name: "Images", extensions: ["png", "jpg", "jpeg", "gif", "svg", "webp", "bmp"] }],
      multiple: false,
    });
    if (!selected) return;

    const path = selected as string;
    const dataUrl: string = await invoke("read_image_as_base64", { path });

    const filename = path.split(/[\\/]/).pop() ?? "image";

    // Get natural dimensions
    const img = new Image();
    img.src = dataUrl;
    await new Promise<void>((resolve) => { img.onload = () => resolve(); });

    // Scale to reasonable canvas size
    const maxDim = 400;
    let w = img.naturalWidth;
    let h = img.naturalHeight;
    if (w > maxDim || h > maxDim) {
      const scale = maxDim / Math.max(w, h);
      w *= scale;
      h *= scale;
    }

    const id = Date.now().toString(36) + Math.random().toString(36).slice(2);
    addBackgroundImage({
      id,
      dataUrl,
      x: 100,
      y: 100,
      width: w,
      height: h,
      opacity: 0.5,
      filename,
    });
  }

  let buttonClass = $derived(
    "px-3 py-1.5 text-xs font-medium rounded transition-colors" +
    (isIronclad ? " ironclad-btn" : "")
  );
</script>

<div
  class="flex items-center gap-1 px-2 py-1.5 flex-wrap {isIronclad ? 'ironclad-toolbar' : ''}"
  style:background-color={isIronclad ? undefined : colors.FRAME_BG}
  style:border-bottom={isIronclad ? undefined : `1px solid ${colors.BORDER_COLOR}`}
>
  <!-- Start Menu -->
  <TooltipWrapper text="Open start menu for file operations and settings">
    <button
      class="{buttonClass} font-bold"
      style:background-color={colors.BUTTON_BG}
      style:color={colors.BUTTON_TEXT}
      onclick={() => showStartMenu.set(true)}
    >
      Start Menu
    </button>
  </TooltipWrapper>

  <!-- Mode Toggle -->
  <TooltipWrapper text="Switch between Configuration (edit) and Operator (monitor) modes">
    <button
      class={buttonClass}
      style:background-color={$mode === "Configuration"
        ? colors.BUTTON_CONFIGURATION_MODE
        : colors.BUTTON_BG}
      style:color={colors.BUTTON_TEXT}
      onclick={toggleMode}
    >
      {#if isIronclad}
        <span class="inline-block {valveTurning ? 'valve-turning' : ''}" style="margin-right: 4px;">&#9881;</span>
      {/if}
      {$mode} Mode
    </button>
  </TooltipWrapper>

  <!-- Configuration-only buttons -->
  {#if $mode === "Configuration"}
    <TooltipWrapper text="Configure VLAN labels and display order">
      <button
        class={buttonClass}
        style:background-color={colors.BUTTON_BG}
        style:color={colors.BUTTON_TEXT}
        onclick={() => activeDialog.set("vlanConfig")}
      >
        VLAN Config
      </button>
    </TooltipWrapper>

    <TooltipWrapper text="Edit all nodes in a spreadsheet-like table">
      <button
        class={buttonClass}
        style:background-color={colors.BUTTON_BG}
        style:color={colors.BUTTON_TEXT}
        onclick={() => activeDialog.set("nodeList")}
      >
        Node List
      </button>
    </TooltipWrapper>

    <TooltipWrapper text="Edit all connections in a spreadsheet-like table">
      <button
        class={buttonClass}
        style:background-color={colors.BUTTON_BG}
        style:color={colors.BUTTON_TEXT}
        onclick={() => activeDialog.set("connectionList")}
      >
        Connections List
      </button>
    </TooltipWrapper>

    <TooltipWrapper text="Toggle Groups mode to draw group rectangles on canvas">
      <button
        class="{buttonClass}"
        style:background-color={$groupsModeActive
          ? colors.BUTTON_ACTIVE_BG
          : colors.BUTTON_BG}
        style:color={colors.BUTTON_TEXT}
        onclick={toggleGroupsMode}
      >
        {$groupsModeActive ? "Groups (Active)" : "Groups"}
      </button>
    </TooltipWrapper>

    <TooltipWrapper text="Edit group colors and properties">
      <button
        class={buttonClass}
        style:background-color={colors.BUTTON_BG}
        style:color={colors.BUTTON_TEXT}
        onclick={() => activeDialog.set("groupEditor")}
      >
        Edit Groups
      </button>
    </TooltipWrapper>

    <TooltipWrapper text="Scan your network to discover devices and auto-create nodes">
      <button
        class={buttonClass}
        style:background-color={colors.BUTTON_BG}
        style:color={colors.BUTTON_TEXT}
        onclick={() => activeDialog.set("networkDiscovery")}
      >
        Discover
      </button>
    </TooltipWrapper>

    <TooltipWrapper text="Add a background image to the canvas">
      <button
        class={buttonClass}
        style:background-color={colors.BUTTON_BG}
        style:color={colors.BUTTON_TEXT}
        onclick={addBackgroundImageFromFile}
      >
        Add Image
      </button>
    </TooltipWrapper>
  {/if}

  <!-- Always visible buttons -->
  <TooltipWrapper text="Clear all node status indicators and highlights">
    <button
      class={buttonClass}
      style:background-color={colors.BUTTON_BG}
      style:color={colors.BUTTON_TEXT}
      onclick={() => clearPingResults()}
    >
      Clear Status
    </button>
  </TooltipWrapper>

  <TooltipWrapper text="Ping all nodes to check network connectivity">
    <button
      class={buttonClass}
      style:background-color={colors.BUTTON_BG}
      style:color={colors.BUTTON_TEXT}
      onclick={() => pingAllNodes()}
    >
      Ping All
    </button>
  </TooltipWrapper>
</div>
