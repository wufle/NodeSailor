<script lang="ts">
  let {
    text,
    position = "right", // Changed default position to right
    children,
  }: {
    text: string;
    position?: "top" | "bottom" | "left" | "right";
    children: any;
  } = $props();

  const verticalOffset = 30; // Pixels to move the tooltip down for 'left' and 'right' positions

  let showTooltip = $state(false);
  let timeoutId: number | undefined;
  let tooltipElement: HTMLDivElement; // Reference to the tooltip div
  let wrapperElement: HTMLDivElement; // Reference to the wrapper div

  function handleMouseEnter() {
    timeoutId = window.setTimeout(() => {
      showTooltip = true;
      // After showing, calculate and adjust position
      requestAnimationFrame(() => {
        if (tooltipElement && wrapperElement) {
          const tooltipRect = tooltipElement.getBoundingClientRect();
          const wrapperRect = wrapperElement.getBoundingClientRect();
          const viewportWidth = window.innerWidth;
          const viewportHeight = window.innerHeight; // Added for vertical clipping check

          // Reset positioning to allow recalculation
          tooltipElement.style.left = '';
          tooltipElement.style.right = '';
          tooltipElement.style.top = '';
          tooltipElement.style.bottom = '';
          tooltipElement.style.transform = '';

          // Apply base positioning
          let finalLeft: string | undefined;
          let finalTop: string | undefined;
          let finalTransform: string | undefined;

          if (position === "right") {
            finalLeft = `${wrapperRect.right + 8}px`;
            finalTop = `${wrapperRect.top + verticalOffset}px`; // Align with the top of the wrapper + offset
            finalTransform = ''; // Remove translateY(-50%)
          } else if (position === "left") {
            finalLeft = `${wrapperRect.left - tooltipRect.width - 8}px`; // Corrected: use tooltipRect.width
            finalTop = `${wrapperRect.top + verticalOffset}px`; // Align with the top of the wrapper + offset
            finalTransform = ''; // Remove translateY(-50%)
          } else if (position === "bottom") {
            finalTop = `${wrapperRect.bottom + 8}px`;
            finalLeft = `${wrapperRect.left + wrapperRect.width / 2}px`;
            finalTransform = `translateX(-50%)`;
          } else if (position === "top") {
            finalTop = `${wrapperRect.top - tooltipRect.height - 8}px`; // Corrected: use tooltipRect.height
            finalLeft = `${wrapperRect.left + wrapperRect.width / 2}px`;
            finalTransform = `translateX(-50%)`;
          }

          // Apply initial calculated styles
          if (finalLeft) tooltipElement.style.left = finalLeft;
          if (finalTop) tooltipElement.style.top = finalTop;
          if (finalTransform) tooltipElement.style.transform = finalTransform;

          // Recalculate tooltip rect after initial positioning
          const adjustedTooltipRect = tooltipElement.getBoundingClientRect();

          // Check for horizontal clipping (for right/left positions)
          if (adjustedTooltipRect.right > viewportWidth) {
            // If it clips on the right, try positioning to the left of the wrapper
            tooltipElement.style.left = `${wrapperRect.left - adjustedTooltipRect.width - 8}px`;
            tooltipElement.style.right = 'auto'; // Clear right in case it was set
            tooltipElement.style.transform = `translateY(-50%)`; // Maintain vertical centering
          } else if (adjustedTooltipRect.left < 0) {
            // If it clips on the left, try positioning to the right of the wrapper
            tooltipElement.style.left = `${wrapperRect.right + 8}px`;
            tooltipElement.style.right = 'auto';
            tooltipElement.style.transform = `translateY(-50%)`;
          }

          // Check for vertical clipping (for top/bottom positions or if horizontal shift caused vertical clip)
          if (adjustedTooltipRect.bottom > viewportHeight) {
            // If it clips on the bottom, position it above the wrapper
            tooltipElement.style.top = `${wrapperRect.top - adjustedTooltipRect.height - 8}px`;
            tooltipElement.style.bottom = 'auto';
            if (position === 'bottom' || position === 'top') {
              tooltipElement.style.transform = `translateX(-50%)`; // Maintain horizontal centering
            }
          } else if (adjustedTooltipRect.top < 0) {
            // If it clips on the top, position it below the wrapper
            tooltipElement.style.top = `${wrapperRect.bottom + 8}px`;
            tooltipElement.style.bottom = 'auto';
            if (position === 'bottom' || position === 'top') {
              tooltipElement.style.transform = `translateX(-50%)`; // Maintain horizontal centering
            }
          }
        }
      });
    }, 500); // 500ms delay before showing
  }

  function handleMouseLeave() {
    if (timeoutId) clearTimeout(timeoutId);
    showTooltip = false;
  }
</script>

<div
  bind:this={wrapperElement}
  class="tooltip-wrapper"
  onmouseenter={handleMouseEnter}
  onmouseleave={handleMouseLeave}
>
  {@render children()}

  {#if showTooltip}
    <div bind:this={tooltipElement} class="tooltip"> <!-- Removed {position} class -->
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
    position: fixed; /* Changed to fixed for viewport-relative positioning */
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

  /* Removed static position classes, as positioning will be dynamic via JS */
</style>
