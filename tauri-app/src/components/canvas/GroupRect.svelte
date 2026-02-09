<script lang="ts">
  import type { GroupRect } from "../../lib/types/network";

  let {
    group,
    index,
    bgColor,
    borderColor,
    textColor,
  }: {
    group: GroupRect;
    index: number;
    bgColor: string;
    borderColor: string;
    textColor: string;
  } = $props();

  let w = $derived(Math.abs(group.x2 - group.x1));
  let h = $derived(Math.abs(group.y2 - group.y1));
  let x = $derived(Math.min(group.x1, group.x2));
  let y = $derived(Math.min(group.y1, group.y2));
</script>

<g data-type="group" data-index={index}>
  <rect
    {x}
    {y}
    width={w}
    height={h}
    fill={bgColor}
    fill-opacity="0.5"
    stroke={borderColor}
    stroke-width="2"
    rx="4"
  />
  {#if group.name}
    <text
      x={x + 8}
      y={y + 18}
      fill={textColor}
      font-family="Helvetica, Arial, sans-serif"
      font-size="14"
      font-weight="bold"
      pointer-events="none"
    >
      {group.name}
    </text>
  {/if}
</g>
