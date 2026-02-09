<script lang="ts">
  import { connections } from "../../lib/stores/networkStore";
  import { mode, unsavedChanges } from "../../lib/stores/uiStore";

  let {
    x,
    y,
    connectionIndex,
    waypointIndex,
  }: {
    x: number;
    y: number;
    connectionIndex: number;
    waypointIndex: number;
  } = $props();

  let isDragging = $state(false);
  let startX = 0;
  let startY = 0;
  let origX = 0;
  let origY = 0;

  function onMouseDown(e: MouseEvent) {
    if ($mode !== "Configuration") return;

    if (e.button === 2) {
      // Right-click: remove waypoint
      e.preventDefault();
      e.stopPropagation();
      connections.update((c) => {
        const copy = [...c];
        const conn = { ...copy[connectionIndex] };
        const wps = [...(conn.waypoints ?? [])];
        wps.splice(waypointIndex, 1);
        conn.waypoints = wps.length > 0 ? wps : undefined;
        copy[connectionIndex] = conn;
        return copy;
      });
      unsavedChanges.set(true);
      return;
    }

    if (e.button === 0) {
      e.stopPropagation();
      isDragging = true;
      origX = x;
      origY = y;
      startX = e.clientX;
      startY = e.clientY;

      const onMove = (me: MouseEvent) => {
        if (!isDragging) return;
        // Get the SVG element to compute scale
        const svgEl = (e.target as SVGElement).closest("svg");
        if (!svgEl) return;
        const rect = svgEl.getBoundingClientRect();
        // We need to account for zoom
        const transform = svgEl.querySelector("#world");
        const zoomMatch = transform
          ?.getAttribute("transform")
          ?.match(/scale\(([^)]+)\)/);
        const currentZoom = zoomMatch
          ? parseFloat(zoomMatch[1])
          : 1;

        const dx = (me.clientX - startX) / currentZoom;
        const dy = (me.clientY - startY) / currentZoom;

        connections.update((c) => {
          const copy = [...c];
          const conn = { ...copy[connectionIndex] };
          const wps = [...(conn.waypoints ?? [])];
          wps[waypointIndex] = [origX + dx, origY + dy];
          conn.waypoints = wps;
          copy[connectionIndex] = conn;
          return copy;
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
  }
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<circle
  cx={x}
  cy={y}
  r="5"
  fill="#FFD700"
  stroke="#333"
  stroke-width="1"
  style:cursor="move"
  onmousedown={onMouseDown}
  oncontextmenu={(e) => e.preventDefault()}
/>
