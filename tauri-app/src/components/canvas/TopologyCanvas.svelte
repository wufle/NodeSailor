<script lang="ts">
  import { onMount } from "svelte";
  import {
    zoom,
    panX,
    panY,
    mode,
    isDark,
    currentTheme,
    selectedNodeIndex,
    previousSelectedNodeIndex,
    groupsModeActive,
    connectionStartNodeIndex,
    contextMenu,
    unsavedChanges,
    activeDialog,
  } from "../../lib/stores/uiStore";
  import {
    nodes,
    connections,
    stickyNotes,
    groups,
    displayOptions,
    addNode,
    moveNode,
    addStickyNote,
    addConnection,
    removeConnection,
    addGroup,
    pingResults,
  } from "../../lib/stores/networkStore";
  import { getThemeColors } from "../../lib/theme/colors";
  import { getGroupColors } from "../../lib/theme/presets";
  import { groupColorPresets } from "../../lib/stores/networkStore";
  import {
    buildPolylinePoints,
    interpolatePolyline,
    findInsertIndex,
  } from "../../lib/utils/geometry";
  import { pingNode } from "../../lib/actions/pingActions";
  import NodeElement from "./NodeElement.svelte";
  import ConnectionLine from "./ConnectionLine.svelte";
  import StickyNoteEl from "./StickyNote.svelte";
  import GroupRect from "./GroupRect.svelte";
  import WaypointHandle from "./WaypointHandle.svelte";

  let svgEl: SVGSVGElement;

  // Pan state
  let isPanning = $state(false);
  let panStartX = 0;
  let panStartY = 0;
  let panStartPanX = 0;
  let panStartPanY = 0;

  // Node drag state
  let isDragging = $state(false);
  let dragNodeIndex: number | null = null;

  // Group drawing state
  let isDrawingGroup = $state(false);
  let groupStartX = $state(0);
  let groupStartY = $state(0);
  let groupCurrentX = $state(0);
  let groupCurrentY = $state(0);

  // Sticky note drag state
  let isDraggingStickyNote = $state(false);
  let dragStickyIndex: number | null = null;

  let colors = $derived(getThemeColors($currentTheme));

  /** Convert screen coordinates to world (SVG) coordinates */
  function screenToWorld(
    clientX: number,
    clientY: number
  ): { x: number; y: number } {
    const rect = svgEl.getBoundingClientRect();
    const sx = clientX - rect.left;
    const sy = clientY - rect.top;
    return {
      x: (sx - $panX) / $zoom,
      y: (sy - $panY) / $zoom,
    };
  }

  // --- Mouse handlers ---

  function onMouseDown(e: MouseEvent) {
    // Right-click: start pan
    if (e.button === 2) {
      e.preventDefault();
      isPanning = true;
      panStartX = e.clientX;
      panStartY = e.clientY;
      panStartPanX = $panX;
      panStartPanY = $panY;
      return;
    }

    // Left-click in groups mode: start drawing group
    if (e.button === 0 && $groupsModeActive && $mode === "Configuration") {
      const { x, y } = screenToWorld(e.clientX, e.clientY);
      // Check if clicking on an existing group (for selection) - skip if on empty canvas
      const target = e.target as SVGElement;
      if (
        target === svgEl ||
        target.closest("svg") === svgEl &&
        !target.closest("[data-type='group']") &&
        !target.closest("[data-type='node']")
      ) {
        isDrawingGroup = true;
        groupStartX = x;
        groupStartY = y;
        groupCurrentX = x;
        groupCurrentY = y;
      }
      return;
    }
  }

  function onMouseMove(e: MouseEvent) {
    // Pan
    if (isPanning) {
      const dx = e.clientX - panStartX;
      const dy = e.clientY - panStartY;
      panX.set(panStartPanX + dx);
      panY.set(panStartPanY + dy);
      return;
    }

    // Group drawing
    if (isDrawingGroup) {
      const { x, y } = screenToWorld(e.clientX, e.clientY);
      groupCurrentX = x;
      groupCurrentY = y;
      return;
    }

    // Node drag
    if (isDragging && dragNodeIndex !== null && $mode === "Configuration") {
      const { x, y } = screenToWorld(e.clientX, e.clientY);
      moveNode(dragNodeIndex, x, y);
      return;
    }

    // Sticky note drag
    if (isDraggingStickyNote && dragStickyIndex !== null && $mode === "Configuration") {
      const { x, y } = screenToWorld(e.clientX, e.clientY);
      stickyNotes.update((notes) => {
        const copy = [...notes];
        if (copy[dragStickyIndex!]) {
          copy[dragStickyIndex!] = { ...copy[dragStickyIndex!], x, y };
        }
        return copy;
      });
      return;
    }
  }

  function onMouseUp(e: MouseEvent) {
    if (isPanning) {
      isPanning = false;
      return;
    }

    if (isDrawingGroup) {
      isDrawingGroup = false;
      const x1 = Math.min(groupStartX, groupCurrentX);
      const y1 = Math.min(groupStartY, groupCurrentY);
      const x2 = Math.max(groupStartX, groupCurrentX);
      const y2 = Math.max(groupStartY, groupCurrentY);
      // Only create if minimum size
      if (Math.abs(x2 - x1) > 20 && Math.abs(y2 - y1) > 20) {
        addGroup({
          x1,
          y1,
          x2,
          y2,
          name: "New Group",
          color: "",
          light_bg: "#e3f0ff",
          light_border: "#3a7bd5",
          dark_bg: "#22304a",
          dark_border: "#3a7bd5",
          color_preset_id: "preset1",
        });
      }
      return;
    }

    if (isDragging) {
      isDragging = false;
      dragNodeIndex = null;
      return;
    }

    if (isDraggingStickyNote) {
      isDraggingStickyNote = false;
      dragStickyIndex = null;
      return;
    }
  }

  function onWheel(e: WheelEvent) {
    e.preventDefault();
    const factor = e.deltaY < 0 ? 1.1 : 0.9;
    const rect = svgEl.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    // Zoom towards mouse position
    const newZoom = $zoom * factor;
    const newPanX = mouseX - (mouseX - $panX) * factor;
    const newPanY = mouseY - (mouseY - $panY) * factor;

    zoom.set(newZoom);
    panX.set(newPanX);
    panY.set(newPanY);
  }

  function onDblClick(e: MouseEvent) {
    if ($mode !== "Configuration") return;
    if ($groupsModeActive) return;

    // Check if shift is held for sticky note
    if (e.shiftKey) {
      const { x, y } = screenToWorld(e.clientX, e.clientY);
      // Open sticky note editor dialog
      activeDialog.set("stickyNote");
      // Store position for the dialog to use
      (window as any).__stickyNotePosition = { x, y };
      return;
    }

    // Create node
    const { x, y } = screenToWorld(e.clientX, e.clientY);
    // Open node editor dialog
    activeDialog.set("nodeEditor");
    (window as any).__newNodePosition = { x, y };
    (window as any).__editNodeIndex = null;
  }

  function onContextMenu(e: MouseEvent) {
    e.preventDefault();
    // Context menu is handled by right-click on nodes
  }

  // Node event handlers (called from NodeElement)
  function handleNodeMouseDown(e: MouseEvent, index: number) {
    if (e.button === 0) {
      // Left click: select + start drag in config mode
      previousSelectedNodeIndex.set($selectedNodeIndex);
      selectedNodeIndex.set(index);

      if ($mode === "Configuration" && !$groupsModeActive) {
        isDragging = true;
        dragNodeIndex = index;
      }

      // Ping on click (both modes)
      pingNode(index);
    } else if (e.button === 1) {
      // Middle click: connection creation
      e.preventDefault();
      if ($mode !== "Configuration") return;

      if (e.shiftKey) {
        // Shift+middle: remove connection
        const currentConns = $connections;
        const connIdx = currentConns.findIndex(
          (c) => c.from === index || c.to === index
        );
        if (connIdx >= 0) {
          removeConnection(connIdx);
        }
        return;
      }

      if ($connectionStartNodeIndex === null) {
        connectionStartNodeIndex.set(index);
      } else if ($connectionStartNodeIndex !== index) {
        // Open connection editor
        (window as any).__connectionFromIndex = $connectionStartNodeIndex;
        (window as any).__connectionToIndex = index;
        (window as any).__editConnectionIndex = null;
        activeDialog.set("connectionEditor");
        connectionStartNodeIndex.set(null);
      }
    } else if (e.button === 2) {
      // Right click: context menu
      e.preventDefault();
      e.stopPropagation();
      contextMenu.set({
        visible: true,
        x: e.clientX,
        y: e.clientY,
        nodeIndex: index,
        connectionIndex: null,
      });
    }
  }

  function handleStickyMouseDown(e: MouseEvent, index: number) {
    if (e.button === 0 && $mode === "Configuration") {
      isDraggingStickyNote = true;
      dragStickyIndex = index;
    } else if (e.button === 2 && $mode === "Configuration") {
      e.preventDefault();
      // Right-click on sticky note: show context menu for delete/edit
      contextMenu.set({
        visible: true,
        x: e.clientX,
        y: e.clientY,
        nodeIndex: null,
        connectionIndex: null,
      });
      (window as any).__contextStickyIndex = index;
    }
  }

  // Middle-click on connection line: add waypoint
  function handleConnectionMiddleClick(
    e: MouseEvent,
    connIndex: number
  ) {
    if ($mode !== "Configuration") return;
    if (e.button !== 1) return;
    e.preventDefault();

    if (e.shiftKey) {
      // Shift+middle: remove entire connection
      removeConnection(connIndex);
      return;
    }

    const { x, y } = screenToWorld(e.clientX, e.clientY);
    const conn = $connections[connIndex];
    const fromNode = $nodes[conn.from];
    const toNode = $nodes[conn.to];
    const polyPoints = buildPolylinePoints(
      fromNode.x,
      fromNode.y,
      toNode.x,
      toNode.y,
      conn.waypoints
    );
    const insertIdx = findInsertIndex(x, y, polyPoints);
    const newWaypoints = [...(conn.waypoints ?? [])];
    newWaypoints.splice(insertIdx, 0, [x, y]);

    connections.update((c) => {
      const copy = [...c];
      copy[connIndex] = { ...copy[connIndex], waypoints: newWaypoints };
      return copy;
    });
    unsavedChanges.set(true);
  }

  // Connection label right-click: edit connection
  function handleConnectionRightClick(
    e: MouseEvent,
    connIndex: number
  ) {
    if (e.button !== 2) return;
    e.preventDefault();
    (window as any).__editConnectionIndex = connIndex;
    const conn = $connections[connIndex];
    (window as any).__connectionFromIndex = conn.from;
    (window as any).__connectionToIndex = conn.to;
    activeDialog.set("connectionEditor");
  }

  // Build SVG polyline points string
  function polylineStr(
    fromX: number,
    fromY: number,
    toX: number,
    toY: number,
    waypoints?: [number, number][]
  ): string {
    const pts: string[] = [`${fromX},${fromY}`];
    if (waypoints) {
      for (const [wx, wy] of waypoints) {
        pts.push(`${wx},${wy}`);
      }
    }
    pts.push(`${toX},${toY}`);
    return pts.join(" ");
  }

  // Get node fill color based on ping results
  function getNodeFill(
    index: number,
    defaultColor: string
  ): string {
    const results = $pingResults[index];
    if (!results || results.length === 0) return defaultColor;

    const allSuccess = results.every((r) => r);
    const anySuccess = results.some((r) => r);

    if (allSuccess) return colors.NODE_PING_SUCCESS;
    if (anySuccess) return colors.NODE_PING_PARTIAL_SUCCESS;
    return colors.NODE_PING_FAILURE;
  }
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<svg
  bind:this={svgEl}
  class="w-full h-full"
  style:background-color={colors.FRAME_BG}
  style:cursor={isPanning
    ? "grabbing"
    : $groupsModeActive
      ? "crosshair"
      : "default"}
  onmousedown={onMouseDown}
  onmousemove={onMouseMove}
  onmouseup={onMouseUp}
  onwheel={onWheel}
  ondblclick={onDblClick}
  oncontextmenu={onContextMenu}
>
  <g
    id="world"
    transform="translate({$panX},{$panY}) scale({$zoom})"
  >
    <!-- Groups layer -->
    <g id="groups-layer">
      {#if $displayOptions.show_groups !== false}
        {#each $groups as group, i}
          {@const gc = getGroupColors(
            group.color_preset_id,
            $isDark,
            $groupColorPresets
          )}
          <GroupRect
            {group}
            index={i}
            bgColor={gc.bg}
            borderColor={gc.border}
            textColor={colors.GROUP_TEXT}
          />
        {/each}
      {/if}
    </g>

    <!-- Connections layer -->
    <g id="connections-layer">
      {#if $displayOptions.show_connections !== false}
        {#each $connections as conn, i}
          {#if $nodes[conn.from] && $nodes[conn.to]}
            <ConnectionLine
              connection={conn}
              index={i}
              fromNode={$nodes[conn.from]}
              toNode={$nodes[conn.to]}
              lineColor={colors.Connections}
              textColor={colors.INFO_TEXT}
              labelBgColor={colors.INFO_NOTE_BG}
              showLabels={$displayOptions.show_connection_labels !== false}
              showHandles={$mode === "Configuration"}
              onMiddleClick={(e) =>
                handleConnectionMiddleClick(e, i)}
              onRightClick={(e) =>
                handleConnectionRightClick(e, i)}
            />
          {/if}
        {/each}
      {/if}
    </g>

    <!-- Notes layer -->
    <g id="notes-layer">
      {#if $displayOptions.show_notes !== false}
        {#each $stickyNotes as note, i}
          <StickyNoteEl
            {note}
            index={i}
            textColor={colors.INFO_TEXT}
            bgColor={colors.INFO_NOTE_BG}
            onMouseDown={(e) => handleStickyMouseDown(e, i)}
          />
        {/each}
      {/if}
    </g>

    <!-- Nodes layer -->
    <g id="nodes-layer">
      {#each $nodes as node, i}
        <NodeElement
          {node}
          index={i}
          fillColor={getNodeFill(i, colors.NODE_DEFAULT)}
          outlineColor={$selectedNodeIndex === i
            ? colors.NODE_HIGHLIGHT
            : colors.NODE_OUTLINE_DEFAULT}
          outlineWidth={$selectedNodeIndex === i ? 4 : 2}
          textColor={colors.BUTTON_TEXT}
          fontSize={$displayOptions.node_size ?? 14}
          onMouseDown={(e) => handleNodeMouseDown(e, i)}
        />
      {/each}
    </g>

    <!-- Handles layer -->
    <g id="handles-layer">
      {#if $mode === "Configuration"}
        {#each $connections as conn, ci}
          {#if conn.waypoints}
            {#each conn.waypoints as wp, wi}
              <WaypointHandle
                x={wp[0]}
                y={wp[1]}
                connectionIndex={ci}
                waypointIndex={wi}
              />
            {/each}
          {/if}
        {/each}
      {/if}
    </g>
  </g>

  <!-- Group drawing preview -->
  {#if isDrawingGroup}
    <rect
      x={Math.min(groupStartX, groupCurrentX) * $zoom + $panX}
      y={Math.min(groupStartY, groupCurrentY) * $zoom + $panY}
      width={Math.abs(groupCurrentX - groupStartX) * $zoom}
      height={Math.abs(groupCurrentY - groupStartY) * $zoom}
      fill="none"
      stroke={colors.GROUP_OUTLINE}
      stroke-width="2"
      stroke-dasharray="6,4"
      pointer-events="none"
    />
  {/if}
</svg>
