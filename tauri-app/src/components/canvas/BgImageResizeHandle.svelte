<script lang="ts">
  import { updateBackgroundImage } from "../../lib/stores/networkStore";
  import { mode } from "../../lib/stores/uiStore";
  import { unsavedChanges } from "../../lib/stores/uiStore";
  import type { BackgroundImage } from "../../lib/types/network";

  let {
    image,
    imageIndex,
    corner,
  }: {
    image: BackgroundImage;
    imageIndex: number;
    corner: "tl" | "tr" | "bl" | "br";
  } = $props();

  let cx = $derived(
    corner === "tl" || corner === "bl" ? image.x : image.x + image.width
  );
  let cy = $derived(
    corner === "tl" || corner === "tr" ? image.y : image.y + image.height
  );

  let isDragging = $state(false);

  function onMouseDown(e: MouseEvent) {
    if ($mode !== "Configuration") return;
    if (e.button !== 0) return;

    e.stopPropagation();
    isDragging = true;

    const startX = e.clientX;
    const startY = e.clientY;
    const origX = image.x;
    const origY = image.y;
    const origW = image.width;
    const origH = image.height;
    const aspectRatio = origW / origH;

    const onMove = (me: MouseEvent) => {
      if (!isDragging) return;

      const svgEl = (e.target as SVGElement).closest("svg");
      if (!svgEl) return;
      const transform = svgEl.querySelector("#world");
      const zoomMatch = transform
        ?.getAttribute("transform")
        ?.match(/scale\(([^)]+)\)/);
      const currentZoom = zoomMatch ? parseFloat(zoomMatch[1]) : 1;

      const dx = (me.clientX - startX) / currentZoom;
      const dy = (me.clientY - startY) / currentZoom;

      let newX = origX;
      let newY = origY;
      let newW = origW;
      let newH = origH;

      if (corner === "br") {
        newW = Math.max(20, origW + dx);
        newH = Math.max(20, origH + dy);
      } else if (corner === "bl") {
        newW = Math.max(20, origW - dx);
        newH = Math.max(20, origH + dy);
        newX = origX + origW - newW;
      } else if (corner === "tr") {
        newW = Math.max(20, origW + dx);
        newH = Math.max(20, origH - dy);
        newY = origY + origH - newH;
      } else if (corner === "tl") {
        newW = Math.max(20, origW - dx);
        newH = Math.max(20, origH - dy);
        newX = origX + origW - newW;
        newY = origY + origH - newH;
      }

      // Shift key locks aspect ratio
      if (me.shiftKey) {
        if (corner === "br" || corner === "tl") {
          newH = newW / aspectRatio;
          if (corner === "tl") {
            newY = origY + origH - newH;
          }
        } else {
          newW = newH * aspectRatio;
          if (corner === "bl") {
            newX = origX + origW - newW;
          }
        }
      }

      updateBackgroundImage(imageIndex, {
        x: newX,
        y: newY,
        width: newW,
        height: newH,
      });
    };

    const onUp = () => {
      isDragging = false;
      unsavedChanges.set(true);
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
    };

    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
  }
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<circle
  cx={cx}
  cy={cy}
  r="6"
  fill="#2196F3"
  stroke="#1565C0"
  stroke-width="2"
  style:cursor={corner === "tl" || corner === "br" ? "nwse-resize" : "nesw-resize"}
  onmousedown={onMouseDown}
  oncontextmenu={(e) => e.preventDefault()}
/>
