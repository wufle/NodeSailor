<script lang="ts">
  import type { NetworkConnection, NetworkNode } from "../../lib/types/network";
  import {
    buildPolylinePoints,
    interpolatePolyline,
  } from "../../lib/utils/geometry";

  let {
    connection,
    index,
    fromNode,
    toNode,
    lineColor,
    textColor,
    labelBgColor,
    showLabels,
    showLine = true,
    showHandles,
    onMiddleClick,
    onRightClick,
  }: {
    connection: NetworkConnection;
    index: number;
    fromNode: NetworkNode;
    toNode: NetworkNode;
    lineColor: string;
    textColor: string;
    labelBgColor: string;
    showLabels: boolean;
    showLine?: boolean;
    showHandles: boolean;
    onMiddleClick: (e: MouseEvent) => void;
    onRightClick: (e: MouseEvent) => void;
  } = $props();

  let polyPoints = $derived(
    buildPolylinePoints(
      fromNode.x,
      fromNode.y,
      toNode.x,
      toNode.y,
      connection.waypoints
    )
  );

  let pointsStr = $derived(
    polyPoints.map(([x, y]) => `${x},${y}`).join(" ")
  );

  let labelPos = $derived(connection.label_pos ?? 0.5);
  let labelXY = $derived(interpolatePolyline(polyPoints, labelPos));

  let labelTextEl: SVGTextElement;
  let labelWidth = $state(0);
  let labelHeight = $state(0);

  $effect(() => {
    if (labelTextEl && connection.label) {
      requestAnimationFrame(() => {
        if (labelTextEl) {
          try {
            const bbox = labelTextEl.getBBox();
            labelWidth = bbox.width;
            labelHeight = bbox.height;
          } catch {}
        }
      });
    }
  });
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<g data-type="connection" data-index={index}>
  {#if connection.connectioninfo}
    <title>{connection.connectioninfo}</title>
  {/if}
  {#if showLine}
    <!-- Hit area (wider invisible line for easier clicking) -->
    <polyline
      points={pointsStr}
      fill="none"
      stroke="transparent"
      stroke-width="10"
      style:cursor="pointer"
      onmousedown={onMiddleClick}
      oncontextmenu={(e) => {
        e.preventDefault();
        onRightClick(e);
      }}
    />
    <!-- Visible line -->
    <polyline
      points={pointsStr}
      fill="none"
      stroke={lineColor}
      stroke-width="2"
      pointer-events="none"
    />
  {/if}

  <!-- Label -->
  {#if showLabels && connection.label && connection.label.trim()}
    <!-- Label background -->
    <rect
      x={labelXY.x - labelWidth / 2 - 2}
      y={labelXY.y - labelHeight / 2 - 2}
      width={labelWidth + 4}
      height={labelHeight + 4}
      fill={labelBgColor}
      rx="2"
      pointer-events="none"
    />
    <text
      bind:this={labelTextEl}
      x={labelXY.x}
      y={labelXY.y}
      text-anchor="middle"
      dominant-baseline="central"
      fill={textColor}
      font-family="Helvetica, Arial, sans-serif"
      font-size="12"
      style:cursor="pointer"
      oncontextmenu={(e) => {
        e.preventDefault();
        onRightClick(e);
      }}
    >
      {connection.label}
    </text>
  {/if}
</g>
