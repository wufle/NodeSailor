<script lang="ts">
  import {
    mode,
    isDark,
    groupsModeActive,
    activeDialog,
    showStartMenu,
  } from "../../lib/stores/uiStore";
  import { getThemeColors } from "../../lib/theme/colors";
  import { pingAllNodes, clearPingResults } from "../../lib/actions/pingActions";
  import { getLocalIps } from "../../lib/actions/systemActions";
  import { nodes, pingResults } from "../../lib/stores/networkStore";

  let colors = $derived(getThemeColors($isDark));

  function toggleMode() {
    mode.update((m) => (m === "Operator" ? "Configuration" : "Operator"));
    if ($groupsModeActive) {
      groupsModeActive.set(false);
    }
  }

  function toggleGroupsMode() {
    groupsModeActive.update((g) => !g);
  }

  async function highlightMatchingNodes() {
    try {
      const localIps = await getLocalIps();
      const allNodes = $nodes;
      for (let i = 0; i < allNodes.length; i++) {
        const node = allNodes[i];
        const vlanValues = Object.values(node.vlans);
        if (vlanValues.some((ip) => localIps.includes(ip))) {
          // Flash the node by toggling ping results
          pingResults.update((pr) => ({
            ...pr,
            [i]: [true], // Mark as host
          }));
        }
      }
    } catch {
      // Best-effort
    }
  }

  let buttonClass = "px-3 py-1.5 text-xs font-medium rounded transition-colors";
</script>

<div
  class="flex items-center gap-1 px-2 py-1 flex-wrap"
  style:background-color={colors.FRAME_BG}
  style:border-bottom="1px solid {colors.BORDER_COLOR}"
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
  {/if}

  <!-- Always visible buttons -->
  <button
    class={buttonClass}
    style:background-color={colors.BUTTON_BG}
    style:color={colors.BUTTON_TEXT}
    onclick={highlightMatchingNodes}
  >
    Who am I?
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
