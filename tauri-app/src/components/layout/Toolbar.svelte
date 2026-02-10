<script lang="ts">
  import {
    mode,
    isDark,
    currentTheme,
    groupsModeActive,
    activeDialog,
    showStartMenu,
  } from "../../lib/stores/uiStore";
  import { getThemeColors } from "../../lib/theme/colors";
  import { pingAllNodes, clearPingResults } from "../../lib/actions/pingActions";
  import { getLocalIps } from "../../lib/actions/systemActions";
  import { nodes, pingResults } from "../../lib/stores/networkStore";

  let colors = $derived(getThemeColors($currentTheme));
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

  let searchingForHost = $state(false);

  async function highlightMatchingNodes() {
    searchingForHost = true;
    try {
      const localIps = await getLocalIps();
      const allNodes = $nodes;
      const matchingIndices: number[] = [];

      // Find all matching nodes
      for (let i = 0; i < allNodes.length; i++) {
        const node = allNodes[i];
        const vlanValues = Object.values(node.vlans);
        if (vlanValues.some((ip) => localIps.includes(ip))) {
          matchingIndices.push(i);
        }
      }

      if (matchingIndices.length > 0) {
        // Flash matching nodes 5 times
        for (let flash = 0; flash < 5; flash++) {
          // Highlight on
          const highlightState: Record<number, boolean[]> = {};
          for (const idx of matchingIndices) {
            highlightState[idx] = [true];
          }
          pingResults.set(highlightState);

          await new Promise(resolve => setTimeout(resolve, 300));

          // Highlight off
          pingResults.set({});

          await new Promise(resolve => setTimeout(resolve, 200));
        }
      } else {
        // No matching node found - clear all highlights briefly to show it ran
        pingResults.set({});
      }
    } catch (error) {
      console.error("Who am I failed:", error);
      // Clear highlights on error
      pingResults.set({});
    } finally {
      searchingForHost = false;
    }
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
  <button
    class="{buttonClass} font-bold"
    style:background-color={colors.BUTTON_BG}
    style:color={colors.BUTTON_TEXT}
    onclick={() => showStartMenu.set(true)}
  >
    Start Menu
  </button>

  <!-- Mode Toggle -->
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

  <!-- Display Options (always visible) -->
  <button
    class={buttonClass}
    style:background-color={colors.BUTTON_BG}
    style:color={colors.BUTTON_TEXT}
    onclick={() => activeDialog.set("displayOptions")}
  >
    Display Options
  </button>

  <!-- Configuration-only buttons -->
  {#if $mode === "Configuration"}
    <button
      class={buttonClass}
      style:background-color={colors.BUTTON_BG}
      style:color={colors.BUTTON_TEXT}
      onclick={() => activeDialog.set("vlanConfig")}
    >
      VLAN Config
    </button>

    <button
      class={buttonClass}
      style:background-color={colors.BUTTON_BG}
      style:color={colors.BUTTON_TEXT}
      onclick={() => activeDialog.set("nodeList")}
    >
      Node List
    </button>

    <button
      class={buttonClass}
      style:background-color={colors.BUTTON_BG}
      style:color={colors.BUTTON_TEXT}
      onclick={() => activeDialog.set("connectionList")}
    >
      Connections List
    </button>

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

    <button
      class={buttonClass}
      style:background-color={colors.BUTTON_BG}
      style:color={colors.BUTTON_TEXT}
      onclick={() => activeDialog.set("groupEditor")}
    >
      Edit Groups
    </button>
  {/if}

  <!-- Always visible buttons -->
  <button
    class={buttonClass}
    style:background-color={colors.BUTTON_BG}
    style:color={colors.BUTTON_TEXT}
    style:opacity={searchingForHost ? "0.6" : "1"}
    disabled={searchingForHost}
    onclick={highlightMatchingNodes}
  >
    {searchingForHost ? "Searching..." : "Who am I?"}
  </button>

  <button
    class={buttonClass}
    style:background-color={colors.BUTTON_BG}
    style:color={colors.BUTTON_TEXT}
    onclick={() => clearPingResults()}
  >
    Clear Status
  </button>

  <button
    class={buttonClass}
    style:background-color={colors.BUTTON_BG}
    style:color={colors.BUTTON_TEXT}
    onclick={() => pingAllNodes()}
  >
    Ping All
  </button>
</div>
