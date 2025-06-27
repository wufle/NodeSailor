import tkinter as tk
from colors import ColorConfig
import os
import sys

if hasattr(sys, "frozen"):
    # Running as PyInstaller executable
    BASE_DIR = os.path.dirname(sys.executable)
    Nodesailor_settings_PATH = os.path.join(BASE_DIR, "Nodesailor_settings.txt")
else:
    # Running from source
    Nodesailor_settings_PATH = os.path.join("data", "Nodesailor_settings.txt")

def read_Nodesailor_settings():
    state = {}
    try:
        if os.path.exists(Nodesailor_settings_PATH):
            with open(Nodesailor_settings_PATH, "r") as f:
                for line in f:
                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        state[k] = v == "1"
    except Exception:
        # Fallback: return empty state if file is unreadable
        state = {}
    return state

def write_Nodesailor_settings(update):
    # update: dict of key(s) to update
    state = read_Nodesailor_settings()
    state.update(update)
    lines = []
    written = set()
    try:
        if os.path.exists(Nodesailor_settings_PATH):
            with open(Nodesailor_settings_PATH, "r") as f:
                for line in f:
                    if "=" in line:
                        k, _ = line.strip().split("=", 1)
                        if k in update:
                            lines.append(f"{k}={'1' if state[k] else '0'}\n")
                            written.add(k)
                        else:
                            lines.append(line)
                    else:
                        lines.append(line)
        # Add any new keys not already present
        for k in update:
            if k not in written:
                lines.append(f"{k}={'1' if state[k] else '0'}\n")
        # Ensure the directory exists before writing
        os.makedirs(os.path.dirname(Nodesailor_settings_PATH), exist_ok=True)
        with open(Nodesailor_settings_PATH, "w") as f:
            f.writelines(lines)
    except Exception:
        # Fail silently or log if needed; fallback is to do nothing
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
    state = read_Nodesailor_settings()
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
        write_Nodesailor_settings({"hide_operator_guidance": var.get()})
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
    state = read_Nodesailor_settings()
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
        write_Nodesailor_settings({"hide_configuration_guidance": var.get()})
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