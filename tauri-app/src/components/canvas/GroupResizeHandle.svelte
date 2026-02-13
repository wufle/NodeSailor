<script lang="ts">
  import { updateGroup } from "../../lib/stores/networkStore";
  import { mode, unsavedChanges } from "../../lib/stores/uiStore";
  import type { GroupRect } from "../../lib/types/network";

  let {
    group,
    groupIndex,
    corner,
  }: {
    group: GroupRect;
    groupIndex: number;
    corner: "tl" | "tr" | "bl" | "br";
  } = $props();

  let x = $derived(
    corner === "tl" || corner === "bl"
      ? Math.min(group.x1, group.x2)
      : Math.max(group.x1, group.x2)
  );
  let y = $derived(
    corner === "tl" || corner === "tr"
      ? Math.min(group.y1, group.y2)
      : Math.max(group.y1, group.y2)
  );

  let isDragging = $state(false);

  function onMouseDown(e: MouseEvent) {
    if ($mode !== "Configuration") return;
    if (e.button !== 0) return;

    e.stopPropagation();
    isDragging = true;

    const startX = e.clientX;
    const startY = e.clientY;
    const origX1 = group.x1;
    const origY1 = group.y1;
    const origX2 = group.x2;
    const origY2 = group.y2;

    const onMove = (me: MouseEvent) => {
      if (!isDragging) return;

      // Get zoom level
      const svgEl = (e.target as SVGElement).closest("svg");
      if (!svgEl) return;
      const transform = svgEl.querySelector("#world");
      const zoomMatch = transform
        ?.getAttribute("transform")
        ?.match(/scale\(([^)]+)\)/);
      const currentZoom = zoomMatch ? parseFloat(zoomMatch[1]) : 1;

      const dx = (me.clientX - startX) / currentZoom;
      const dy = (me.clientY - startY) / currentZoom;

      let newX1 = origX1;
      let newY1 = origY1;
      let newX2 = origX2;
      let newY2 = origY2;

      // Update coordinates based on corner
      if (corner === "tl") {
        newX1 = origX1 + dx;
        newY1 = origY1 + dy;
      } else if (corner === "tr") {
        newX2 = origX2 + dx;
        newY1 = origY1 + dy;
      } else if (corner === "bl") {
        newX1 = origX1 + dx;
        newY2 = origY2 + dy;
      } else if (corner === "br") {
        newX2 = origX2 + dx;
        newY2 = origY2 + dy;
      }

      updateGroup(groupIndex, {
        x1: newX1,
        y1: newY1,
        x2: newX2,
        y2: newY2,
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
  cx={x}
  cy={y}
  r="6"
  fill="#4CAF50"
  stroke="#2E7D32"
  stroke-width="2"
  style:cursor={corner === "tl" || corner === "br" ? "nwse-resize" : "nesw-resize"}
  onmousedown={onMouseDown}
  oncontextmenu={(e) => e.preventDefault()}
/>
