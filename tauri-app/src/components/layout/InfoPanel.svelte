<script lang="ts">
  import {
    selectedNodeIndex,
    currentTheme,
    mode,
    activeDialog,
  } from "../../lib/stores/uiStore";
  import {
    nodes,
    vlanLabels,
    vlanLabelOrder,
    pingResults,
    removeNode,
    customCommands,
  } from "../../lib/stores/networkStore";
  import { effectiveColors } from "../../lib/theme/colors";
  import { getPopulatedVlans } from "../../lib/utils/vlanUtils";
  import {
    openRemoteDesktop,
    openSSH,
    openFileExplorer,
    openWebBrowser,
    executeCustomCommand,
  } from "../../lib/actions/systemActions";
  import type { CustomCommand } from "../../lib/types/network";

  let colors = $derived($effectiveColors);
  let isIronclad = $derived($currentTheme === "ironclad");

  // Show hovered node if hovering, otherwise show selected node
  let displayNodeIndex = $derived($selectedNodeIndex);

  let selectedNode = $derived(
    displayNodeIndex !== null ? $nodes[displayNodeIndex] : null
  );

  let vlans = $derived(
    selectedNode
      ? getPopulatedVlans(selectedNode, $vlanLabelOrder)
      : []
  );

  let nodeResults = $derived(
    displayNodeIndex !== null
      ? $pingResults[displayNodeIndex]
      : undefined
  );

  // Map VLAN index to ping result
  function getVlanColor(vlanIdx: number): string | null {
    if (!nodeResults || vlanIdx >= nodeResults.length) return null;
    return nodeResults[vlanIdx]
      ? colors.NODE_PING_SUCCESS
      : colors.NODE_PING_FAILURE;
  }

  // Get applicable custom commands for the current node
  function getApplicableCommands(
    nodeIndex: number
  ): { name: string; template: string }[] {
    const node = $nodes[nodeIndex];
    if (!node) return [];
    const result: { name: string; template: string }[] = [];

    for (const [name, cmd] of Object.entries($customCommands)) {
      let template: string;
      let applicableNodes: string[] | null = null;

      if (typeof cmd === "string") {
        template = cmd;
      } else {
        template = (cmd as CustomCommand).template;
        applicableNodes = (cmd as CustomCommand).applicable_nodes;
      }

      if (
        applicableNodes !== null &&
        !applicableNodes.includes(node.name)
      ) {
        continue;
      }

      result.push({ name, template });
    }
    return result;
  }
</script>

{#if selectedNode}
  <div
    class="absolute top-2 right-2 p-3 rounded min-w-[180px] {isIronclad ? 'ironclad-info-panel' : 'shadow-lg'}"
    style:background-color={colors.INFO_NOTE_BG}
    style:color={colors.INFO_TEXT}
    style:border={isIronclad ? undefined : `1px solid ${colors.BORDER_COLOR}`}
  >
    <div class="text-sm font-medium mb-2">
      <span class="opacity-60">Name:</span>
      <span class="ml-2">{selectedNode.name}</span>
    </div>

    {#each vlans as vlan, i}
      <div class="text-sm flex items-center gap-2 py-0.5">
        <span class="opacity-60">
          {$vlanLabels[vlan.key] ?? vlan.key}:
        </span>
        <span
          class="px-1 rounded"
          style:background-color={getVlanColor(i) ?? "transparent"}
          style:color={getVlanColor(i) ? "#fff" : colors.INFO_TEXT}
        >
          {vlan.value}
        </span>
      </div>
    {/each}

    <!-- Action buttons -->
    <div class="border-t mt-2 pt-2" style:border-color={colors.BORDER_COLOR}>
      <button
        class="block w-full text-left px-2 py-1 text-sm rounded hover:opacity-80"
        style:color={colors.INFO_TEXT}
        onclick={() => {
          (window as any).__editNodeIndex = displayNodeIndex;
          (window as any).__newNodePosition = null;
          activeDialog.set("nodeEditor");
        }}
      >
        Edit Node Information
      </button>
      <button
        class="block w-full text-left px-2 py-1 text-sm rounded hover:opacity-80"
        style:color={colors.INFO_TEXT}
        onclick={() => openRemoteDesktop(selectedNode!.remote_desktop_address)}
      >
        Open Remote Desktop
      </button>
      <button
        class="block w-full text-left px-2 py-1 text-sm rounded hover:opacity-80"
        style:color={colors.INFO_TEXT}
        onclick={() => {
          const ip = Object.values(selectedNode!.vlans).find((v) => v && v.trim() !== "") ?? "";
          openSSH(ip);
        }}
      >
        Open SSH
      </button>
      <button
        class="block w-full text-left px-2 py-1 text-sm rounded hover:opacity-80"
        style:color={colors.INFO_TEXT}
        onclick={() => openFileExplorer(selectedNode!.file_path)}
      >
        Open File Explorer
      </button>
      <button
        class="block w-full text-left px-2 py-1 text-sm rounded hover:opacity-80"
        style:color={colors.INFO_TEXT}
        onclick={() => openWebBrowser(selectedNode!.web_config_url)}
      >
        Open Web Browser
      </button>

      {#if $mode === "Configuration"}
        <div class="border-t mt-1" style:border-color={colors.BORDER_COLOR}></div>
        <button
          class="block w-full text-left px-2 py-1 text-sm rounded hover:opacity-80"
          style:color="#ef4444"
          onclick={() => { if (displayNodeIndex !== null) removeNode(displayNodeIndex); }}
        >
          Delete Node
        </button>
      {/if}

      {#if displayNodeIndex !== null}
        {@const cmds = getApplicableCommands(displayNodeIndex)}
        {#if cmds.length > 0}
          <div class="border-t mt-1" style:border-color={colors.BORDER_COLOR}></div>
          {#each cmds as cmd}
            <button
              class="block w-full text-left px-2 py-1 text-sm rounded hover:opacity-80"
              style:color={colors.INFO_TEXT}
              onclick={() => executeCustomCommand(cmd.template, selectedNode!)}
            >
              {cmd.name}
            </button>
          {/each}
        {/if}
      {/if}
    </div>
  </div>
{/if}
