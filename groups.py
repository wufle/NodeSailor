import tkinter as tk
from colors import ColorConfig

from colors import ColorConfig, get_group_colors

class RectangleGroup:
    HANDLE_SIZE = 8

    def __init__(self, canvas, x1, y1, x2, y2, name="Group", color=None,
                 light_bg=None, light_border=None, dark_bg=None, dark_border=None, color_preset_id=None, color_presets=None):
        self.canvas = canvas
        self.x1 = min(x1, x2)
        self.y1 = min(y1, y2)
        self.x2 = max(x1, x2)
        self.y2 = max(y1, y2)
        self.name = name
        self.color = color or ColorConfig.current.GROUP_DEFAULT
        self.light_bg = light_bg or ColorConfig.current.GROUP_DEFAULT
        self.light_border = light_border or ColorConfig.current.GROUP_OUTLINE
        self.dark_bg = dark_bg or "#222222"
        self.dark_border = dark_border or "#888888"
        self.color_preset_id = color_preset_id  # New attribute for preset selection
        self.color_presets = color_presets  # Store the current color presets

        # Track whether resize mode is active
        self.resize_mode_active = False

        # Use color preset if available
        if self.color_preset_id:
            color_scheme = "dark" if ColorConfig.current == ColorConfig.Dark else "light"
            fill_color, outline_color = get_group_colors(self.color_preset_id, color_scheme, self.color_presets)
        else:
            if ColorConfig.current == ColorConfig.Light:
                fill_color = self.light_bg
                outline_color = self.light_border
            else:
                fill_color = self.dark_bg
                outline_color = self.dark_border

        self.rectangle = canvas.create_rectangle(
            self.x1, self.y1, self.x2, self.y2,
            fill=fill_color, outline=outline_color,
            width=2, stipple="gray50", tags="group"
        )

        # Create the text label for the group
        self.text = canvas.create_text(
            self.x1 + 10, self.y1 + 10,  # Position text in top-left corner with padding
            text=self.name,
            fill=ColorConfig.current.GROUP_TEXT,
            anchor="nw",
            font=("Helvetica", 10, "bold"),
            tags="group_text"
        )

        # Handles: [top-left, top-right, bottom-right, bottom-left]
        self.handles = [None, None, None, None]
        self._active_handle = None
        self._drag_start = None

        # Ensure the group is drawn behind all nodes and connections
        self.send_to_back()

        # Bind events for selection and context menu
        self.canvas.tag_bind(self.rectangle, '<Button-1>', self.on_click)
        self.canvas.tag_bind(self.text, '<Button-1>', self.on_click)

    def show_handles(self):
        self.remove_handles()
        coords = [
            (self.x1, self.y1),  # top-left
            (self.x2, self.y1),  # top-right
            (self.x2, self.y2),  # bottom-right
            (self.x1, self.y2),  # bottom-left
        ]
        self.handles = []
        for idx, (x, y) in enumerate(coords):
            handle = self.canvas.create_rectangle(
                x - self.HANDLE_SIZE // 2, y - self.HANDLE_SIZE // 2,
                x + self.HANDLE_SIZE // 2, y + self.HANDLE_SIZE // 2,
                fill="#ffffff", outline="#000000", width=1, tags="resize_handle"
            )
            self.handles.append(handle)
            self.canvas.tag_bind(handle, "<Button-1>", lambda e, i=idx: self._on_handle_press(e, i))
            self.canvas.tag_bind(handle, "<B1-Motion>", lambda e, i=idx: self._on_handle_drag(e, i))
            self.canvas.tag_bind(handle, "<ButtonRelease-1>", lambda e, i=idx: self._on_handle_release(e, i))

    def remove_handles(self):
        for handle in self.handles:
            if handle is not None:
                self.canvas.delete(handle)
        self.handles = [None, None, None, None]

    def update_handles(self):
        if not self.handles or any(h is None for h in self.handles):
            return
        coords = [
            (self.x1, self.y1),  # top-left
            (self.x2, self.y1),  # top-right
            (self.x2, self.y2),  # bottom-right
            (self.x1, self.y2),  # bottom-left
        ]
        for handle, (x, y) in zip(self.handles, coords):
            self.canvas.coords(
                handle,
                x - self.HANDLE_SIZE // 2, y - self.HANDLE_SIZE // 2,
                x + self.HANDLE_SIZE // 2, y + self.HANDLE_SIZE // 2,
            )

    def _on_handle_press(self, event, handle_idx):
        self._active_handle = handle_idx
        self._drag_start = (self.x1, self.y1, self.x2, self.y2, event.x, event.y)

    def _on_handle_drag(self, event, handle_idx):
        # Only allow resizing if resize mode is active
        if not getattr(self, "resize_mode_active", False):
            return
        if self._drag_start is None:
            return
        x1, y1, x2, y2, start_x, start_y = self._drag_start
        dx = self.canvas.canvasx(event.x) - self.canvas.canvasx(start_x)
        dy = self.canvas.canvasy(event.y) - self.canvas.canvasy(start_y)
        # Update coordinates based on handle
        if handle_idx == 0:  # top-left
            new_x1, new_y1 = x1 + dx, y1 + dy
            self.update_position(new_x1, new_y1, x2, y2)
        elif handle_idx == 1:  # top-right
            new_x2, new_y1 = x2 + dx, y1 + dy
            self.update_position(x1, new_y1, new_x2, y2)
        elif handle_idx == 2:  # bottom-right
            new_x2, new_y2 = x2 + dx, y2 + dy
            self.update_position(x1, y1, new_x2, new_y2)
        elif handle_idx == 3:  # bottom-left
            new_x1, new_y2 = x1 + dx, y2 + dy
            self.update_position(new_x1, y1, x2, new_y2)
        self.update_handles()

    def _on_handle_release(self, event, handle_idx):
        self._active_handle = None
        self._drag_start = None

    def update_position(self, x1, y1, x2, y2):
        """Update the position and size of the rectangle group"""
        self.x1 = min(x1, x2)
        self.y1 = min(y1, y2)
        self.x2 = max(x1, x2)
        self.y2 = max(y1, y2)

        self.canvas.coords(self.rectangle, self.x1, self.y1, self.x2, self.y2)
        self.canvas.coords(self.text, self.x1 + 10, self.y1 + 10)
        self.update_handles()
        
    def update_properties(self, name=None, color=None,
                          light_bg=None, light_border=None, dark_bg=None, dark_border=None, color_preset_id=None, color_presets=None, resize_mode_active=None):
        """Update the properties of the rectangle group"""
        if name is not None:
            self.name = name
            self.canvas.itemconfig(self.text, text=name)
        if color is not None:
            self.color = color
        if light_bg is not None:
            self.light_bg = light_bg
        if light_border is not None:
            self.light_border = light_border
        if dark_bg is not None:
            self.dark_bg = dark_bg
        if dark_border is not None:
            self.dark_border = dark_border
        if color_preset_id is not None:
            self.color_preset_id = color_preset_id
        if color_presets is not None:
            self.color_presets = color_presets
        if resize_mode_active is not None:
            self.resize_mode_active = resize_mode_active

        # Use color preset if available
        if self.color_preset_id:
            color_scheme = "dark" if ColorConfig.current == ColorConfig.Dark else "light"
            fill_color, outline_color = get_group_colors(self.color_preset_id, color_scheme, self.color_presets)
        else:
            if ColorConfig.current == ColorConfig.Light:
                fill_color = self.light_bg
                outline_color = self.light_border
            else:
                fill_color = self.dark_bg
                outline_color = self.dark_border
        self.canvas.itemconfig(self.rectangle, fill=fill_color, outline=outline_color)
    
    def send_to_back(self):
        """Ensure the group is drawn behind all nodes and connections"""
        self.canvas.tag_lower(self.rectangle)
        self.canvas.tag_raise(self.text, self.rectangle)  # Keep text above rectangle
    
    def on_click(self, event):
        """Handle click events on the group"""
        gui = self.canvas.gui
        if hasattr(gui, "groups_mode_active") and gui.groups_mode_active:
            gui.group_manager.selected_group = self         
            # If there's a group editor window open, update it
            if hasattr(gui, "group_editor_window") and gui.group_editor_window and gui.group_editor_window.winfo_exists():
                gui.update_group_editor(self)
    
    def contains_point(self, x, y):
        """Check if the point (x, y) is inside the rectangle"""
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2
    
    def contains_node(self, node):
        """Check if a node is inside the rectangle"""
        return self.contains_point(node.x, node.y)
    
    def get_contained_nodes(self):
        """Get all nodes contained within this group"""
        contained_nodes = []
        gui = self.canvas.gui
        for node in gui.nodes:
            if self.contains_node(node):
                contained_nodes.append(node)
        return contained_nodes
    
    def to_dict(self):
        """Convert the group to a dictionary for saving"""
        return {
            'x1': self.x1,
            'y1': self.y1,
            'x2': self.x2,
            'y2': self.y2,
            'name': self.name,
            'color': self.color,
            'light_bg': self.light_bg,
            'light_border': self.light_border,
            'dark_bg': self.dark_bg,
            'dark_border': self.dark_border,
            'color_preset_id': self.color_preset_id
        }
    
    @classmethod
    def from_dict(cls, canvas, data):
        """Create a group from a dictionary (for loading)"""
        return cls(
            canvas,
            data['x1'],
            data['y1'],
            data['x2'],
            data['y2'],
            data.get('name', "Group"),
            data.get('color'),
            data.get('light_bg'),
            data.get('light_border'),
            data.get('dark_bg'),
            data.get('dark_border'),
            data.get('color_preset_id')
        )

class GroupManager:
    def __init__(self, gui):
        self.gui = gui
        self.groups = []
        self.selected_group = None
        self.start_x = None
        self.start_y = None
        self.current_group = None
        self.drawing = False
        
    @property
    def canvas(self):
        """Access the canvas through the gui object when needed"""
        return self.gui.canvas
    
    def start_drawing(self, event):
        """Start drawing a new rectangle group"""
        if not self.gui.groups_mode_active:
            return
            
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        self.drawing = True
        
        # Create a temporary rectangle
        self.current_group = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline=ColorConfig.current.GROUP_OUTLINE,
            width=2, dash=(5, 5)
        )
    
    def update_drawing(self, event):
        """Update the rectangle being drawn"""
        if not self.drawing or not self.gui.groups_mode_active:
            return
            
        self.canvas.coords(
            self.current_group,
            self.start_x, self.start_y,
            self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        )
    
    def finish_drawing(self, event):
        """Finish drawing the rectangle and create a group"""
        if not self.drawing or not self.gui.groups_mode_active:
            return
            
        self.drawing = False
        
        # Only create a group if the rectangle has some size
        if abs(self.canvas.canvasx(event.x) - self.start_x) > 10 and abs(self.canvas.canvasy(event.y) - self.start_y) > 10:
            # Delete the temporary rectangle
            self.canvas.delete(self.current_group)
            
            # Create a new group
            group = RectangleGroup(
                self.canvas,
                self.start_x, self.start_y,
                self.canvas.canvasx(event.x), self.canvas.canvasy(event.y),
                f"Group {len(self.groups) + 1}",
                ColorConfig.current.GROUP_DEFAULT
            )
            
            self.groups.append(group)
            self.selected_group = group
            
            # Open the group editor
            self.gui.open_group_editor(group)
        else:
            # Delete the temporary rectangle if it's too small
            self.canvas.delete(self.current_group)
        
        self.current_group = None
    
    def select_group(self, event):
        """Select a group at the given coordinates"""
        if not self.gui.groups_mode_active:
            return

        prev_selected = self.selected_group

        # Find the topmost group at the event coordinates
        for group in reversed(self.groups):
            if group.contains_point(self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)):
                self.selected_group = group
                if prev_selected and prev_selected != group:
                    prev_selected.remove_handles()
                if self.selected_group:
                    if (
                        hasattr(self.gui, "group_editor_window")
                        and self.gui.group_editor_window
                        and self.gui.group_editor_window.winfo_exists()
                        and getattr(self.gui, "group_resize_mode_active", False)
                    ):
                        self.selected_group.show_handles()
                    else:
                        self.selected_group.remove_handles()
                if hasattr(self.gui, "group_editor_window") and self.gui.group_editor_window and self.gui.group_editor_window.winfo_exists():
                    self.gui.update_group_editor(group)
                return

        if self.selected_group:
            self.selected_group.remove_handles()
        self.selected_group = None
    
    def delete_group(self, group):
        """Delete a group"""
        if group in self.groups:
            self.canvas.delete(group.rectangle)
            self.canvas.delete(group.text)
            self.groups.remove(group)
            
            if self.selected_group == group:
                self.selected_group = None
    
    def send_all_to_back(self):
        """Send all groups to the back"""
        for group in self.groups:
            group.send_to_back()