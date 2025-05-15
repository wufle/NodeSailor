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

def write_legend_state(update):
    # update: dict of key(s) to update
    state = read_legend_state()
    state.update(update)
    lines = []
    written = set()
    if os.path.exists(LEGEND_STATE_PATH):
        with open(LEGEND_STATE_PATH, "r") as f:
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
    with open(LEGEND_STATE_PATH, "w") as f:
        f.writelines(lines)

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
    state = read_legend_state()
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

    # Guidance lines copied from gui.py help_lines
    help_lines = [
        ("\nOperator Mode:\n", "header"),
        ("- Left Click on Node: Ping the node (Green = all assigned IP addresses connected, Yellow = partial connection, Red = no connection).\n"
         "- Right Click on Node: Open context menu.\n"
         "- Right Click and Drag: Pan the canvas.\n"
         "- Scroll Wheel: Zoom in and out.\n"
         "- Who am I?: Highlight the node matching your machine's IP.\n"
         "- Ping All: Ping every node.\n"
         "- Clear Status: Reset node status.\n", "text"),

        ("- Ctrl-Shift-C Change color theme.\n", "text"),
    ]

    for line, tag in help_lines:
        if tag == "title":
            tk.Label(content, text=line, bg=ColorConfig.current.INFO_NOTE_BG,
                     fg=ColorConfig.current.INFO_TEXT, font=custom_font, anchor="w", justify="left", wraplength=420).pack(anchor="w", pady=(0, 8))
        elif tag == "header":
            tk.Label(content, text=line, bg=ColorConfig.current.INFO_NOTE_BG,
                     fg=ColorConfig.current.INFO_TEXT, font=custom_font, anchor="w", justify="left", wraplength=420).pack(anchor="w", pady=(8, 0))
        else:
            tk.Label(content, text=line, bg=ColorConfig.current.INFO_NOTE_BG,
                     fg=ColorConfig.current.INFO_TEXT, font=custom_font, anchor="w", justify="left", wraplength=420).pack(anchor="w")

    var = tk.BooleanVar(value=False)
    def on_check():
        write_legend_state({"hide_operator_guidance": var.get()})
    cb = tk.Checkbutton(content, text="Don't display this window again", variable=var,
                        command=on_check, bg=ColorConfig.current.INFO_NOTE_BG,
                        fg=ColorConfig.current.INFO_TEXT, selectcolor=ColorConfig.current.INFO_NOTE_BG,
                        activebackground=ColorConfig.current.INFO_NOTE_BG, font=custom_font)
    cb.pack(anchor="w", pady=(16, 0))

    win.bind('<Escape>', lambda e: win.destroy())

    win.update_idletasks()
    _bring_to_front(win)
    if center_func:
        center_func(win)

def show_configuration_guidance(root, center_func=None, custom_font=None):
    state = read_legend_state()
    if state.get("hide_configuration_guidance", False):
        return

    win = tk.Toplevel(root)
    win.title("Configuration Mode Warning")
    win.overrideredirect(True)
    win.transient(root)

    # Outer border frame
    outer_frame = tk.Frame(win, bg=ColorConfig.current.BORDER_COLOR, padx=2, pady=2)
    outer_frame.pack(fill=tk.BOTH, expand=True)

    # Title bar
    title_bar = tk.Frame(outer_frame, bg=ColorConfig.current.INFO_NOTE_BG)
    title_bar.pack(side=tk.TOP, fill=tk.X)

    title_label = tk.Label(title_bar, text="Configuration Mode",
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

    tk.Label(content, text="Warning:", bg=ColorConfig.current.INFO_NOTE_BG,
             fg=ColorConfig.current.INFO_TEXT, font=custom_font).pack(anchor="w", pady=(0, 4))
    tk.Label(content, text="This mode should only be used when creating/editing a node map.",
             bg=ColorConfig.current.INFO_NOTE_BG, fg=ColorConfig.current.INFO_TEXT, wraplength=420, justify="left", font=custom_font).pack(anchor="w")

    var = tk.BooleanVar(value=False)
    def on_check():
        write_legend_state({"hide_configuration_guidance": var.get()})
    cb = tk.Checkbutton(content, text="Don't display this window again", variable=var,
                        command=on_check, bg=ColorConfig.current.INFO_NOTE_BG,
                        fg=ColorConfig.current.INFO_TEXT, selectcolor=ColorConfig.current.INFO_NOTE_BG,
                        activebackground=ColorConfig.current.BUTTON_ACTIVE_BG, font=custom_font)
    cb.pack(anchor="w", pady=(16, 0))

    win.bind('<Escape>', lambda e: win.destroy())

    win.update_idletasks()
    _bring_to_front(win)
    if center_func:
        center_func(win)