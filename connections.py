import tkinter as tk
from colors import ColorConfig

class ConnectionLine:
    def __init__(self, canvas, node1, node2, label='', connectioninfo=None, gui=None, waypoints=None, label_pos=0.5):
        self.canvas = canvas
        self.node1 = node1
        self.node2 = node2
        self.label = label
        self.connectioninfo = connectioninfo
        self.label_id = None
        self.gui = gui
        self.waypoints = waypoints or []  # List of (x, y) tuples
        self.waypoint_handles = []  # Canvas IDs for waypoint circles
        self.line = None
        self._dragging_waypoint = None  # Track which waypoint is being dragged
        self.label_pos = label_pos  # Float between 0 and 1, position of label along the connection
        self.draw_line()
        if label:
            self.update_label()
        node1.connections.append(self)
        node2.connections.append(self)
        # Register with GUI's connection_lines list if available
        if self.gui and hasattr(self.gui, "connection_lines"):
            self.gui.connection_lines.append(self)

    def show_waypoint_handles(self):
        # Only show handles if in Configuration mode
        if self.gui and getattr(self.gui, "mode", "") == "Configuration":
            self.draw_line()

    def remove_waypoint_handles(self):
        for handle in getattr(self, 'waypoint_handles', []):
            self.canvas.delete(handle)
        self.waypoint_handles = []

    def update_properties(self, resize_mode_active=None):
        # For compatibility with group_editor logic
        # Waypoints are always visible in Configuration mode, so this method doesn't need to do much
        if resize_mode_active is not None:
            # Store the state for potential future use, but waypoints work independently
            self.waypoint_resize_mode_active = resize_mode_active
        # Always redraw to ensure waypoint handles match current mode
        self.draw_line()

    def draw_line(self):
        # Check if we're in the middle of a drag operation
        active_drag = getattr(self, "_active_waypoint_handle", None) is not None
        if active_drag:
            pass
        
        # Remove old line and handles
        if self.line:
            self.canvas.delete(self.line)
        handle_count = len(getattr(self, 'waypoint_handles', []))
        for handle in getattr(self, 'waypoint_handles', []):
            self.canvas.delete(handle)

        self.waypoint_handles = []

        # Draw the polyline
        points = [self.node1.x, self.node1.y]
        for wx, wy in self.waypoints:
            points.extend([wx, wy])
        points.extend([self.node2.x, self.node2.y])
        self.line = self.canvas.create_line(*points, width=2, fill=ColorConfig.current.Connections)

        # Draw waypoint handles (small circles) only if not in operator mode (i.e., only in Configuration mode)
        # This ensures waypoints are hidden in operator mode
        if self.gui and getattr(self.gui, "mode", "") == "Configuration":
            for idx, (wx, wy) in enumerate(self.waypoints):
                handle = self.canvas.create_oval(
                    wx - 8 // 2, wy - 8 // 2, wx + 8 // 2, wy + 8 // 2,
                    fill="#FFD700", outline="#333", tags="waypoint_handle"
                )
                self.canvas.tag_bind(handle, "<Button-1>", lambda e, i=idx: self._on_waypoint_handle_press(e, i))
                self.canvas.tag_bind(handle, "<B1-Motion>", lambda e, i=idx: self._on_waypoint_handle_drag(e, i))
                self.canvas.tag_bind(handle, "<ButtonRelease-1>", lambda e, i=idx: self._on_waypoint_handle_release(e, i))
                self.canvas.tag_bind(handle, "<Button-3>", lambda e, i=idx: self.remove_waypoint(i))
                self.waypoint_handles.append(handle)

        # Bind middle-click to add waypoint if in Configuration mode
        if self.gui and getattr(self.gui, "mode", "") == "Configuration":
            self.canvas.tag_bind(self.line, '<Button-2>', self.handle_middle_click)
        else:
            # Remove any existing waypoint handles if not in Configuration mode
            for handle in getattr(self, 'waypoint_handles', []):
                self.canvas.delete(handle)
            self.waypoint_handles = []

    def handle_middle_click(self, event):
        # Only add waypoint if in Configuration mode
        if self.gui and getattr(self.gui, "mode", "") == "Configuration":
            # Convert to canvas coordinates
            canvas_x = self.canvas.canvasx(event.x)
            canvas_y = self.canvas.canvasy(event.y)
            self.add_waypoint(canvas_x, canvas_y)
            if hasattr(self.gui, 'unsaved_changes'):
                self.gui.unsaved_changes = True

    def add_waypoint(self, canvas_x, canvas_y):
        # Waypoint coordinates are already in canvas coordinates
        self.waypoints.append((canvas_x, canvas_y))
        self.draw_line()

    def remove_waypoint(self, idx):
        if 0 <= idx < len(self.waypoints):
            self.waypoints.pop(idx)
            self.draw_line()

    # --- Waypoint Handle Drag Logic (mirroring group resizer handle logic) ---
    def _on_waypoint_handle_press(self, event, idx):
        # Always allow waypoint dragging in Configuration mode, not dependent on resize mode
        if self.gui and getattr(self.gui, "mode", "") != "Configuration":
            return
        self._active_waypoint_handle = idx
        # Store the original waypoint coordinates and the original event coordinates
        waypoint_x, waypoint_y = self.waypoints[idx]
        self._waypoint_drag_start = (waypoint_x, waypoint_y, event.x, event.y)

    def _on_waypoint_handle_drag(self, event, idx):
        # Always allow waypoint dragging in Configuration mode, not dependent on resize mode
        if self.gui and getattr(self.gui, "mode", "") != "Configuration":
            return
        if getattr(self, "_active_waypoint_handle", None) is None:
            return
        if getattr(self, "_waypoint_drag_start", None) is None:
            return
        # Get original waypoint coordinates and original event coordinates
        orig_waypoint_x, orig_waypoint_y, orig_event_x, orig_event_y = self._waypoint_drag_start
        # Calculate delta in canvas coordinates (like group resizer)
        dx = self.canvas.canvasx(event.x) - self.canvas.canvasx(orig_event_x)
        dy = self.canvas.canvasy(event.y) - self.canvas.canvasy(orig_event_y)
        # Apply delta to original waypoint coordinates
        new_x = orig_waypoint_x + dx
        new_y = orig_waypoint_y + dy
        # Update the waypoint
        active_idx = self._active_waypoint_handle
        if 0 <= active_idx < len(self.waypoints):
            self.waypoints[active_idx] = (new_x, new_y)
            
            # Efficient update: only update line coordinates and handle position without recreating items
            self._update_line_coordinates()
            self._update_waypoint_handle_position(active_idx, new_x, new_y)
        else:
            pass

    def _on_waypoint_handle_release(self, event, idx):
        # Always allow waypoint dragging in Configuration mode, not dependent on resize mode
        if self.gui and getattr(self.gui, "mode", "") != "Configuration":
            return
        self._active_waypoint_handle = None
        self._waypoint_drag_start = None
        if self.gui and hasattr(self.gui, 'unsaved_changes'):
            self.gui.unsaved_changes = True

    def _update_line_coordinates(self):
        """Efficiently update only the line coordinates using canvas.coords() without recreating items"""
        if self.line:
            # Calculate new line coordinates including all waypoints
            points = [self.node1.x, self.node1.y]
            for wx, wy in self.waypoints:
                points.extend([wx, wy])
            points.extend([self.node2.x, self.node2.y])
            # Update line coordinates efficiently
            self.canvas.coords(self.line, *points)

    def _update_waypoint_handle_position(self, idx, new_x, new_y):
        """Efficiently update only the specific waypoint handle position using canvas.coords()"""
        if 0 <= idx < len(self.waypoint_handles):
            handle = self.waypoint_handles[idx]
            # Update handle position efficiently without recreating
            self.canvas.coords(handle,
                             new_x - 8 // 2, new_y - 8 // 2,
                             new_x + 8 // 2, new_y + 8 // 2)

    def update_position(self):
        self.draw_line()
        if self.label_id:
            self.update_label()  # Update label position
        # Ensure nodes are always visible on top of connection lines
        if self.gui and hasattr(self.gui, 'raise_all_nodes'):
            self.gui.raise_all_nodes()

    def update_label(self):
        if self.label_id:
            self.canvas.delete(self.label_id)
            if hasattr(self, 'label_bg') and self.label_bg:
                self.canvas.delete(self.label_bg)

        # --- Compute label position along the polyline using label_pos ---
        # Gather all points along the connection (start, waypoints, end)
        points = [(self.node1.x, self.node1.y)]
        points.extend(self.waypoints)
        points.append((self.node2.x, self.node2.y))

        # Calculate total length of the polyline
        import math
        def dist(a, b):
            return math.hypot(b[0] - a[0], b[1] - a[1])

        seg_lengths = []
        total_length = 0
        for i in range(len(points) - 1):
            l = dist(points[i], points[i+1])
            seg_lengths.append(l)
            total_length += l

        # Find the segment and position for label_pos
        target = self.label_pos * total_length
        accum = 0
        label_x, label_y = points[0]
        for i, seg_len in enumerate(seg_lengths):
            if accum + seg_len >= target:
                ratio = (target - accum) / seg_len if seg_len > 0 else 0
                x0, y0 = points[i]
                x1, y1 = points[i+1]
                label_x = x0 + (x1 - x0) * ratio
                label_y = y0 + (y1 - y0) * ratio
                break
            accum += seg_len
        else:
            # Fallback: end of last segment
            label_x, label_y = points[-1]

        # --- Draw label text ---
        self.label_id = self.canvas.create_text(
            label_x, label_y,
            text=self.label,
            font=('Helvetica', '12'),
            fill=ColorConfig.current.INFO_TEXT,
            tags="connection_label",
            anchor="center"
        )

        self.info_popup = None

        if self.connectioninfo:
            def show_info(event):
                self.info_popup = tk.Toplevel(self.canvas)
                self.info_popup.wm_overrideredirect(True)
                self.info_popup.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
                label = tk.Label(self.info_popup, text=self.connectioninfo,
                                background=ColorConfig.current.INFO_NOTE_BG,
                                foreground=ColorConfig.current.INFO_TEXT,
                                relief='solid', borderwidth=1,
                                font=("Helvetica", 10), justify='left')
                label.pack()

            def hide_info(event):
                if self.info_popup:
                    self.info_popup.destroy()
                    self.info_popup = None

            self.canvas.tag_bind(self.label_id, "<Enter>", show_info)
            self.canvas.tag_bind(self.label_id, "<Leave>", hide_info)

        # Always allow right-click editing, regardless of connectioninfo
        self.canvas.tag_bind(self.label_id, "<Button-3>", lambda event: self.gui.create_connection(event=None, edit_connection=self))

        # --- Add drag logic for label ---
        def on_label_press(event):
            # Only allow label drag in Configuration mode
            if not (self.gui and getattr(self.gui, "mode", "") == "Configuration"):
                return
            self._dragging_label = True
            self.canvas.itemconfig(self.label_id, fill=ColorConfig.current.NODE_HIGHLIGHT)
            if hasattr(self, 'label_bg') and self.label_bg:
                self.canvas.itemconfig(self.label_bg, fill=ColorConfig.current.NODE_HIGHLIGHT)
            # Store initial label_pos and mouse position for smooth dragging
            self._drag_label_start = (self.label_pos, event.x, event.y)
            # Bind drag and release to canvas so drag continues outside label area
            self.canvas.bind("<B1-Motion>", on_label_drag)
            self.canvas.bind("<ButtonRelease-1>", on_label_release)

        def on_label_drag(event):
            # Use the initial label_pos and mouse position to compute offset
            if not hasattr(self, '_drag_label_start'):
                return
            orig_label_pos, orig_x, orig_y = self._drag_label_start
            dx = event.x - orig_x
            dy = event.y - orig_y

            # Find the point along the polyline corresponding to the original label_pos
            if total_length == 0:
                return
            target = orig_label_pos * total_length
            accum = 0
            for i in range(len(points) - 1):
                x0, y0 = points[i]
                x1, y1 = points[i+1]
                seg_len = seg_lengths[i]
                if accum + seg_len >= target:
                    t = (target - accum) / seg_len if seg_len > 0 else 0
                    label_x = x0 + (x1 - x0) * t
                    label_y = y0 + (y1 - y0) * t
                    break
                accum += seg_len
            else:
                label_x, label_y = points[-1]

            # Apply mouse delta to label's original position
            px = label_x + dx
            py = label_y + dy

            # Project new (px, py) onto the polyline to get new label_pos
            min_dist = float('inf')
            best_pos = 0
            accum = 0
            for i in range(len(points) - 1):
                x0, y0 = points[i]
                x1, y1 = points[i+1]
                dx_seg, dy_seg = x1 - x0, y1 - y0
                seg_len = seg_lengths[i]
                if seg_len == 0:
                    continue
                t = ((px - x0) * dx_seg + (py - y0) * dy_seg) / (seg_len ** 2)
                t = max(0, min(1, t))
                proj_x = x0 + dx_seg * t
                proj_y = y0 + dy_seg * t
                d = math.hypot(px - proj_x, py - proj_y)

                if d < min_dist:
                    min_dist = d
                    best_pos = (accum + seg_len * t) / total_length if total_length > 0 else 0
                accum += seg_len
            self.label_pos = best_pos
            self.update_label()

        def on_label_release(event):
            self._dragging_label = False
            self.canvas.itemconfig(self.label_id, fill=ColorConfig.current.INFO_TEXT)
            if hasattr(self, 'label_bg') and self.label_bg:
                self.canvas.itemconfig(self.label_bg, fill=ColorConfig.current.INFO_NOTE_BG)
            # Unbind drag and release from canvas after drag ends
            self.canvas.unbind("<B1-Motion>")
            self.canvas.unbind("<ButtonRelease-1>")
            # label_pos is now updated and will be persisted by existing logic

        self.canvas.tag_bind(self.label_id, "<Button-1>", on_label_press)
        # Drag and release events will be bound to the canvas on press

        # --- Draw label background ---
        bbox = self.canvas.bbox(self.label_id)
        if bbox:
            padding = 2
            self.label_bg = self.canvas.create_rectangle(
                bbox[0]-padding, bbox[1]-padding, bbox[2]+padding, bbox[3]+padding,
                fill=ColorConfig.current.INFO_NOTE_BG, outline=''
            )
            self.canvas.tag_lower(self.label_bg, self.label_id)  # Ensure the background is behind the text
            # Also bind drag events to the background for easier grabbing
            self.canvas.tag_bind(self.label_bg, "<Button-1>", on_label_press)
            # Drag and release events will be bound to the canvas on press

    def set_label(self, label):
        self.label = label
        self.update_label()
