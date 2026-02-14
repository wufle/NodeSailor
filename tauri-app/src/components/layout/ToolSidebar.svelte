<script lang="ts">
  import {
    mode,
    activeTool,
    connectionStartNodeIndex,
    currentTheme,
  } from "../../lib/stores/uiStore";
  import { nodes } from "../../lib/stores/networkStore";
  import { effectiveColors } from "../../lib/theme/colors";
  import type { ActiveTool } from "../../lib/stores/uiStore";
  import TooltipWrapper from "../common/TooltipWrapper.svelte";

  let colors = $derived($effectiveColors);
  let isIronclad = $derived($currentTheme === "ironclad");

  const tools: { id: ActiveTool; label: string; shortcut: string; tooltip: string }[] = [
    { id: "select", label: "Select", shortcut: "V", tooltip: "Select / Move (V)" },
    { id: "addNode", label: "Add Node", shortcut: "N", tooltip: "Add Node (N)" },
    { id: "connect", label: "Connect", shortcut: "C", tooltip: "Connect Nodes (C)" },
    { id: "addNote", label: "Add Note", shortcut: "T", tooltip: "Add Sticky Note (T)" },
  ];

  // SVG icon paths for each tool
  function getIcon(id: ActiveTool): string {
    switch (id) {
      case "select":
        // Cursor/arrow icon
        return "M4 2 L4 18 L9 13 L14 18 L16 16 L11 11 L16 11 Z";
      case "addNode":
        // Plus icon
        return "M10 3 L10 17 M3 10 L17 10";
      case "connect":
        // Line with dots icon
        return "M4 16 L16 4";
      case "addNote":
        // Note/document icon
        return "M5 3 L15 3 L15 17 L5 17 Z M7 7 L13 7 M7 10 L13 10 M7 13 L11 13";
    }
  }

  function isStroke(id: ActiveTool): boolean {
    return id !== "select";
  }

  // Connection status indicator
  let connectingFromName = $derived.by(() => {
    if ($activeTool !== "connect" || $connectionStartNodeIndex === null) return null;
    const node = $nodes[$connectionStartNodeIndex];
    return node?.name ?? `Node ${$connectionStartNodeIndex}`;
  });

  function selectTool(id: ActiveTool) {
    activeTool.set(id);
    if (id !== "connect") {
      connectionStartNodeIndex.set(null);
    }
  }
</script>

{#if $mode === "Configuration"}
  <div
    class="absolute left-0 top-0 z-10 flex flex-col gap-1 p-1 {isIronclad ? 'ironclad-toolbar' : ''}"
    style:background-color={isIronclad ? undefined : colors.FRAME_BG}
    style:border-right={isIronclad ? undefined : `1px solid ${colors.BORDER_COLOR}`}
    style:border-bottom={isIronclad ? undefined : `1px solid ${colors.BORDER_COLOR}`}
    style:border-bottom-right-radius="6px"
  >
    {#each tools as tool}
      <TooltipWrapper text={tool.tooltip} position="right">
        <button
          class="w-9 h-9 flex items-center justify-center rounded transition-colors {isIronclad ? 'ironclad-btn' : ''}"
          style:background-color={$activeTool === tool.id ? colors.BUTTON_ACTIVE_BG : colors.BUTTON_BG}
          style:color={$activeTool === tool.id ? colors.BUTTON_ACTIVE_TEXT : colors.BUTTON_TEXT}
          onclick={() => selectTool(tool.id)}
        >
          <svg width="20" height="20" viewBox="0 0 20 20">
            <path
              d={getIcon(tool.id)}
              fill={isStroke(tool.id) ? "none" : "currentColor"}
              stroke={isStroke(tool.id) ? "currentColor" : "none"}
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
            {#if tool.id === "connect"}
              <!-- Dots at endpoints -->
              <circle cx="4" cy="16" r="2.5" fill="currentColor" />
              <circle cx="16" cy="4" r="2.5" fill="currentColor" />
            {/if}
          </svg>
        </button>
      </TooltipWrapper>
    {/each}

    <!-- Connection status indicator -->
    {#if connectingFromName}
      <div
        class="text-xs px-1 py-0.5 text-center rounded mt-1 max-w-[80px] truncate"
        style:background-color={colors.BUTTON_ACTIVE_BG}
        style:color={colors.BUTTON_ACTIVE_TEXT}
        title="Connecting from {connectingFromName} — click another node to complete"
      >
        From: {connectingFromName}
      </div>
    {/if}
  </div>
{/if}
