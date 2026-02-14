<script lang="ts">
  import { mode, groupsModeActive, currentTheme } from "../../lib/stores/uiStore";
  import { settings } from "../../lib/stores/settingsStore";
  import { effectiveColors } from "../../lib/theme/colors";

  let colors = $derived($effectiveColors);

  // Only show if enabled in settings (default true)
  let visible = $derived($settings.show_canvas_status_bar !== false);

  let interactions = $derived.by(() => {
    const base = [
      "Right-click + drag: Pan",
      "Scroll: Zoom",
    ];

    if ($mode === "Configuration") {
      if ($groupsModeActive) {
        return ["Click + drag: Draw group", "Double-click group name: Rename", ...base];
      } else {
        return ["Double-click: Create node", "Middle-click nodes: Connect", ...base];
      }
    } else {
      return ["Left-click: Ping node", "Right-click: Context menu", ...base];
    }
  });
</script>

{#if visible}
<!--
  <div
    class="canvas-status-bar"
    style:background-color={colors.FRAME_BG}
    style:border="1px solid {colors.BORDER_COLOR}"
  >
    <div class="status-header" style:color={colors.TEXT_PRIMARY}>
      Available Actions:
    </div>
    <div class="status-list">
      {#each interactions as interaction}
        <div
          class="status-item"
          style:color={colors.TEXT_SECONDARY}
        >
          {interaction}
        </div>
      {/each}
    </div>
  </div>
  -->
{/if}

<style>
  .canvas-status-bar {
    position: absolute;
    top: 12px;
    left: 12px;
    padding: 10px 12px;
    font-size: 12px;
    border-radius: 6px;
    z-index: 50;
    backdrop-filter: blur(8px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    min-width: 200px;
    pointer-events: none;
  }

  .status-header {
    font-weight: 600;
    margin-bottom: 6px;
    font-size: 13px;
  }

  .status-list {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .status-item {
    line-height: 1.4;
    padding-left: 8px;
    position: relative;
  }

  .status-item::before {
    content: "•";
    position: absolute;
    left: 0;
    opacity: 0.5;
  }
</style>
