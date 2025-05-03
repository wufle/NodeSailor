import tkinter as tk
from tkinter import colorchooser

def open_group_editor(gui_self, group=None):
    ColorConfig = gui_self.ColorConfig if hasattr(gui_self, "ColorConfig") else __import__("colors").ColorConfig
    
    # Close any existing group editor window to ensure a clean state
    if getattr(gui_self, 'group_editor_window', None) and gui_self.group_editor_window.winfo_exists():
        gui_self.group_editor_window.destroy()
        gui_self.group_editor_window = None
    
    # Close the legend window if it exists
    if getattr(gui_self, 'legend_window', None) and gui_self.legend_window.winfo_exists():
        gui_self.legend_window.destroy()
        gui_self.legend_window = None
    
    def close_editor():
        try:
            gui_self.group_editor_window.grab_release()
        except:
            pass
        gui_self.group_editor_window.destroy()
        gui_self.group_editor_window = None
        gui_self.root.focus_force()  # Restore focus to the main window
    
    # Create the popup window
    win, content = gui_self.create_popup(
        "Group Editor", 400, 300,
        on_close=close_editor,
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
    
    # Explicitly set focus after a short delay to ensure the window is fully rendered
    win.after(100, lambda: name_entry.focus_force())
    
    # Group colors (four pickers)
    color_labels = [
        ("Light BG", "light_bg"),
        ("Light Border", "light_border"),
        ("Dark BG", "dark_bg"),
        ("Dark Border", "dark_border"),
    ]
    color_defaults = {
        "light_bg": ColorConfig.current.GROUP_DEFAULT if hasattr(ColorConfig.current, "GROUP_DEFAULT") else "#ffffff",
        "light_border": ColorConfig.current.GROUP_OUTLINE if hasattr(ColorConfig.current, "GROUP_OUTLINE") else "#000000",
        "dark_bg": "#222222",
        "dark_border": "#888888",
    }
    color_frames = {}
    color_previews = {}

    for label, key in color_labels:
        frame = tk.Frame(editor_frame, bg=ColorConfig.current.FRAME_BG)
        frame.pack(fill=tk.X, pady=2)
        tk.Label(frame, text=f"{label}:", bg=ColorConfig.current.FRAME_BG,
                 fg=ColorConfig.current.BUTTON_TEXT).pack(side=tk.LEFT, padx=5)
        preview = tk.Frame(frame, width=30, height=20, bg=color_defaults[key])
        preview.pack(side=tk.LEFT, padx=5)
        def make_choose_color(preview_ref):
            return lambda: (
                (color := colorchooser.askcolor(color=preview_ref["bg"])[1]) and preview_ref.config(bg=color)
            )
        btn = tk.Button(frame, text="Choose Color",
                        bg=ColorConfig.current.BUTTON_BG,
                        fg=ColorConfig.current.BUTTON_TEXT,
                        command=make_choose_color(preview))
        btn.pack(side=tk.LEFT, padx=5)
        color_frames[key] = frame
        color_previews[key] = preview
    
    # Buttons frame
    buttons_frame = tk.Frame(editor_frame, bg=ColorConfig.current.FRAME_BG)
    buttons_frame.pack(fill=tk.X, pady=10)
    
    def save_group():
        if gui_self.group_manager.selected_group:
            group = gui_self.group_manager.selected_group
            group.update_properties(
                name=name_entry.get(),
                light_bg=color_previews["light_bg"]["bg"],
                light_border=color_previews["light_border"]["bg"],
                dark_bg=color_previews["dark_bg"]["bg"],
                dark_border=color_previews["dark_border"]["bg"],
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
    
    delete_button = tk.Button(buttons_frame, text="Delete", 
                             bg=ColorConfig.current.BUTTON_BG, 
                             fg=ColorConfig.current.BUTTON_TEXT,
                             command=delete_group)
    delete_button.pack(side=tk.LEFT, padx=5)
    
    # If a group is provided, populate the fields
    if group:
        name_entry.delete(0, tk.END)
        name_entry.insert(0, group.name)
        # Populate color pickers
        color_previews["light_bg"].config(bg=getattr(group, "light_bg", color_defaults["light_bg"]))
        color_previews["light_border"].config(bg=getattr(group, "light_border", color_defaults["light_border"]))
        color_previews["dark_bg"].config(bg=getattr(group, "dark_bg", color_defaults["dark_bg"]))
        color_previews["dark_border"].config(bg=getattr(group, "dark_border", color_defaults["dark_border"]))
        win.after(100, lambda: name_entry.focus_force())  # Ensure focus after populating
    
    # Add method to update the editor with a group
    def update_group_editor(group):
        if group and win.winfo_exists():
            name_entry.delete(0, tk.END)
            name_entry.insert(0, group.name)
            color_previews["light_bg"].config(bg=getattr(group, "light_bg", color_defaults["light_bg"]))
            color_previews["light_border"].config(bg=getattr(group, "light_border", color_defaults["light_border"]))
            color_previews["dark_bg"].config(bg=getattr(group, "dark_bg", color_defaults["dark_bg"]))
            color_previews["dark_border"].config(bg=getattr(group, "dark_border", color_defaults["dark_border"]))
            win.after(100, lambda: name_entry.focus_force())  # Ensure focus when updating
    
    gui_self.update_group_editor = update_group_editor