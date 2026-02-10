<script lang="ts">
  let {
    text,
    position = "bottom",
    children,
  }: {
    text: string;
    position?: "top" | "bottom" | "left" | "right";
    children: any;
  } = $props();

  let showTooltip = $state(false);
  let timeoutId: number | undefined;

  function handleMouseEnter() {
    timeoutId = window.setTimeout(() => {
      showTooltip = true;
    }, 500); // 500ms delay before showing
  }

  function handleMouseLeave() {
    if (timeoutId) clearTimeout(timeoutId);
    showTooltip = false;
  }
</script>

<div
  class="tooltip-wrapper"
  onmouseenter={handleMouseEnter}
  onmouseleave={handleMouseLeave}
>
  {@render children()}

  {#if showTooltip}
    <div class="tooltip {position}">
      {text}
    </div>
  {/if}
</div>

<style>
  .tooltip-wrapper {
    position: relative;
    display: inline-block;
  }

  .tooltip {
    position: absolute;
    background: var(--bg-elevated);
    border: 1px solid var(--border-color);
    padding: 6px 10px;
    border-radius: 4px;
    font-size: 13px;
    white-space: nowrap;
    z-index: 10000;
    pointer-events: none;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(8px);
    opacity: 0.98;
  }

  /* Make tooltip background more opaque in both themes */
  :global(.dark) .tooltip,
  :global(.theme-ironclad) .tooltip {
    background: rgba(30, 30, 30, 0.95);
    color: #ffffff;
    border-color: rgba(255, 255, 255, 0.2);
  }

  :global(.light) .tooltip {
    background: rgba(255, 255, 255, 0.95);
    color: #000000;
    border-color: rgba(0, 0, 0, 0.2);
  }

  .tooltip.bottom {
    top: calc(100% + 8px);
    left: 50%;
    transform: translateX(-50%);
  }

  .tooltip.top {
    bottom: calc(100% + 8px);
    left: 50%;
    transform: translateX(-50%);
  }

  .tooltip.right {
    left: calc(100% + 8px);
    top: 50%;
    transform: translateY(-50%);
  }

  .tooltip.left {
    right: calc(100% + 8px);
    top: 50%;
    transform: translateY(-50%);
  }
</style>
