<script lang="ts">
  import type { NetworkNode } from "../../lib/types/network";
  import { currentTheme } from "../../lib/stores/uiStore";
  import { hostNodeIndices, pingAnimationStates } from "../../lib/stores/networkStore";
  import squaredMetalUrl from "../../assets/textures/squared-metal.png";

  let {
    node,
    index,
    fillColor,
    outlineColor,
    outlineWidth,
    textColor,
    fontSize,
    onMouseDown,
    onMouseEnter,
    onMouseLeave,
    pingAnimationState = null,
  }: {
    node: NetworkNode;
    index: number;
    fillColor: string;
    outlineColor: string;
    outlineWidth: number;
    textColor: string;
    fontSize: number;
    onMouseDown: (e: MouseEvent) => void;
    onMouseEnter?: () => void;
    onMouseLeave?: () => void;
    pingAnimationState?: 'success' | 'failure' | null;
  } = $props();

  let isIronclad = $derived($currentTheme === "ironclad");
  let isHostNode = $derived($hostNodeIndices.has(index));
  let hasPingSuccess = $derived(pingAnimationState === 'success');
  let hasPingFailure = $derived(pingAnimationState === 'failure');

  // Auto-clear animation state after CSS animation completes
  $effect(() => {
    if (pingAnimationState) {
      const duration = pingAnimationState === 'success' ? 600 : 800;
      const timeoutId = setTimeout(() => {
        pingAnimationStates.update((s) => {
          const copy = { ...s };
          delete copy[index];
          return copy;
        });
      }, duration);
      return () => clearTimeout(timeoutId);
    }
  });

  // Approximate text width for sizing the rectangle
  let textEl: SVGTextElement;
  let textWidth = $state(30);
  let textHeight = $state(16);

  $effect(() => {
    if (textEl) {
      // Force re-measure when name or fontSize changes
      const _ = node.name;
      const __ = fontSize;
      requestAnimationFrame(() => {
        if (textEl) {
          try {
            const bbox = textEl.getBBox();
            textWidth = bbox.width;
            textHeight = bbox.height;
          } catch {
            // getBBox can fail if element is not rendered
          }
        }
      });
    }
  });

  let pad = $derived(Math.max(2, Math.round(fontSize * 0.3)));
  let halfW = $derived(textWidth / 2 + pad);
  let halfH = $derived(textHeight / 2 + pad);
</script>

<style>
  @keyframes strobe-pulse {
    0% {
      filter: drop-shadow(0 0 8px rgba(255, 255, 0, 0.2)); /* Initial faint glow */
    }
    16.67% { /* Peak of first strobe */
      filter: drop-shadow(0 0 16px rgba(255, 255, 0, 0.8));
    }
    33.33% { /* Return to faint glow */
      filter: drop-shadow(0 0 8px rgba(255, 255, 0, 0.2));
    }
    50% { /* Peak of second strobe */
      filter: drop-shadow(0 0 16px rgba(255, 255, 0, 0.8));
    }
    66.67% { /* Return to faint glow */
      filter: drop-shadow(0 0 8px rgba(255, 255, 0, 0.2));
    }
    83.33% { /* Peak of third strobe */
      filter: drop-shadow(0 0 16px rgba(255, 255, 0, 0.8));
    }
    100% { /* Final sustained light glow */
      filter: drop-shadow(0 0 8px rgba(255, 255, 0, 0.5));
    }
  }

  .strobe-effect {
    animation: strobe-pulse 6s ease-out forwards;
  }

  @keyframes ping-success-strobe {
    0% {
      filter: drop-shadow(0 0 0px rgba(39, 174, 96, 0));
    }
    20% {
      filter: drop-shadow(0 0 20px rgba(39, 174, 96, 0.9));
    }
    100% {
      filter: drop-shadow(0 0 0px rgba(39, 174, 96, 0));
    }
  }

  @keyframes ping-failure-strobe {
    0% {
      filter: drop-shadow(0 0 0px rgba(231, 76, 60, 0));
    }
    50% {
      filter: drop-shadow(0 0 20px rgba(231, 76, 60, 0.9));
    }
    100% {
      filter: drop-shadow(0 0 0px rgba(231, 76, 60, 0));
    }
  }

  .ping-success-effect {
    animation: ping-success-strobe 0.6s ease-out forwards;
  }

  .ping-failure-effect {
    animation: ping-failure-strobe 0.8s ease-out forwards;
  }
</style>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<g
  data-type="node"
  data-index={index}
  class:strobe-effect={isHostNode}
  class:ping-success-effect={hasPingSuccess}
  class:ping-failure-effect={hasPingFailure}
  style:cursor="pointer"
  onmousedown={onMouseDown}
  onmouseenter={onMouseEnter}
  onmouseleave={onMouseLeave}
>
  {#if isIronclad}
    <defs>
      <pattern id="node-texture-{index}" patternUnits="userSpaceOnUse" width="132" height="132">
        <image href={squaredMetalUrl} width="132" height="132" opacity="0.12" />
      </pattern>
    </defs>
  {/if}
  <!-- Main node rect -->
  <rect
    x={node.x - halfW}
    y={node.y - halfH}
    width={halfW * 2}
    height={halfH * 2}
    fill={fillColor}
    stroke={outlineColor}
    stroke-width={isIronclad ? Math.max(outlineWidth, 2) : outlineWidth}
    rx={isIronclad ? 3 : 2}
  />
  {#if isIronclad}
    <!-- Texture overlay on node -->
    <rect
      x={node.x - halfW}
      y={node.y - halfH}
      width={halfW * 2}
      height={halfH * 2}
      fill="url(#node-texture-{index})"
      stroke="none"
      rx="3"
      pointer-events="none"
    />
    <!-- Top highlight edge -->
    <line
      x1={node.x - halfW + 3}
      y1={node.y - halfH + 1}
      x2={node.x + halfW - 3}
      y2={node.y - halfH + 1}
      stroke="rgba(255,255,255,0.15)"
      stroke-width="1"
      pointer-events="none"
    />
    <!-- Bottom shadow edge -->
    <line
      x1={node.x - halfW + 3}
      y1={node.y + halfH - 1}
      x2={node.x + halfW - 3}
      y2={node.y + halfH - 1}
      stroke="rgba(0,0,0,0.4)"
      stroke-width="1"
      pointer-events="none"
    />
  {/if}
  <text
    bind:this={textEl}
    x={node.x}
    y={node.y}
    text-anchor="middle"
    dominant-baseline="central"
    fill={textColor}
    font-family={isIronclad ? "DM Sans, Helvetica, Arial, sans-serif" : "Helvetica, Arial, sans-serif"}
    font-size={fontSize}
    font-weight={isIronclad ? "500" : "normal"}
    pointer-events="none"
  >
    {node.name}
  </text>
</g>
