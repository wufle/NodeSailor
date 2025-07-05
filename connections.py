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

    def draw_line(self):
        # Remove old line and handles
        if self.line:
            self.canvas.delete(self.line)
        for handle in getattr(self, 'waypoint_handles', []):
            self.canvas.delete(handle)
        self.waypoint_handles = []

        # Draw the polyline
        points = [self.node1.x, self.node1.y]
        for wx, wy in self.waypoints:
            points.extend([wx, wy])
        points.extend([self.node2.x, self.node2.y])
        # Remove 'smooth=True' to make sharp turns at waypoints
        self.line = self.canvas.create_line(*points, width=2, fill=ColorConfig.current.Connections)

        # Draw waypoint handles (small circles) if in Configuration mode
        if self.gui and getattr(self.gui, "mode", "") == "Configuration":
            for idx, (wx, wy) in enumerate(self.waypoints):
                handle = self.canvas.create_oval(wx-6, wy-6, wx+6, wy+6, fill="#FFD700", outline="#333", tags="waypoint_handle")
                self.canvas.tag_bind(handle, "<ButtonPress-1>", lambda e, i=idx: self.start_drag_waypoint(e, i))
                self.canvas.tag_bind(handle, "<B1-Motion>", self.drag_waypoint)
                self.canvas.tag_bind(handle, "<ButtonRelease-1>", self.end_drag_waypoint)
                self.canvas.tag_bind(handle, "<Button-3>", lambda e, i=idx: self.remove_waypoint(i))
                self.waypoint_handles.append(handle)

        # Bind middle-click to add waypoint if in Configuration mode
        if self.gui and getattr(self.gui, "mode", "") == "Configuration":
            self.canvas.tag_bind(self.line, '<Button-2>', self.handle_middle_click)

    def handle_middle_click(self, event):
        # Only add waypoint if in Configuration mode
        if self.gui and getattr(self.gui, "mode", "") == "Configuration":
            self.add_waypoint(event.x, event.y)
            if hasattr(self.gui, 'unsaved_changes'):
                self.gui.unsaved_changes = True

    def add_waypoint(self, x, y):
        self.waypoints.append((x, y))
        self.draw_line()

    def remove_waypoint(self, idx):
        if 0 <= idx < len(self.waypoints):
            self.waypoints.pop(idx)
            self.draw_line()

    def start_drag_waypoint(self, event, idx):
        self._dragging_waypoint = idx

    def drag_waypoint(self, event):
        idx = self._dragging_waypoint
        if idx is not None and 0 <= idx < len(self.waypoints):
            self.waypoints[idx] = (event.x, event.y)
            self.draw_line()

    def end_drag_waypoint(self, event):
        self._dragging_waypoint = None
        if self.gui and hasattr(self.gui, 'unsaved_changes'):
            self.gui.unsaved_changes = True

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
