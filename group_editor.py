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
        gui_self.regain_focus()  # Regain focus to the main window
    
    # Create the popup window
    win, content = gui_self.create_popup(
        "Group Editor", 300, 360,
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
    
    # Preset color sets
    color_presets = [
        {
            "id": "preset1",
            "name": "Classic Blue",
            "light_bg": "#e3f0ff",
            "light_border": "#3a7bd5",
            "dark_bg": "#22304a",
            "dark_border": "#3a7bd5"
        },
        {
            "id": "preset2",
            "name": "Sunset",
            "light_bg": "#ffe5d0",
            "light_border": "#ff7f50",
            "dark_bg": "#4a2c23",
            "dark_border": "#ff7f50"
        },
        {
            "id": "preset3",
            "name": "Mint",
            "light_bg": "#e0fff4",
            "light_border": "#2ecc71",
            "dark_bg": "#204034",
            "dark_border": "#2ecc71"
        },
        {
            "id": "preset4",
            "name": "Lavender",
            "light_bg": "#f3e8ff",
            "light_border": "#a259e6",
            "dark_bg": "#2d234a",
            "dark_border": "#a259e6"
        },
        {
            "id": "preset5",
            "name": "Slate",
            "light_bg": "#f0f4f8",
            "light_border": "#607d8b",
            "dark_bg": "#232b32",
            "dark_border": "#607d8b"
        },
        {
            "id": "preset6",
            "name": "Contrast",
            "light_bg": "#ffffff",
            "light_border": "#000000",
            "dark_bg": "#000000",
            "dark_border": "#ffffff"
        }
    ]

    preset_var = tk.StringVar()
    preset_var.set(color_presets[0]["id"])

    # Ensure UI always reflects the current value of preset_var
    def on_preset_var_change(*args):
        # This callback is triggered on any change to preset_var
        # Tkinter Radiobuttons automatically update, but this ensures any additional UI sync if needed
        win.update_idletasks()  # Force UI update to keep radio selection in sync

    preset_var.trace_add("write", on_preset_var_change)

    def is_valid_preset_id(preset_id):
        return any(p["id"] == preset_id for p in color_presets)

    def select_preset(preset_id):
        if is_valid_preset_id(preset_id):
            preset_var.set(preset_id)
        else:
            preset_var.set(color_presets[0]["id"])

    # Preset selection UI
    presets_frame = tk.LabelFrame(editor_frame, text="Color Presets", bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT)
    presets_frame.pack(fill=tk.X, pady=8)

    for preset in color_presets:
        row = tk.Frame(presets_frame, bg=ColorConfig.current.FRAME_BG)
        row.pack(fill=tk.X, pady=2)
        # Determine correct select color and active background for current color scheme
        if ColorConfig.current is getattr(ColorConfig, "Dark", None):
            radio_color = preset["dark_bg"]
        else:
            radio_color = preset["light_bg"]
        rb = tk.Radiobutton(
            row, variable=preset_var, value=preset["id"],
            bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT,
            selectcolor=radio_color, activebackground=radio_color
        )
        rb.pack(side=tk.LEFT, padx=5)
        # Visual preview
        preview = tk.Frame(row, width=30, height=20, bg=preset["light_bg"], bd=2, relief=tk.SOLID)
        preview.pack(side=tk.LEFT, padx=2)
        border_preview = tk.Frame(row, width=30, height=20, bg=preset["light_border"], bd=2, relief=tk.SOLID)
        border_preview.pack(side=tk.LEFT, padx=2)
        dark_preview = tk.Frame(row, width=30, height=20, bg=preset["dark_bg"], bd=2, relief=tk.SOLID)
        dark_preview.pack(side=tk.LEFT, padx=2)
        dark_border_preview = tk.Frame(row, width=30, height=20, bg=preset["dark_border"], bd=2, relief=tk.SOLID)
        dark_border_preview.pack(side=tk.LEFT, padx=2)
        tk.Label(row, text=preset["name"], bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT).pack(side=tk.LEFT, padx=8)
    
    # Buttons frame
    buttons_frame = tk.Frame(editor_frame, bg=ColorConfig.current.FRAME_BG)
    buttons_frame.pack(fill=tk.X, pady=10)
    
    def save_group():
        if gui_self.group_manager.selected_group:
            group = gui_self.group_manager.selected_group
            selected_preset_id = preset_var.get()
            # Ensure selected_preset_id is valid
            if not is_valid_preset_id(selected_preset_id):
                selected_preset_id = color_presets[0]["id"]
                preset_var.set(selected_preset_id)
            group.update_properties(
                name=name_entry.get(),
                color_preset_id=selected_preset_id
            )
            gui_self.unsaved_changes = True
            # After saving, ensure preset_var is still valid
            if not is_valid_preset_id(preset_var.get()):
                preset_var.set(color_presets[0]["id"])
    
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
        # Set preset selection if available
        if hasattr(group, "color_preset_id") and group.color_preset_id and is_valid_preset_id(group.color_preset_id):
            preset_var.set(group.color_preset_id)
        else:
            preset_var.set(color_presets[0]["id"])
        win.after(100, lambda: name_entry.focus_force())  # Ensure focus after populating
    
    # Add method to update the editor with a group
    def update_group_editor(group):
        if group and win.winfo_exists():
            name_entry.delete(0, tk.END)
            name_entry.insert(0, group.name)
            # Always update the radio button selection via preset_var.set
            if hasattr(group, "color_preset_id") and group.color_preset_id:
                if is_valid_preset_id(group.color_preset_id):
                    preset_var.set(group.color_preset_id)
                else:
                    preset_var.set(color_presets[0]["id"])
                win.after(100, lambda: name_entry.focus_force())  # Ensure focus when updating
    
    gui_self.update_group_editor = update_group_editor