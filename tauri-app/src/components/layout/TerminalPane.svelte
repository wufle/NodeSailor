<script lang="ts">
  import { currentTheme } from "../../lib/stores/uiStore";
  import { effectiveColors } from "../../lib/theme/colors";
  import { matrixMode } from "../../lib/stores/matrixStore";
  import {
    terminalEntries,
    terminalVisible,
    terminalHeight,
    clearTerminal,
  } from "../../lib/stores/terminalStore";
  import type { TerminalEntryType } from "../../lib/stores/terminalStore";

  let colors = $derived($effectiveColors);
  let isIronclad = $derived($currentTheme === "ironclad");
  let isMatrix = $derived($matrixMode);
  let isDarkOrIronclad = $derived($currentTheme === "dark" || $currentTheme === "ironclad" || isMatrix);

  let scrollContainer: HTMLDivElement | undefined = $state(undefined);
  let userScrolledUp = $state(false);
  let isResizing = $state(false);

  const HEADER_HEIGHT = 28;
  const MIN_HEIGHT = 100;
  const MAX_HEIGHT = 600;

  function formatTime(date: Date): string {
    return date.toLocaleTimeString("en-US", {
      hour12: false,
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  }

  function getTypeColor(type: TerminalEntryType): string {
    if (isMatrix) {
      return type === "error" ? "#ff0000" : "#00ff00";
    }
    switch (type) {
      case "ping":
        return "#e5c07b";
      case "ping-result":
        return "#98c379";
      case "system":
        return "#61afef";
      case "custom":
        return "#c678dd";
      case "info":
        return "#56b6c2";
      case "error":
        return "#e06c75";
      default:
        return "#abb2bf";
    }
  }

  function getResultColor(result?: string): string {
    if (isMatrix) {
      if (result === "Failed") return "#ff0000";
      return "#00ff00";
    }
    if (!result) return "#abb2bf";
    if (result === "Success") return "#98c379";
    if (result === "Failed") return "#e06c75";
    return "#abb2bf";
  }

  function handleScroll() {
    if (!scrollContainer) return;
    const { scrollTop, scrollHeight, clientHeight } = scrollContainer;
    userScrolledUp = scrollHeight - scrollTop - clientHeight > 40;
  }

  function scrollToBottom() {
    if (scrollContainer) {
      scrollContainer.scrollTop = scrollContainer.scrollHeight;
      userScrolledUp = false;
    }
  }

  // Auto-scroll when new entries arrive (unless user scrolled up)
  $effect(() => {
    const _entries = $terminalEntries;
    if (!userScrolledUp && scrollContainer) {
      // Use tick to wait for DOM update
      requestAnimationFrame(() => {
        if (scrollContainer) {
          scrollContainer.scrollTop = scrollContainer.scrollHeight;
        }
      });
    }
  });

  // Resize handling
  function startResize(e: MouseEvent) {
    e.preventDefault();
    isResizing = true;
    const startY = e.clientY;
    const startHeight = $terminalHeight;

    function onMouseMove(e: MouseEvent) {
      const delta = startY - e.clientY;
      const newHeight = Math.min(MAX_HEIGHT, Math.max(MIN_HEIGHT, startHeight + delta));
      terminalHeight.set(newHeight);
    }

    function onMouseUp() {
      isResizing = false;
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("mouseup", onMouseUp);
    }

    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", onMouseUp);
  }

  function toggleCollapse() {
    terminalVisible.update((v) => !v);
  }
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
  class="flex flex-col {isIronclad ? 'ironclad-terminal' : ''}"
  style:border-top={isIronclad ? undefined : `1px solid ${colors.BORDER_COLOR}`}
>
  <!-- Resize handle (only when expanded) -->
  {#if $terminalVisible}
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div
      class="h-1 cursor-ns-resize shrink-0"
      style:background-color={isIronclad ? "transparent" : colors.BORDER_COLOR}
      onmousedown={startResize}
    ></div>
  {/if}

  <!-- Header -->
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div
    class="flex items-center justify-between px-3 shrink-0 cursor-pointer select-none {isIronclad ? 'terminal-header' : ''}"
    style:height="{HEADER_HEIGHT}px"
    style:background-color={isIronclad ? undefined : colors.HEADER_BG}
    style:color={colors.HEADER_TEXT}
    onclick={toggleCollapse}
  >
    <div class="flex items-center gap-2 text-xs font-medium">
      <span class="opacity-60">{$terminalVisible ? "\u25BC" : "\u25B6"}</span>
      <span>Terminal</span>
      {#if $terminalEntries.length > 0}
        <span class="opacity-50">({$terminalEntries.length})</span>
      {/if}
    </div>
    <div class="flex items-center gap-2">
      {#if userScrolledUp && $terminalVisible}
        <button
          class="text-xs px-1.5 py-0.5 rounded opacity-70 hover:opacity-100 transition-opacity"
          style:background-color={colors.BUTTON_BG}
          style:color={colors.BUTTON_TEXT}
          onclick={(e: MouseEvent) => { e.stopPropagation(); scrollToBottom(); }}
        >
          Scroll to bottom
        </button>
      {/if}
      {#if $terminalEntries.length > 0}
        <button
          class="text-xs px-1.5 py-0.5 rounded opacity-70 hover:opacity-100 transition-opacity"
          style:background-color={colors.BUTTON_BG}
          style:color={colors.BUTTON_TEXT}
          onclick={(e: MouseEvent) => { e.stopPropagation(); clearTerminal(); }}
        >
          Clear
        </button>
      {/if}
    </div>
  </div>

  <!-- Body -->
  {#if $terminalVisible}
    <div
      bind:this={scrollContainer}
      class="overflow-y-auto overflow-x-hidden terminal-pane-body {isIronclad ? 'terminal-body' : ''}"
      style:height="{$terminalHeight}px"
      style:background-color={isIronclad ? undefined : (isMatrix ? "#000000" : (isDarkOrIronclad ? "#0d1117" : "#fafafa"))}
      style:font-family="'Consolas', 'Courier New', monospace"
      style:font-size="12px"
      style:line-height="1.5"
      onscroll={handleScroll}
    >
      {#if $terminalEntries.length === 0}
        <div class="flex items-center justify-center h-full opacity-40" style:color={colors.INFO_TEXT}>
          Commands will appear here as they are executed...
        </div>
      {:else}
        <div class="px-2 py-1">
          {#each $terminalEntries as entry (entry.id)}
            <div class="py-0.5">
              <span class="opacity-40" style:color={isMatrix ? "#005500" : (isDarkOrIronclad ? "#636d83" : "#999999")}>
                [{formatTime(entry.timestamp)}]
              </span>
              {" "}
              <span style:color={getTypeColor(entry.type)}>
                {entry.command}
              </span>
              {#if entry.result}
                {" "}
                <span style:color={getResultColor(entry.result)}>
                  [{entry.result}]
                </span>
              {/if}
              <div class="pl-6 opacity-60 italic text-[11px]" style:color={isMatrix ? "#007700" : (isDarkOrIronclad ? "#7a8394" : "#888888")}>
                {entry.description}
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  {/if}
</div>
