import tkinter as tk
from tkinter import colorchooser

def open_group_editor(gui_self, group=None):
    ColorConfig = gui_self.ColorConfig if hasattr(gui_self, "ColorConfig") else __import__("colors").ColorConfig
    
    if getattr(gui_self, 'legend_window', None) and gui_self.legend_window.winfo_exists():
        gui_self.legend_window.destroy()
        gui_self.legend_window = None
    
    if getattr(gui_self, 'group_editor_window', None) and gui_self.group_editor_window.winfo_exists():
        gui_self.group_editor_window.lift()
        if group:
            gui_self.update_group_editor(group)
        return
    
    def close_editor():
        gui_self.group_editor_window.destroy()
        gui_self.group_editor_window = None
    
    win, content = gui_self.create_popup(
        "Group Editor", 400, 300,
        on_close=gui_self.make_popup_closer("group_editor_window"),
        grab=False
    )
    gui_self.group_editor_window = win
    win.lift(gui_self.root)
    win.attributes("-topmost", True)
    
    # Create the editor content
    editor_frame = tk.Frame(content, bg=ColorConfig.current.FRAME_BG)
    editor_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Group name
    name_frame = tk.Frame(editor_frame, bg=ColorConfig.current.FRAME_BG)
    name_frame.pack(fill=tk.X, pady=5)
    
    tk.Label(name_frame, text="Group Name:", bg=ColorConfig.current.FRAME_BG, 
             fg=ColorConfig.current.BUTTON_TEXT).pack(side=tk.LEFT, padx=5)
    
    name_entry = tk.Entry(name_frame, bg=ColorConfig.current.BUTTON_BG, 
                         fg=ColorConfig.current.BUTTON_TEXT, width=30)
    name_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    # Group color
    color_frame = tk.Frame(editor_frame, bg=ColorConfig.current.FRAME_BG)
    color_frame.pack(fill=tk.X, pady=5)
    
    tk.Label(color_frame, text="Group Color:", bg=ColorConfig.current.FRAME_BG, 
             fg=ColorConfig.current.BUTTON_TEXT).pack(side=tk.LEFT, padx=5)
    
    color_preview = tk.Frame(color_frame, width=30, height=20, bg=ColorConfig.current.GROUP_DEFAULT)
    color_preview.pack(side=tk.LEFT, padx=5)
    
    def choose_color():
        color = colorchooser.askcolor(color=color_preview["bg"])[1]
        if color:
            color_preview.config(bg=color)
    
    color_button = tk.Button(color_frame, text="Choose Color", 
                            bg=ColorConfig.current.BUTTON_BG, 
                            fg=ColorConfig.current.BUTTON_TEXT,
                            command=choose_color)
    color_button.pack(side=tk.LEFT, padx=5)
    
    # Buttons frame
    buttons_frame = tk.Frame(editor_frame, bg=ColorConfig.current.FRAME_BG)
    buttons_frame.pack(fill=tk.X, pady=10)
    
    def save_group():
        if gui_self.group_manager.selected_group:
            group = gui_self.group_manager.selected_group
            group.update_properties(
                name=name_entry.get(),
                color=color_preview["bg"]
            )
            gui_self.unsaved_changes = True
    
    save_button = tk.Button(buttons_frame, text="Save", 
                           bg=ColorConfig.current.BUTTON_BG, 
                           fg=ColorConfig.current.BUTTON_TEXT,
                           command=save_group)
    save_button.pack(side=tk.LEFT, padx=5)
    
    def delete_group():
        if gui_self.group_manager.selected_group:
            gui_self.group_manager.delete_group(gui_self.group_manager.selected_group)
            gui_self.unsaved_changes = True
            close_editor()
    
    delete_button = tk.Button(buttons_frame, text="Delete", 
                             bg=ColorConfig.current.BUTTON_BG, 
                             fg=ColorConfig.current.BUTTON_TEXT,
                             command=delete_group)
    delete_button.pack(side=tk.LEFT, padx=5)
    
    # If a group is provided, populate the fields
    if group:
        name_entry.delete(0, tk.END)
        name_entry.insert(0, group.name)
        color_preview.config(bg=group.color)
    
    # Add method to update the editor with a group
    def update_group_editor(group):
        if group and win.winfo_exists():
            name_entry.delete(0, tk.END)
            name_entry.insert(0, group.name)
            color_preview.config(bg=group.color)
    
    gui_self.update_group_editor = update_group_editor