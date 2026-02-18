<script lang="ts">
  import {
    contextMenu,
    mode,
    currentTheme,
    activeDialog,
  } from "../../lib/stores/uiStore";
  import {
    nodes,
    connections,
    removeNode,
    removeConnection,
    removeStickyNote,
    removeGroup,
    removeBackgroundImage,
    customCommands,
  } from "../../lib/stores/networkStore";
  import { effectiveColors } from "../../lib/theme/colors";
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

  let menuX = $state(0);
  let menuY = $state(0);
  let menuReady = $state(false);
  let menuEl: HTMLDivElement | undefined = $state();

  // Re-run positioning whenever contextMenu changes (handles re-opens)
  $effect(() => {
    // Track the context menu state to re-trigger on changes
    const cx = $contextMenu.x;
    const cy = $contextMenu.y;
    const visible = $contextMenu.visible;
    if (!visible || !menuEl) return;

    menuReady = false;
    requestAnimationFrame(() => {
      if (!menuEl) return;
      const pad = 4;
      const rect = menuEl.getBoundingClientRect();
      let x = cx;
      let y = cy;

      if (x + rect.width > window.innerWidth - pad) {
        x = window.innerWidth - rect.width - pad;
      }
      if (y + rect.height > window.innerHeight - pad) {
        y = window.innerHeight - rect.height - pad;
      }
      if (x < pad) x = pad;
      if (y < pad) y = pad;

      menuX = x;
      menuY = y;
      menuReady = true;
    });
  });

  function close() {
    contextMenu.set({
      visible: false,
      x: 0,
      y: 0,
      nodeIndex: null,
      connectionIndex: null,
    });
    (window as any).__contextStickyIndex = undefined;
    (window as any).__contextGroupIndex = undefined;
    (window as any).__contextBgImageIndex = undefined;
  }

  function handleAction(action: () => void) {
    action();
    close();
  }

  // Close on click outside
  function handleWindowClick() {
    if ($contextMenu.visible) {
      close();
    }
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

<svelte:window onclick={handleWindowClick} />

{#if $contextMenu.visible}
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div
    bind:this={menuEl}
    class="fixed z-50 rounded overflow-hidden {isIronclad ? 'ironclad-context-menu' : 'shadow-lg'}"
    style:left="{menuX}px"
    style:top="{menuY}px"
    style:visibility={menuReady ? 'visible' : 'hidden'}
    style:background-color={isIronclad ? undefined : colors.BUTTON_BG}
    style:border={isIronclad ? undefined : `1px solid ${colors.BORDER_COLOR}`}
    onclick={(e) => e.stopPropagation()}
    oncontextmenu={(e) => e.preventDefault()}
  >
    {#if $contextMenu.nodeIndex !== null}
      {@const nodeIdx = $contextMenu.nodeIndex}
      {@const node = $nodes[nodeIdx]}
      {#if node}
        <button
          class="block w-full text-left px-4 py-2 text-sm hover:opacity-80"
          style:color={colors.BUTTON_TEXT}
          onclick={() =>
            handleAction(() => {
              (window as any).__editNodeIndex = nodeIdx;
              (window as any).__newNodePosition = null;
              activeDialog.set("nodeEditor");
            })}
        >
          Edit Node Information
        </button>
        <button
          class="block w-full text-left px-4 py-2 text-sm hover:opacity-80"
          style:color={colors.BUTTON_TEXT}
          onclick={() =>
            handleAction(() =>
              openRemoteDesktop(node.remote_desktop_address)
            )}
        >
          Open Remote Desktop
        </button>
        <button
          class="block w-full text-left px-4 py-2 text-sm hover:opacity-80"
          style:color={colors.BUTTON_TEXT}
          onclick={() =>
            handleAction(() => {
              const ip = Object.values(node.vlans).find((v) => v && v.trim() !== "") ?? "";
              openSSH(ip);
            })}
        >
          Open SSH
        </button>
        <button
          class="block w-full text-left px-4 py-2 text-sm hover:opacity-80"
          style:color={colors.BUTTON_TEXT}
          onclick={() =>
            handleAction(() => openFileExplorer(node.file_path))}
        >
          Open File Explorer
        </button>
        <button
          class="block w-full text-left px-4 py-2 text-sm hover:opacity-80"
          style:color={colors.BUTTON_TEXT}
          onclick={() =>
            handleAction(() =>
              openWebBrowser(node.web_config_url)
            )}
        >
          Open Web Browser
        </button>

        {#if $mode === "Configuration"}
          <div
            class="border-t"
            style:border-color={colors.BORDER_COLOR}
          ></div>
          <button
            class="block w-full text-left px-4 py-2 text-sm hover:opacity-80"
            style:color="#ef4444"
            onclick={() =>
              handleAction(() => removeNode(nodeIdx))}
          >
            Delete Node
          </button>
        {/if}

        <!-- Custom commands -->
        {@const cmds = getApplicableCommands(nodeIdx)}
        {#if cmds.length > 0}
          <div
            class="border-t"
            style:border-color={colors.BORDER_COLOR}
          ></div>
          {#each cmds as cmd}
            <button
              class="block w-full text-left px-4 py-2 text-sm hover:opacity-80"
              style:color={colors.BUTTON_TEXT}
              onclick={() =>
                handleAction(() =>
                  executeCustomCommand(cmd.template, node)
                )}
            >
              {cmd.name}
            </button>
          {/each}
        {/if}
      {/if}
    {:else if $contextMenu.connectionIndex !== null}
      {@const connIdx = $contextMenu.connectionIndex}
      {@const conn = $connections[connIdx]}
      {#if conn}
        <button
          class="block w-full text-left px-4 py-2 text-sm hover:opacity-80"
          style:color={colors.BUTTON_TEXT}
          onclick={() =>
            handleAction(() => {
              (window as any).__editConnectionIndex = connIdx;
              (window as any).__connectionFromIndex = conn.from;
              (window as any).__connectionToIndex = conn.to;
              activeDialog.set("connectionEditor");
            })}
        >
          Edit Connection
        </button>
        {#if $mode === "Configuration"}
          <div
            class="border-t"
            style:border-color={colors.BORDER_COLOR}
          ></div>
          <button
            class="block w-full text-left px-4 py-2 text-sm hover:opacity-80"
            style:color="#ef4444"
            onclick={() =>
              handleAction(() => removeConnection(connIdx))}
          >
            Delete Connection
          </button>
        {/if}
      {/if}
    {:else if (window as any).__contextStickyIndex !== undefined}
      {@const stickyIdx = (window as any).__contextStickyIndex}
      <button
        class="block w-full text-left px-4 py-2 text-sm hover:opacity-80"
        style:color="#ef4444"
        onclick={() =>
          handleAction(() => removeStickyNote(stickyIdx))}
      >
        Delete Sticky Note
      </button>
    {:else if (window as any).__contextGroupIndex !== undefined}
      {@const groupIdx = (window as any).__contextGroupIndex}
      <button
        class="block w-full text-left px-4 py-2 text-sm hover:opacity-80"
        style:color={colors.BUTTON_TEXT}
        onclick={() =>
          handleAction(() => activeDialog.set("groupEditor"))}
      >
        Edit Group Colors
      </button>
      <button
        class="block w-full text-left px-4 py-2 text-sm hover:opacity-80"
        style:color="#ef4444"
        onclick={() =>
          handleAction(() => removeGroup(groupIdx))}
      >
        Delete Group
      </button>
    {:else if (window as any).__contextBgImageIndex !== undefined}
      {@const bgIdx = (window as any).__contextBgImageIndex}
      <button
        class="block w-full text-left px-4 py-2 text-sm hover:opacity-80"
        style:color={colors.BUTTON_TEXT}
        onclick={() =>
          handleAction(() => {
            (window as any).__bgImageOpacityIndex = bgIdx;
            activeDialog.set("bgImageOpacity");
          })}
      >
        Adjust Opacity
      </button>
      <div
        class="border-t"
        style:border-color={colors.BORDER_COLOR}
      ></div>
      <button
        class="block w-full text-left px-4 py-2 text-sm hover:opacity-80"
        style:color="#ef4444"
        onclick={() =>
          handleAction(() => removeBackgroundImage(bgIdx))}
      >
        Delete Image
      </button>
    {/if}
  </div>
{/if}
