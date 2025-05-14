import tkinter as tk
from colors import ColorConfig
import os

LEGEND_STATE_PATH = "_internal/legend_state.txt"

def read_legend_state():
    state = {}
    if os.path.exists(LEGEND_STATE_PATH):
        with open(LEGEND_STATE_PATH, "r") as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    state[k] = v == "1"
    return state

def write_legend_state(state):
    with open(LEGEND_STATE_PATH, "w") as f:
        for k, v in state.items():
            f.write(f"{k}={'1' if v else '0'}\n")

def _center_and_drag_window(win, root, title_bar, title_label):
    # Center window on screen
    win.update_idletasks()
    w, h = win.winfo_width(), win.winfo_height()
    x = root.winfo_x() + (root.winfo_width() - w) // 2
    y = root.winfo_y() + (root.winfo_height() - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")
    win.lift()
    win.focus_set()

    # Drag logic
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

def show_operator_guidance(root):
    state = read_legend_state()
    if state.get("hide_operator_guidance", False):
        return

    win = tk.Toplevel(root)
    win.title("Operator Mode Guidance")
    win.overrideredirect(True)
    win.transient(root)

    # Outer border frame
    outer = tk.Frame(win, bg=ColorConfig.current.BORDER_COLOR, padx=2, pady=2)
    outer.pack(fill=tk.BOTH, expand=True)

    # Title bar
    title_bar = tk.Frame(outer, bg=ColorConfig.current.FRAME_BG)
    title_bar.pack(side=tk.TOP, fill=tk.X)

    # Use a default font if custom_font is not available
    font = ("Arial", 11, "bold")

    title_label = tk.Label(title_bar, text="Operator Mode Guidance",
                           bg=ColorConfig.current.FRAME_BG,
                           fg=ColorConfig.current.BUTTON_TEXT,
                           font=font)
    title_label.pack(side=tk.LEFT, padx=10)

    close_button = tk.Button(
        title_bar, text='X',
        command=win.destroy,
        bg=ColorConfig.current.FRAME_BG,
        fg=ColorConfig.current.BUTTON_TEXT,
        font=font
    )
    close_button.pack(side=tk.RIGHT)

    # Content frame
    content = tk.Frame(outer, bg=ColorConfig.current.INFO_NOTE_BG)
    content.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

    # Operator Mode guidance text (from show_help)
    tk.Label(content, text="Operator Mode:", bg=ColorConfig.current.INFO_NOTE_BG,
             fg=ColorConfig.current.INFO_TEXT, font=font).pack(anchor="w", pady=(0, 4))
    tk.Label(content, text="- Left Click on Node: Ping the node (Green = all assigned IP addresses connected, Yellow = partial connection, Red = no connection).",
             bg=ColorConfig.current.INFO_NOTE_BG, fg=ColorConfig.current.INFO_TEXT, wraplength=420, justify="left").pack(anchor="w")

    # Checkbox
    var = tk.BooleanVar(value=False)
    def on_check():
        state["hide_operator_guidance"] = var.get()
        write_legend_state(state)
    cb = tk.Checkbutton(content, text="Don't display this window again", variable=var,
                        command=on_check, bg=ColorConfig.current.FRAME_BG,
                        fg=ColorConfig.current.BUTTON_TEXT, selectcolor=ColorConfig.current.FRAME_BG,
                        activebackground=ColorConfig.current.BUTTON_ACTIVE_BG, font=font)
    cb.pack(anchor="w", pady=(16, 0))

    win.bind('<Escape>', lambda e: win.destroy())
    _center_and_drag_window(win, root, title_bar, title_label)

def show_configuration_guidance(root):
    state = read_legend_state()
    if state.get("hide_configuration_guidance", False):
        return

    win = tk.Toplevel(root)
    win.title("Configuration Mode Warning")
    win.overrideredirect(True)
    win.transient(root)

    # Outer border frame
    outer = tk.Frame(win, bg=ColorConfig.current.BORDER_COLOR, padx=2, pady=2)
    outer.pack(fill=tk.BOTH, expand=True)

    # Title bar
    title_bar = tk.Frame(outer, bg=ColorConfig.current.FRAME_BG)
    title_bar.pack(side=tk.TOP, fill=tk.X)

    font = ("Arial", 11, "bold")

    title_label = tk.Label(title_bar, text="Configuration Mode",
                           bg=ColorConfig.current.FRAME_BG,
                           fg=ColorConfig.current.BUTTON_TEXT,
                           font=font)
    title_label.pack(side=tk.LEFT, padx=10)

    close_button = tk.Button(
        title_bar, text='X',
        command=win.destroy,
        bg=ColorConfig.current.FRAME_BG,
        fg=ColorConfig.current.BUTTON_TEXT,
        font=font
    )
    close_button.pack(side=tk.RIGHT)

    # Content frame
    content = tk.Frame(outer, bg=ColorConfig.current.INFO_NOTE_BG)
    content.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

    # Warning text
    tk.Label(content, text="Warning:", bg=ColorConfig.current.INFO_NOTE_BG,
             fg=ColorConfig.current.INFO_TEXT, font=font).pack(anchor="w", pady=(0, 4))
    tk.Label(content, text="This mode should only be used when creating/editing a node map.",
             bg=ColorConfig.current.INFO_NOTE_BG, fg=ColorConfig.current.INFO_TEXT, wraplength=420, justify="left").pack(anchor="w")

    # Checkbox
    var = tk.BooleanVar(value=False)
    def on_check():
        state["hide_configuration_guidance"] = var.get()
        write_legend_state(state)
    cb = tk.Checkbutton(content, text="Don't display this window again", variable=var,
                        command=on_check, bg=ColorConfig.current.FRAME_BG,
                        fg=ColorConfig.current.BUTTON_TEXT, selectcolor=ColorConfig.current.FRAME_BG,
                        activebackground=ColorConfig.current.BUTTON_ACTIVE_BG, font=font)
    cb.pack(anchor="w", pady=(16, 0))

    win.bind('<Escape>', lambda e: win.destroy())
    _center_and_drag_window(win, root, title_bar, title_label)