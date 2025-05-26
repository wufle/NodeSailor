import tkinter as tk
from tkinter import colorchooser, simpledialog, messagebox
import json
import os

DEFAULT_HEIGHT = 460
DEFAULT_PRESETS = [
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

__all__ = ["DEFAULT_HEIGHT", "DEFAULT_PRESETS"]


def open_group_editor(gui_self, group=None, color_presets=None, window_height=None):
    ColorConfig = gui_self.ColorConfig if hasattr(gui_self, "ColorConfig") else __import__("colors").ColorConfig

    # --- Persistence Setup ---
    CONFIG_PATH = "group_editor_config.json"

    def load_config():
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r") as f:
                    data = json.load(f)
                    return data.get("color_presets", DEFAULT_PRESETS), data.get("window_height", DEFAULT_HEIGHT)
            except Exception:
                return DEFAULT_PRESETS, DEFAULT_HEIGHT
        return DEFAULT_PRESETS, DEFAULT_HEIGHT

    def save_config(presets, height):
        try:
            with open(CONFIG_PATH, "w") as f:
                json.dump({"color_presets": presets, "window_height": height}, f, indent=2)
        except Exception as e:
            print("Failed to save group editor config:", e)

    # Use provided values if present, else fall back to config/defaults
    if color_presets is None or color_presets is False:
        color_presets, _ = load_config()
    if window_height is None or window_height is False:
        _, window_height = load_config()

    # --- End Persistence Setup ---

    # Close any existing group editor window to ensure a clean state
    if getattr(gui_self, 'group_editor_window', None) and gui_self.group_editor_window.winfo_exists():
        gui_self.group_editor_window.destroy()
        gui_self.group_editor_window = None

    # Close the legend window if it exists
    if getattr(gui_self, 'legend_window', None) and gui_self.legend_window.winfo_exists():
        gui_self.legend_window.destroy()
        gui_self.legend_window = None

    def close_editor():
        # Ensure resize mode is disabled and all handles are hidden when closing the editor
        gui_self.group_resize_mode_active = False
        if hasattr(gui_self, "group_manager"):
            for group in getattr(gui_self.group_manager, "groups", []):
                group.update_properties(resize_mode_active=False)
                if hasattr(group, "remove_handles"):
                    group.remove_handles()
        try:
            gui_self.group_editor_window.grab_release()
        except:
            pass
        gui_self.group_editor_window.destroy()
        gui_self.group_editor_window = None
        gui_self.regain_focus()  # Regain focus to the main window

    # Create the popup window with persisted height
    win, content = gui_self.create_popup(
        "Group Editor", 300, window_height,
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

    # --- Add New Color Set Button ---
    def add_color_set():
        dialog = tk.Toplevel(win)
        dialog.title("Add New Color Set")
        dialog.geometry("350x320")
        dialog.transient(win)
        dialog.grab_set()
        dialog.resizable(False, False)
        fields = {}

        def pick_color(entry):
            color = colorchooser.askcolor()[1]
            if color:
                entry.delete(0, tk.END)
                entry.insert(0, color)

        tk.Label(dialog, text="Preset Name:").pack(pady=5)
        name_e = tk.Entry(dialog)
        name_e.pack(pady=2)
        fields["name"] = name_e

        color_fields = [
            ("Light BG", "light_bg"),
            ("Light Border", "light_border"),
            ("Dark BG", "dark_bg"),
            ("Dark Border", "dark_border"),
        ]
        for label, key in color_fields:
            frame = tk.Frame(dialog)
            frame.pack(pady=3)
            tk.Label(frame, text=label + ":").pack(side=tk.LEFT)
            entry = tk.Entry(frame, width=12)
            entry.pack(side=tk.LEFT, padx=2)
            btn = tk.Button(frame, text="Pick", command=lambda e=entry: pick_color(e))
            btn.pack(side=tk.LEFT)
            fields[key] = entry

        def submit():
            name = fields["name"].get().strip()
            if not name:
                messagebox.showerror("Error", "Preset name required.")
                return
            # Generate unique id
            preset_id = "custom_" + str(len(color_presets) + 1)
            preset = {
                "id": preset_id,
                "name": name,
                "light_bg": fields["light_bg"].get().strip() or "#ffffff",
                "light_border": fields["light_border"].get().strip() or "#000000",
                "dark_bg": fields["dark_bg"].get().strip() or "#000000",
                "dark_border": fields["dark_border"].get().strip() or "#ffffff",
            }
            color_presets.append(preset)
            # Increase window height by 40px per new color set
            nonlocal window_height
            window_height += 40
            save_config(color_presets, window_height)
            dialog.destroy()
            win.destroy()
            # Reopen editor at new height
            open_group_editor(gui_self, group)

        submit_btn = tk.Button(dialog, text="Add Color Set", command=submit)
        submit_btn.pack(pady=12)
        cancel_btn = tk.Button(dialog, text="Cancel", command=dialog.destroy)
        cancel_btn.pack()
        dialog.wait_window()

    # --- End Add New Color Set Button ---

    # Preset color sets (now dynamic)
    preset_var = tk.StringVar()
    preset_var.set(color_presets[0]["id"] if color_presets else "")

    # Ensure UI always reflects the current value of preset_var
    def on_preset_var_change(*args):
        # Update the group's color_preset_id and refresh rectangle colors
        selected_preset_id = preset_var.get()
        if group is not None and hasattr(group, "update_properties"):
            group.update_properties(color_preset_id=selected_preset_id, color_presets=color_presets)
            update_group_editor(group)
            # Force canvas redraw for instant visual feedback after color change
            if hasattr(gui_self, "canvas") and gui_self.canvas is not None:
                gui_self.canvas.update_idletasks()
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

    # Add "New Color Set" button at the bottom
    add_color_btn = tk.Button(presets_frame, text="New Color Set", command=add_color_set, bg=ColorConfig.current.BUTTON_BG, fg=ColorConfig.current.BUTTON_TEXT)
    add_color_btn.pack(fill=tk.X, pady=4)

    # Buttons frame
    buttons_frame = tk.Frame(editor_frame, bg=ColorConfig.current.FRAME_BG)
    buttons_frame.pack(fill=tk.X, pady=10)

    # --- Resize Mode State ---
    if not hasattr(gui_self, "group_resize_mode_active"):
        gui_self.group_resize_mode_active = False

    # --- Resize Mode UI Update ---
    def update_resize_mode_ui():
        if gui_self.group_resize_mode_active:
            resize_button["bg"] = ColorConfig.current.BUTTON_CONFIGURATION_MODE
        else:
            resize_button["bg"] = ColorConfig.current.BUTTON_BG

    # --- Resize Mode Toggle Logic ---
    def toggle_resize_mode():
        gui_self.group_resize_mode_active = not gui_self.group_resize_mode_active
        update_resize_mode_ui()
        # Update resize_mode_active for all RectangleGroup instances
        for group in getattr(gui_self.group_manager, "groups", []):
            group.update_properties(resize_mode_active=gui_self.group_resize_mode_active)
        # When entering resize mode, disable drawing/selecting groups
        # When exiting, restore normal behavior
        # Optionally, change cursor or provide other visual cues
        if gui_self.group_resize_mode_active:
            # Optionally change cursor to indicate resize mode
            gui_self.canvas.config(cursor="tcross")
        else:
            gui_self.canvas.config(cursor="")

    resize_button = tk.Button(
        buttons_frame,
        text="Resize",
        bg=ColorConfig.current.BUTTON_BG,
        fg=ColorConfig.current.BUTTON_TEXT,
        command=toggle_resize_mode
    )
    resize_button.pack(side=tk.LEFT, padx=5)

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
                color_preset_id=selected_preset_id,
                color_presets=color_presets
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

    # Ensure UI reflects initial state
    update_resize_mode_ui()
    
    def delete_group():
        if gui_self.group_manager.selected_group:
            gui_self.group_manager.delete_group(gui_self.group_manager.selected_group)
            gui_self.unsaved_changes = True

    delete_button = tk.Button(buttons_frame, text="Delete",
                             bg=ColorConfig.current.BUTTON_BG,
                             fg=ColorConfig.current.BUTTON_TEXT,
                             command=delete_group)
    delete_button.pack(side=tk.LEFT, padx=5)

    # --- Patch group manager event handlers to respect resize mode ---
    # Only allow handle interaction when in resize mode
    orig_start_drawing = gui_self.group_manager.start_drawing
    orig_update_drawing = gui_self.group_manager.update_drawing
    orig_finish_drawing = getattr(gui_self.group_manager, "finish_drawing", None)
    orig_select_group = getattr(gui_self.group_manager, "select_group", None)

    def patched_start_drawing(event):
        if getattr(gui_self, "group_resize_mode_active", False):
            return
        orig_start_drawing(event)
    def patched_update_drawing(event):
        if getattr(gui_self, "group_resize_mode_active", False):
            return
        orig_update_drawing(event)
    def patched_finish_drawing(event):
        if getattr(gui_self, "group_resize_mode_active", False):
            return
        if orig_finish_drawing:
            orig_finish_drawing(event)
    def patched_select_group(event):
        if getattr(gui_self, "group_resize_mode_active", False):
            return
        if orig_select_group:
            orig_select_group(event)

    gui_self.group_manager.start_drawing = patched_start_drawing
    gui_self.group_manager.update_drawing = patched_update_drawing
    if orig_finish_drawing:
        gui_self.group_manager.finish_drawing = patched_finish_drawing
    if orig_select_group:
        gui_self.group_manager.select_group = patched_select_group
    
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
        # Ensure only the selected group displays handles
        if hasattr(gui_self, "group_manager"):
            for g in getattr(gui_self.group_manager, "groups", []):
                if (
                    g is group
                    and group
                    and getattr(gui_self, "group_resize_mode_active", False)
                    and win.winfo_exists()
                ):
                    g.show_handles()
                else:
                    g.remove_handles()
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