import tkinter as tk
from colors import ColorConfig

class RectangleGroup:
    def __init__(self, canvas, x1, y1, x2, y2, name="Group", color=None,
                 light_bg=None, light_border=None, dark_bg=None, dark_border=None):
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
        
        # Create the rectangle with lower z-index to be behind nodes and connections
        # Select background and border color based on current color scheme
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
        
        # Ensure the group is drawn behind all nodes and connections
        self.send_to_back()
        
        # Bind events for selection and context menu
        self.canvas.tag_bind(self.rectangle, '<Button-1>', self.on_click)
        self.canvas.tag_bind(self.text, '<Button-1>', self.on_click)
        
    def update_position(self, x1, y1, x2, y2):
        """Update the position and size of the rectangle group"""
        self.x1 = min(x1, x2)
        self.y1 = min(y1, y2)
        self.x2 = max(x1, x2)
        self.y2 = max(y1, y2)
        
        self.canvas.coords(self.rectangle, self.x1, self.y1, self.x2, self.y2)
        self.canvas.coords(self.text, self.x1 + 10, self.y1 + 10)
        
    def update_properties(self, name=None, color=None,
                          light_bg=None, light_border=None, dark_bg=None, dark_border=None):
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

        # Update fill and outline based on current color scheme
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
            # Highlight the selected group
            self.canvas.itemconfig(self.rectangle, width=3, outline=ColorConfig.current.GROUP_SELECTED)
            
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
            'dark_border': self.dark_border
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
            data.get('dark_border')
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
            
        self.start_x = event.x
        self.start_y = event.y
        self.drawing = True
        
        # Create a temporary rectangle
        self.current_group = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline=ColorConfig.current.GROUP_SELECTED,
            width=2, dash=(5, 5)
        )
    
    def update_drawing(self, event):
        """Update the rectangle being drawn"""
        if not self.drawing or not self.gui.groups_mode_active:
            return
            
        self.canvas.coords(
            self.current_group,
            self.start_x, self.start_y,
            event.x, event.y
        )
    
    def finish_drawing(self, event):
        """Finish drawing the rectangle and create a group"""
        if not self.drawing or not self.gui.groups_mode_active:
            return
            
        self.drawing = False
        
        # Only create a group if the rectangle has some size
        if abs(event.x - self.start_x) > 10 and abs(event.y - self.start_y) > 10:
            # Delete the temporary rectangle
            self.canvas.delete(self.current_group)
            
            # Create a new group
            group = RectangleGroup(
                self.canvas,
                self.start_x, self.start_y,
                event.x, event.y,
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
            
        # Deselect the current group
        if self.selected_group:
            self.canvas.itemconfig(
                self.selected_group.rectangle,
                width=2,
                outline=ColorConfig.current.GROUP_OUTLINE
            )
            
        # Find the topmost group at the event coordinates
        for group in reversed(self.groups):
            if group.contains_point(event.x, event.y):
                self.selected_group = group
                self.canvas.itemconfig(
                    group.rectangle,
                    width=3,
                    outline=ColorConfig.current.GROUP_SELECTED
                )
                
                # If there's a group editor window open, update it
                if hasattr(self.gui, "group_editor_window") and self.gui.group_editor_window and self.gui.group_editor_window.winfo_exists():
                    self.gui.update_group_editor(group)
                    
                return
                
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