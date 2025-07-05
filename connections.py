import tkinter as tk
from colors import ColorConfig

class ConnectionLine:
    def __init__(self, canvas, node1, node2, label='', connectioninfo=None, gui=None, waypoints=None):
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
            print(f"DEBUG: draw_line() called during active drag of waypoint {getattr(self, '_active_waypoint_handle', 'unknown')}")
        
        # Remove old line and handles
        if self.line:
            self.canvas.delete(self.line)
        handle_count = len(getattr(self, 'waypoint_handles', []))
        for handle in getattr(self, 'waypoint_handles', []):
            self.canvas.delete(handle)
        self.waypoint_handles = []
        
        if active_drag:
            print(f"DEBUG: Deleted {handle_count} handles during drag - this will break the drag operation!")

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
                
            if active_drag:
                print(f"DEBUG: Created {len(self.waypoint_handles)} new handles during drag - event bindings reset!")

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
        print(f"DEBUG: Starting drag on waypoint {idx}")
        self._active_waypoint_handle = idx
        # Store the original waypoint coordinates and the original event coordinates
        waypoint_x, waypoint_y = self.waypoints[idx]
        self._waypoint_drag_start = (waypoint_x, waypoint_y, event.x, event.y)
        print(f"DEBUG: Drag start data: waypoint=({waypoint_x}, {waypoint_y}), event=({event.x}, {event.y})")

    def _on_waypoint_handle_drag(self, event, idx):
        # Always allow waypoint dragging in Configuration mode, not dependent on resize mode
        if self.gui and getattr(self.gui, "mode", "") != "Configuration":
            return
        if getattr(self, "_active_waypoint_handle", None) is None:
            print(f"DEBUG: Lost grip - no active waypoint handle")
            return
        if getattr(self, "_waypoint_drag_start", None) is None:
            print(f"DEBUG: Lost grip - no drag start data")
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
            print(f"DEBUG: Efficiently updating waypoint {active_idx} to ({new_x:.1f}, {new_y:.1f}), delta=({dx:.1f}, {dy:.1f})")
            self.waypoints[active_idx] = (new_x, new_y)
            
            # Efficient update: only update line coordinates and handle position without recreating items
            self._update_line_coordinates()
            self._update_waypoint_handle_position(active_idx, new_x, new_y)
        else:
            print(f"DEBUG: Lost grip - invalid waypoint index {active_idx}")

    def _on_waypoint_handle_release(self, event, idx):
        # Always allow waypoint dragging in Configuration mode, not dependent on resize mode
        if self.gui and getattr(self.gui, "mode", "") != "Configuration":
            return
        print(f"DEBUG: Ending drag on waypoint {idx}")
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

    def update_label(self):
        if self.label_id:
            self.canvas.delete(self.label_id)
            if hasattr(self, 'label_bg') and self.label_bg:
                self.canvas.delete(self.label_bg)

        # Calculate midpoint for the label
        if self.waypoints:
            # Use the middle waypoint for the label if available
            mid_idx = len(self.waypoints) // 2
            mid_x, mid_y = self.waypoints[mid_idx]
        else:
            mid_x = (self.node1.x + self.node2.x) / 2
            mid_y = (self.node1.y + self.node2.y) / 2

        # Create a text object similar to StickyNote
        self.label_id = self.canvas.create_text(mid_x, mid_y, text=self.label, font=('Helvetica', '12'), fill=ColorConfig.current.INFO_TEXT, tags="connection_label", anchor="center")

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
     
        # Recreate a background similar to StickyNote
        bbox = self.canvas.bbox(self.label_id)
        if bbox:
            padding = 2
            self.label_bg = self.canvas.create_rectangle(bbox[0]-padding, bbox[1]-padding, bbox[2]+padding, bbox[3]+padding, fill=ColorConfig.current.INFO_NOTE_BG, outline='')
            self.canvas.tag_lower(self.label_bg, self.label_id)  # Ensure the background is behind the text

    def set_label(self, label):
        self.label = label
        self.update_label()
