<script lang="ts">
  import type { StickyNote } from "../../lib/types/network";

  let {
    note,
    index,
    textColor,
    bgColor,
    onMouseDown,
  }: {
    note: StickyNote;
    index: number;
    textColor: string;
    bgColor: string;
    onMouseDown: (e: MouseEvent) => void;
  } = $props();

  let textEl: SVGTextElement;
  let textWidth = $state(30);
  let textHeight = $state(14);

  $effect(() => {
    if (textEl) {
      const _ = note.text;
      requestAnimationFrame(() => {
        if (textEl) {
          try {
            const bbox = textEl.getBBox();
            textWidth = bbox.width;
            textHeight = bbox.height;
          } catch {}
        }
      });
    }
  });
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<g
  data-type="sticky"
  data-index={index}
  style:cursor="move"
  onmousedown={onMouseDown}
>
  <rect
    x={note.x - 4}
    y={note.y - textHeight / 2 - 4}
    width={textWidth + 8}
    height={textHeight + 8}
    fill={bgColor}
    stroke={bgColor}
    rx="3"
    class="sticky_bg"
  />
  <text
    bind:this={textEl}
    x={note.x}
    y={note.y}
    dominant-baseline="central"
    fill={textColor}
    font-family="Helvetica, Arial, sans-serif"
    font-size="12"
    pointer-events="none"
    class="sticky_note"
  >
    {note.text}
  </text>
</g>
