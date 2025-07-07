import tkinter as tk
from colors import ColorConfig
import os
import sys

if hasattr(sys, "frozen"):
    # Running as PyInstaller executable
    BASE_DIR = os.path.dirname(sys.executable)
    NodeSailor_settings_PATH = os.path.join(BASE_DIR, "NodeSailor_settings.ini")
else:
    # Running from source
    NodeSailor_settings_PATH = os.path.join("data", "NodeSailor_settings.ini")

def read_NodeSailor_settings():
    state = {}
    try:
        if os.path.exists(NodeSailor_settings_PATH):
            with open(NodeSailor_settings_PATH, "r") as f:
                for line in f:
                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        # Handle boolean values for backward compatibility
                        if v in ("0", "1"):
                            state[k] = v == "1"
                        else:
                            # Handle string/path values
                            state[k] = v
    except Exception as e:
        # Fallback: return empty state if file is unreadable
        state = {}
    return state

def write_NodeSailor_settings(update):
    # update: dict of key(s) to update
    state = read_NodeSailor_settings()
    state.update(update)
    lines = []
    written = set()
    try:
        # Read existing lines if file exists, else start with empty
        if os.path.exists(NodeSailor_settings_PATH):
            with open(NodeSailor_settings_PATH, "r") as f:
                existing_lines = f.readlines()
        else:
            existing_lines = []

        # Track which keys have been written
        written = set()
        lines = []

        # Update existing keys in file
        for line in existing_lines:
            if "=" in line:
                k, _ = line.strip().split("=", 1)
                if k in update:
                    v = state[k]
                    if isinstance(v, bool):
                        lines.append(f"{k}={'1' if v else '0'}\n")
                    else:
                        lines.append(f"{k}={v}\n")
                    written.add(k)
                else:
                    lines.append(line)
            else:
                lines.append(line)

        # Add any new keys not already present
        for k in update:
            if k not in written:
                v = state[k]
                if isinstance(v, bool):
                    lines.append(f"{k}={'1' if v else '0'}\n")
                else:
                    lines.append(f"{k}={v}\n")

        # Ensure the directory exists before writing
        os.makedirs(os.path.dirname(NodeSailor_settings_PATH), exist_ok=True)
        with open(NodeSailor_settings_PATH, "w") as f:
            f.writelines(lines)
    except Exception:
        # Fail silently or log if needed; fallback is to do nothing
        pass

def _is_settings_file_complete():
    """
    Check if the existing settings file contains the expected structure.
    Returns True if the file is complete with proper sections and comments.
    Returns False if the file doesn't exist or is incomplete.
    """
    if not os.path.exists(NodeSailor_settings_PATH):
        return False
    
    try:
        with open(NodeSailor_settings_PATH, "r") as f:
            content = f.read()
        
        # Check for essential section headers and comments that indicate a complete file
        required_elements = [
            "# NodeSailor Configuration File",
            "# [FILES] - File Management Settings",
            "# [USER_INTERFACE] - UI Display Preferences",
            "# [WINDOW] - Window State and Positioning",
            "hide_operator_guidance=",
            "hide_configuration_guidance=",
            "HIDE_LEGEND="
        ]
        
        # File is considered complete if it contains all required elements
        for element in required_elements:
            if element not in content:
                return False
        
        return True
        
    except Exception:
        # If there's any error reading the file, consider it incomplete
        return False

def create_default_settings_file(force_recreate=False):
    """
    Creates a default NodeSailor_settings.ini file with all comments preserved.
    Only creates the file if it doesn't already exist or is incomplete.
    Uses default values suitable for new installations.
    
    Args:
        force_recreate (bool): If True, recreate the file even if it exists and is complete
    """
    # Check if file exists and is complete (unless force_recreate is True)
    if not force_recreate and _is_settings_file_complete():
        return
    
    try:
        # Ensure the directory exists before writing
        os.makedirs(os.path.dirname(NodeSailor_settings_PATH), exist_ok=True)
        
        # Preserve existing values if file exists
        existing_values = {}
        if os.path.exists(NodeSailor_settings_PATH):
            try:
                with open(NodeSailor_settings_PATH, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            existing_values[key.strip()] = value.strip()
            except Exception:
                pass  # If reading fails, proceed with defaults
        
        # Complete default content with all comments preserved
        # Use existing values where available, otherwise use defaults
        last_file_path = existing_values.get("LAST_FILE_PATH", "")
        hide_operator = existing_values.get("hide_operator_guidance", "0")
        hide_config = existing_values.get("hide_configuration_guidance", "0")
        hide_legend = existing_values.get("HIDE_LEGEND", "0")
        window_geometry = existing_values.get("WINDOW_GEOMETRY", "1200x800+100+100")
        
        default_content = f"""# NodeSailor Configuration File

# ==============================================================================
# [FILES] - File Management Settings
# ==============================================================================

# Last opened network file path
# Used to automatically reload the last project when NodeSailor starts
LAST_FILE_PATH={last_file_path}

# ==============================================================================
# [USER_INTERFACE] - UI Display Preferences
# ==============================================================================

# Hide operator guidance window on startup
hide_operator_guidance={hide_operator}

# Hide configuration guidance window on startup
hide_configuration_guidance={hide_config}

# Hide legend panel on startup
HIDE_LEGEND={hide_legend}

# ==============================================================================
# [WINDOW] - Window State and Positioning
# ==============================================================================

# Main window geometry (width x height + x_offset + y_offset)
# Format: WIDTHxHEIGHT+X+Y
# Example: 1800x900+100+50 means 1800px wide, 900px tall, positioned at (100,50)
WINDOW_GEOMETRY={window_geometry}

"""
        
        with open(NodeSailor_settings_PATH, "w") as f:
            f.write(default_content)
            
    except Exception:
        # Fail silently if file creation fails
        pass

def _setup_draggable_titlebar(win, title_bar, title_label):
    def start_drag(event):
        win._x = event.x
        win._y = event.y

    def do_drag(event):
        x = win.winfo_x() + event.x - win._x
        y = win.winfo_y() + event.y - win._y
        win.geometry(f"+{x}+{y}")

    title_bar.bind("<ButtonPress-1>", start_drag)
    title_bar.bind("<B1-Motion>", do_drag)
    title_label.bind("<ButtonPress-1>", start_drag)
    title_label.bind("<B1-Motion>", do_drag)

def _bring_to_front(win):
    win.lift()
    win.focus_set()
    win.attributes("-topmost", True)
    win.after(10, lambda: win.attributes("-topmost", False))

def show_operator_guidance(root, center_func=None, custom_font=None):
    state = read_NodeSailor_settings()
    if state.get("hide_operator_guidance", False):
        return

    win = tk.Toplevel(root)
    win.title("Operator Mode Guidance")
    win.overrideredirect(True)
    win.transient(root)

    # Outer border frame
    outer_frame = tk.Frame(win, bg=ColorConfig.current.BORDER_COLOR, padx=2, pady=2)
    outer_frame.pack(fill=tk.BOTH, expand=True)

    # Title bar
    title_bar = tk.Frame(outer_frame, bg=ColorConfig.current.INFO_NOTE_BG)
    title_bar.pack(side=tk.TOP, fill=tk.X)

    title_label = tk.Label(title_bar, text="Operator Mode Guidance",
                           bg=ColorConfig.current.INFO_NOTE_BG,
                           fg=ColorConfig.current.INFO_TEXT,
                           font=custom_font)
    title_label.pack(side=tk.LEFT, padx=10)

    close_button = tk.Button(
        title_bar, text='X',
        command=lambda: [win.destroy(), root.focus_force(), root.lift()],
        bg=ColorConfig.current.INFO_NOTE_BG,
        fg=ColorConfig.current.INFO_TEXT,
        font=custom_font
    )
    close_button.pack(side=tk.RIGHT)

    _setup_draggable_titlebar(win, title_bar, title_label)

    # Content frame
    content = tk.Frame(outer_frame, bg=ColorConfig.current.INFO_NOTE_BG)
    content.pack(fill=tk.BOTH, expand=True)

    # Screenshot viewer
    import os
    from PIL import Image, ImageTk

    screenshots_dir = os.path.join(os.path.dirname(__file__), "data", "screenshots", "operator_guidance")
    image_files = [f for f in os.listdir(screenshots_dir) if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp"))]
    image_files.sort()
    images = []
    for fname in image_files:
        img_path = os.path.join(screenshots_dir, fname)
        try:
            img = Image.open(img_path)
            img.thumbnail((500, 400), Image.Resampling.LANCZOS)
            images.append(img)
        except Exception:
            continue

    img_label = tk.Label(content, bg=ColorConfig.current.INFO_NOTE_BG)
    img_label.pack(pady=10)


    nav_frame = tk.Frame(content, bg=ColorConfig.current.INFO_NOTE_BG)
    nav_frame.pack(pady=(10, 0))

    current_idx = [0]
    tk_images = [None] * len(images)

    def show_image(idx):
        if not images:
            img_label.config(text="No screenshots found.", image="", width=60, height=10)
            return
        if tk_images[idx] is None:
            tk_images[idx] = ImageTk.PhotoImage(images[idx])
        img_label.config(image=tk_images[idx], text="")
        img_label.image = tk_images[idx]

    def prev_img():
        if images:
            current_idx[0] = (current_idx[0] - 1) % len(images)
            show_image(current_idx[0])

    def next_img():
        if images:
            current_idx[0] = (current_idx[0] + 1) % len(images)
            show_image(current_idx[0])

    prev_btn = tk.Button(nav_frame, text="Previous", command=prev_img,
                         bg=ColorConfig.current.INFO_NOTE_BG, fg=ColorConfig.current.INFO_TEXT, font=custom_font)
    prev_btn.pack(side=tk.LEFT, padx=10)
    next_btn = tk.Button(nav_frame, text="Next", command=next_img,
                         bg=ColorConfig.current.INFO_NOTE_BG, fg=ColorConfig.current.INFO_TEXT, font=custom_font)
    next_btn.pack(side=tk.LEFT, padx=10)

    show_image(current_idx[0])

    var = tk.BooleanVar(value=False)
    def on_check():
        write_NodeSailor_settings({"hide_operator_guidance": var.get()})
    cb = tk.Checkbutton(content, text="Don't display this window again", variable=var,
                        command=on_check, bg=ColorConfig.current.INFO_NOTE_BG,
                        fg=ColorConfig.current.INFO_TEXT, selectcolor=ColorConfig.current.INFO_NOTE_BG,
                        font=("Arial", 8),
                        activebackground=ColorConfig.current.INFO_NOTE_BG)
    cb.pack(anchor="w", pady=(16, 0))

    win.bind('<Escape>', lambda e: win.destroy())

    win.update_idletasks()
    _bring_to_front(win)
    if center_func:
        center_func(win)

def show_configuration_guidance(root, center_func=None, custom_font=None):
    state = read_NodeSailor_settings()
    if state.get("hide_configuration_guidance", False):
        return

    win = tk.Toplevel(root)
    win.title("Configuration Mode Guidance")
    win.overrideredirect(True)
    win.transient(root)

    # Outer border frame
    outer_frame = tk.Frame(win, bg=ColorConfig.current.BORDER_COLOR, padx=2, pady=2)
    outer_frame.pack(fill=tk.BOTH, expand=True)

    # Title bar
    title_bar = tk.Frame(outer_frame, bg=ColorConfig.current.INFO_NOTE_BG)
    title_bar.pack(side=tk.TOP, fill=tk.X)

    title_label = tk.Label(title_bar, text="Configuration Mode Guidance",
                           bg=ColorConfig.current.INFO_NOTE_BG,
                           fg=ColorConfig.current.INFO_TEXT,
                           font=custom_font)
    title_label.pack(side=tk.LEFT, padx=10)

    close_button = tk.Button(
        title_bar, text='X',
        command=lambda: [win.destroy(), root.focus_force(), root.lift()],
        bg=ColorConfig.current.INFO_NOTE_BG,
        fg=ColorConfig.current.INFO_TEXT,
        font=custom_font
    )
    close_button.pack(side=tk.RIGHT)

    _setup_draggable_titlebar(win, title_bar, title_label)

    content = tk.Frame(outer_frame, bg=ColorConfig.current.INFO_NOTE_BG)
    content.pack(fill=tk.BOTH, expand=True)

    import os
    from PIL import Image, ImageTk

    screenshots_dir = os.path.join(os.path.dirname(__file__), "data", "screenshots", "configuration_guidance")
    image_files = [f for f in os.listdir(screenshots_dir) if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp"))]
    image_files.sort()
    images = []
    for fname in image_files:
        img_path = os.path.join(screenshots_dir, fname)
        try:
            img = Image.open(img_path)
            img.thumbnail((500, 400), Image.Resampling.LANCZOS)
            images.append(img)
        except Exception:
            continue

    img_label = tk.Label(content, bg=ColorConfig.current.INFO_NOTE_BG)
    img_label.pack(pady=10)

    nav_frame = tk.Frame(content, bg=ColorConfig.current.INFO_NOTE_BG)
    nav_frame.pack(pady=(10, 0))

    current_idx = [0]
    tk_images = [None] * len(images)

    def show_image(idx):
        if not images:
            img_label.config(text="No screenshots found.", image="", width=60, height=10)
            return
        if tk_images[idx] is None:
            tk_images[idx] = ImageTk.PhotoImage(images[idx])
        img_label.config(image=tk_images[idx], text="")
        img_label.image = tk_images[idx]

    def prev_img():
        if images:
            current_idx[0] = (current_idx[0] - 1) % len(images)
            show_image(current_idx[0])

    def next_img():
        if images:
            current_idx[0] = (current_idx[0] + 1) % len(images)
            show_image(current_idx[0])

    prev_btn = tk.Button(nav_frame, text="Previous", command=prev_img,
                         bg=ColorConfig.current.INFO_NOTE_BG, fg=ColorConfig.current.INFO_TEXT, font=custom_font)
    prev_btn.pack(side=tk.LEFT, padx=10)
    next_btn = tk.Button(nav_frame, text="Next", command=next_img,
                         bg=ColorConfig.current.INFO_NOTE_BG, fg=ColorConfig.current.INFO_TEXT, font=custom_font)
    next_btn.pack(side=tk.LEFT, padx=10)

    show_image(current_idx[0])

    var = tk.BooleanVar(value=False)
    def on_check():
        write_NodeSailor_settings({"hide_configuration_guidance": var.get()})
    cb = tk.Checkbutton(content, text="Don't display this window again", variable=var,
                        command=on_check, bg=ColorConfig.current.INFO_NOTE_BG,
                        fg=ColorConfig.current.INFO_TEXT, selectcolor=ColorConfig.current.INFO_NOTE_BG,
                        font=("Arial", 8),
                        activebackground=ColorConfig.current.BUTTON_ACTIVE_BG)
    cb.pack(anchor="w", pady=(16, 0))

    win.bind('<Escape>', lambda e: win.destroy())

    win.update_idletasks()
    _bring_to_front(win)
    if center_func:
        center_func(win)