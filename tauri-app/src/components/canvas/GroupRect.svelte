<script lang="ts">
  import type { GroupRect } from "../../lib/types/network";
  import { updateGroup } from "../../lib/stores/networkStore";
  import { mode } from "../../lib/stores/uiStore";

  let {
    group,
    index,
    bgColor,
    borderColor,
    textColor,
    onRightClick,
  }: {
    group: GroupRect;
    index: number;
    bgColor: string;
    borderColor: string;
    textColor: string;
    onRightClick?: (e: MouseEvent, index: number) => void;
  } = $props();

  let w = $derived(Math.abs(group.x2 - group.x1));
  let h = $derived(Math.abs(group.y2 - group.y1));
  let x = $derived(Math.min(group.x1, group.x2));
  let y = $derived(Math.min(group.y1, group.y2));

  function handleTextDblClick(e: MouseEvent) {
    if ($mode !== "Configuration") return;
    e.stopPropagation();

    const newName = prompt("Enter group name:", group.name || "");
    if (newName !== null) {
      updateGroup(index, { name: newName });
    }
  }

  function handleRightClick(e: MouseEvent) {
    if ($mode !== "Configuration") return;
    if (onRightClick) {
      e.preventDefault();
      e.stopPropagation();
      onRightClick(e, index);
    }
  }
</script>

<g data-type="group" data-index={index}>
  <!-- svelte-ignore a11y_no_static_element_interactions -->
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
    style:cursor={$mode === "Configuration" ? "pointer" : "default"}
    oncontextmenu={handleRightClick}
  />
  {#if group.name}
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <text
      x={x + 8}
      y={y + 18}
      fill={textColor}
      font-family="Helvetica, Arial, sans-serif"
      font-size="14"
      font-weight="bold"
      style:cursor={$mode === "Configuration" ? "text" : "default"}
      ondblclick={handleTextDblClick}
      oncontextmenu={handleRightClick}
    >
      {group.name}
    </text>
  {/if}
</g>
