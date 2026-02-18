<script lang="ts">
  import type { BackgroundImage } from "../../lib/types/network";
  import { mode } from "../../lib/stores/uiStore";

  let {
    image,
    index,
    onMouseDown,
    onRightClick,
  }: {
    image: BackgroundImage;
    index: number;
    onMouseDown: (e: MouseEvent) => void;
    onRightClick: (e: MouseEvent) => void;
  } = $props();

  function handleContextMenu(e: MouseEvent) {
    if ($mode !== "Configuration") return;
    e.preventDefault();
    e.stopPropagation();
    onRightClick(e);
  }
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<g data-type="bgimage" data-index={index}>
  <image
    href={image.dataUrl}
    x={image.x}
    y={image.y}
    width={image.width}
    height={image.height}
    opacity={image.opacity}
    preserveAspectRatio="none"
    style:cursor={$mode === "Configuration" ? "move" : "default"}
    onmousedown={onMouseDown}
    oncontextmenu={handleContextMenu}
  />
</g>
