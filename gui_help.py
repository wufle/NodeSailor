import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from colors import ColorConfig

def show_help_window(gui, event=None):
    """
    Creates a help window with a scrollable text area that displays
    the application's help information.
    :param gui: The main GUI instance (NetworkMapGUI)
    :param event: Unused
    """
    help_window = tk.Toplevel(gui.root)
    help_window.title("Help - Keyboard Shortcuts and Functions")
    help_window.overrideredirect(True)
    help_window.transient(gui.root)

    # Outer border frame
    outer_frame = tk.Frame(help_window, bg=ColorConfig.current.BORDER_COLOR, padx=2, pady=2)
    outer_frame.pack(fill=tk.BOTH, expand=True)

    # Title bar
    title_bar = tk.Frame(outer_frame, bg=ColorConfig.current.FRAME_BG)
    title_bar.pack(side=tk.TOP, fill=tk.X)

    title_label = tk.Label(title_bar, text="Help - Keyboard Shortcuts and Functions",
                        bg=ColorConfig.current.FRAME_BG,
                        fg=ColorConfig.current.BUTTON_TEXT,
                        font=gui.custom_font)
    title_label.pack(side=tk.LEFT, padx=10)

    close_button = tk.Button(title_bar, text='X',
                            command=lambda: [help_window.destroy(), gui.root.focus_force(), gui.root.lift()],
                            bg=ColorConfig.current.FRAME_BG,
                            fg=ColorConfig.current.BUTTON_TEXT,
                            font=gui.custom_font)
    close_button.pack(side=tk.RIGHT)

    # Make draggable
    def start_drag(event):
        help_window._x = event.x
        help_window._y = event.y

    def do_drag(event):
        x = help_window.winfo_x() + event.x - help_window._x
        y = help_window.winfo_y() + event.y - help_window._y
        help_window.geometry(f"+{x}+{y}")

    title_bar.bind("<ButtonPress-1>", start_drag)
    title_bar.bind("<B1-Motion>", do_drag)
    title_label.bind("<ButtonPress-1>", start_drag)
    title_label.bind("<B1-Motion>", do_drag)
    help_window.bind('<Escape>', lambda e: help_window.destroy())

    # Content area with scroll
    content_frame = tk.Frame(outer_frame, bg=ColorConfig.current.FRAME_BG)
    content_frame.pack(fill=tk.BOTH, expand=True)

    text_frame = tk.Frame(content_frame, bg=ColorConfig.current.FRAME_BG)
    text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    theme = "Dark" if ColorConfig.current == ColorConfig.Dark else "Light"
    scrollbar = ttk.Scrollbar(text_frame, orient="vertical", style=f"{theme}Scrollbar.Vertical.TScrollbar")
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    text_area = tk.Text(text_frame, wrap="word", yscrollcommand=scrollbar.set,
                        font="Helvetica 10",
                        bg=ColorConfig.current.FRAME_BG,
                        fg=ColorConfig.current.BUTTON_TEXT,
                        insertbackground=ColorConfig.current.BUTTON_TEXT,
                        relief=tk.FLAT)
    scrollbar.config(command=text_area.yview)
    text_area.pack(fill=tk.BOTH, expand=True)

    help_lines = [
        ("Help\n", "title"),
        ("\nOverview:\n", "header"),
        ("NodeSailor is a simple network visualization tool.  It allows the user to create a network map, display and test their connections with options for pinging, quick launchers for file explorer, web browser, RDP and more with the implementation of custom commands.\n", "text"),
        ("\nUser Modes:\n", "header"),
        ("- Operator: Monitor and interact with the network.\n- Configuration: Build and edit the network layout.\n", "text"),
        ("\nOperator Mode:\n", "header"),
        ("- Left Click on Node: Ping the node (Green = all assigned IP addresses connected, Yellow = partial connection, Red = no connection).\n- Right Click on Node: Open context menu.\n- Right Click and Drag: Pan the canvas.\n- Scroll Wheel: Zoom in and out.\n- Who am I?: Highlight node matching active system IP address.\n- Ping All: Ping every node.\n- Clear Status: Reset node status.\n", "text"),
        ("\nConfiguration Mode:\n", "header"),
        ("- Double Left Click: Create a new node.\n- Shift + Double Left Click: Add a sticky note.\n- Middle Click: Create a connection line between two nodes.\n- Shift + Middle Click: Remove connection line.\n- Left Click + Drag: Move nodes or notes.\n- Right Click: Open context menu.\n", "text"),
        ("\nGroups:\n", "header"),
        ("Groups allow the configurator to visually organize nodes into labeled rectangles. Use the Groups button to create, edit, or remove groups. Groups can be renamed and repositioned for clarity.\n", "text"),
        ("\nNode List Editor:\n", "header"),
        ("The Node List Editor presents all nodes in a table for quick editing. Use it to add, remove, or modify node properties. Access via the Node List button.\n", "text"),
        ("\nConnections List Editor:\n", "header"),
        ("The Connections Editor displays all connections in a list format. Use it to add, remove, or edit connections between nodes. Access via the Connections List button.\n", "text"),
        ("\nVLAN Checkboxes:\n", "header"),
        ("- Toggle visibility of VLAN nodes.\n", "text"),
        ("\nCustom Commands:\n", "header"),
        ("- Access through 'Start Menu > Manage Custom Commands'.\n- Use placeholders like {ip}, {name}, {file}, {web}.\n- Example: ping {ip} -t\n", "text"),
        ("\nKeyboard Shortcuts:\n", "header"),
        ("- Ctrl-Shift-C Change color theme.\n", "text"),
    ]

    for line, tag in help_lines:
        text_area.insert(tk.END, line, tag)

    text_area.tag_config("title", font="Helvetica 12 bold")
    text_area.tag_config("header", font="Helvetica 10 bold", spacing3=4)
    text_area.tag_config("text", font="Helvetica 10", spacing1=1)

    text_area.config(state="disabled")
    help_window.lift()
    help_window.focus_set()
    gui.center_window_on_screen(help_window)
