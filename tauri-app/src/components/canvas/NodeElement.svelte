<script lang="ts">
  import type { NetworkNode } from "../../lib/types/network";
  import { currentTheme } from "../../lib/stores/uiStore";

  let {
    node,
    index,
    fillColor,
    outlineColor,
    outlineWidth,
    textColor,
    fontSize,
    onMouseDown,
  }: {
    node: NetworkNode;
    index: number;
    fillColor: string;
    outlineColor: string;
    outlineWidth: number;
    textColor: string;
    fontSize: number;
    onMouseDown: (e: MouseEvent) => void;
  } = $props();

  let isIronclad = $derived($currentTheme === "ironclad");

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

<!-- svelte-ignore a11y_no_static_element_interactions -->
<g
  data-type="node"
  data-index={index}
  style:cursor="pointer"
  onmousedown={onMouseDown}
>
  <rect
    x={node.x - halfW}
    y={node.y - halfH}
    width={halfW * 2}
    height={halfH * 2}
    fill={fillColor}
    stroke={outlineColor}
    stroke-width={outlineWidth}
    rx="2"
  />
  <text
    bind:this={textEl}
    x={node.x}
    y={node.y}
    text-anchor="middle"
    dominant-baseline="central"
    fill={textColor}
    font-family={isIronclad ? "DM Sans, Helvetica, Arial, sans-serif" : "Helvetica, Arial, sans-serif"}
    font-size={fontSize}
    pointer-events="none"
  >
    {node.name}
  </text>
</g>
