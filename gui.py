import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as font
from tkinter import colorchooser, filedialog, messagebox
import json
from group_editor import DEFAULT_PRESETS, DEFAULT_HEIGHT, CONFIG_PATH
import os
import sys
import customtkinter as ctk  # Added for CTk window
from utils import get_ip_addresses
from colors import ColorConfig
from tooltip import ToolTip
from helpers import show_operator_guidance, show_configuration_guidance, read_NodeSailor_settings, write_NodeSailor_settings, NodeSailor_settings_PATH
from nodes import NetworkNode
from connections import ConnectionLine
from notes import StickyNote
from PIL import Image, ImageTk
from node_list import open_node_list_editor
from connection_list_editor import open_connection_list_editor
from groups import GroupManager, RectangleGroup
from group_editor import open_group_editor
from custom_commands import manage_custom_commands

# Default height for Edit Node window (for 4 VLANs) 
DEFAULT_NODE_HEIGHT = 360
# Height per VLAN row (used for dynamic resizing)
NODE_HEIGHT_PER_VLAN = 35

def get_resource_path(filename):
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, filename)
    return filename

class NetworkMapGUI:
    def manage_custom_commands(self):
        return manage_custom_commands(self)
    def _setup_scrollbar_styles(self):
        style = ttk.Style()
        theme = "Dark" if ColorConfig.current == ColorConfig.Dark else "Light"
        style.configure(f"{theme}Scrollbar.Vertical.TScrollbar",
                        troughcolor=ColorConfig.current.FRAME_BG,
                        background=ColorConfig.current.BUTTON_BG,
                        bordercolor=ColorConfig.current.BORDER_COLOR,
                        arrowcolor=ColorConfig.current.BUTTON_TEXT)
        style.configure(f"{theme}Scrollbar.Horizontal.TScrollbar",
                        troughcolor=ColorConfig.current.FRAME_BG,
                        background=ColorConfig.current.BUTTON_BG,
                        bordercolor=ColorConfig.current.BORDER_COLOR,
                        arrowcolor=ColorConfig.current.BUTTON_TEXT)

    def __init__(self, root):
        # Ensure gui.nodes always references the main node list
        self.gui = self
        # root should be created with ctk.CTk() for CustomTkinter support
        self.root = root
        self.sticky_note_popup = None
        self.load_window_geometry()  # Load saved window size and position
        # PyInstaller-compatible icon path
        icon_path = get_resource_path('data/favicon.ico')
        root.iconbitmap(icon_path)
        self.root.configure(bg=ColorConfig.current.FRAME_BG)
        self.custom_font = font.Font(family="Helvetica", size=12)
        self.show_tooltips = False
        self.color_editor_window = None
        self.vlan_label_names = {
            'VLAN_1': 'VLAN_1',
            'VLAN_2': 'VLAN_2',
            'VLAN_3': 'VLAN_3',
            'VLAN_4': 'VLAN_4'
        }
        self.vlan_label_order = list(self.vlan_label_names.keys())
        # Setup custom scrollbar styles for current theme
        self._setup_scrollbar_styles()
        self.info_value_style = {'font': ('Helvetica', 10),
                                 'bg': ColorConfig.current.INFO_NOTE_BG,
                                 'anchor': 'w'}
        
        # Bind <Map> event to restore secondary windows
        self.root.bind("<Map>", self.on_restore)

        # Load custom commands
        self.custom_commands = self.load_custom_commands()

        self.mode = "Configuration"
        self.selected_object_type = None
        self.connection_start_node = None
        self.legend_window = None
        self.unsaved_changes = False
        self.groups_mode_active = False
        self.group_manager = GroupManager(self)

        # Buttons Frame
        self.buttons_frame = tk.Frame(root)
        self.buttons_frame.pack(side=tk.TOP, fill=tk.X)
        self.buttons_frame.config(bg=ColorConfig.current.FRAME_BG)
        
        # Tooltip toggle button ('?')
        self.tooltip_button = tk.Button(
            self.buttons_frame,
            text='?',
            command=self.toggle_tooltips,
            font=self.custom_font,
            bg=ColorConfig.current.BUTTON_BG,
            fg=ColorConfig.current.BUTTON_TEXT,
            activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
            activeforeground=ColorConfig.current.BUTTON_ACTIVE_TEXT,
            relief=tk.SUNKEN if self.show_tooltips else tk.RAISED,
            padx=5,
            pady=2
        )
        self.tooltip_button.pack(side=tk.RIGHT, padx=4, pady=2)

        # Add tooltip for the tooltip button itself
        ToolTip(self.tooltip_button, "Enable or disable tooltips", self, bg=lambda: ColorConfig.current.INFO_NOTE_BG)

        # Groups mode banner label (persistent, hidden by default)
        self.groups_banner_label = tk.Label(
            self.root,
            text="Groups Mode Active",
            font=("Helvetica", 12, "bold"),
            fg="#ff9900",
            bg=ColorConfig.current.FRAME_BG
        )
        self.groups_banner_label.pack(side=tk.TOP, fill=tk.X)
        self.groups_banner_label.pack_forget()

        # Node deletion banner label (hidden by default)
        self.node_banner_label = tk.Label(
            self.root,
            text="",
            font=("Helvetica", 12, "bold"),
            fg="#ff9900",
            bg=ColorConfig.current.FRAME_BG
        )
        # Do not pack; will use place() when needed for bottom banner
     
        # Update button styles
        button_style = {
            'font': self.custom_font,
            'bg': ColorConfig.current.BUTTON_BG,
            'fg': ColorConfig.current.BUTTON_TEXT,
            'activebackground': ColorConfig.current.BUTTON_ACTIVE_BG,
            'activeforeground': ColorConfig.current.BUTTON_ACTIVE_TEXT,
            'padx': 5,
            'pady': 2
        }

        #scrollbar style
        style = ttk.Style()
        style.theme_use('clam')  # 'clam' allows customization

        style.configure("LightScrollbar.Vertical.TScrollbar",
            gripcount=0,
            background=ColorConfig.Light.BUTTON_BG,
            troughcolor=ColorConfig.Light.FRAME_BG,
            bordercolor=ColorConfig.Light.FRAME_BG,
            lightcolor=ColorConfig.Light.FRAME_BG,
            darkcolor=ColorConfig.Light.FRAME_BG,
            arrowsize=12
        )

        style.configure("DarkScrollbar.Vertical.TScrollbar",
            gripcount=0,
            background=ColorConfig.Dark.INFO_NOTE_BG,
            troughcolor=ColorConfig.Dark.FRAME_BG,
            bordercolor=ColorConfig.Dark.FRAME_BG,
            lightcolor=ColorConfig.Dark.FRAME_BG,
            darkcolor=ColorConfig.Dark.FRAME_BG,
            arrowsize=12
        )

        # Dark scrollbar theme fix (hover color issue)
        style.element_create("Dark.Vertical.Scrollbar.trough", "from", "clam")
        style.layout("DarkScrollbar.Vertical.TScrollbar", [
            ("Vertical.Scrollbar.trough", {
                "children": [("Vertical.Scrollbar.thumb", {"unit": "1", "sticky": "nswe"})],
                "sticky": "ns"
            })
        ])

        style.map("DarkScrollbar.Vertical.TScrollbar",
            background=[("active", ColorConfig.Dark.BUTTON_ACTIVE_BG),
                        ("!active", ColorConfig.Dark.INFO_NOTE_BG)]
        )


        start_menu_style = button_style.copy()
        start_menu_style['font'] = ("Helvetica", 12, "bold")

        start_menu_button = tk.Button(self.buttons_frame, text="Start Menu", command=self.display_legend, **start_menu_style)
        start_menu_button.pack(side=tk.LEFT, padx=5, pady=5)

        ToolTip(start_menu_button, "Open the Start Menu", self,
        bg=lambda: ColorConfig.current.INFO_NOTE_BG,
        fg=lambda: ColorConfig.current.INFO_TEXT)

        self.mode_button = tk.Button(self.buttons_frame, text='Configuration', command=self.toggle_mode, **button_style)
        self.mode_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        ToolTip(self.mode_button, "Toggle Operator/Configuration mode", self,
        bg=lambda: ColorConfig.current.INFO_NOTE_BG,
        fg=lambda: ColorConfig.current.INFO_TEXT)
        
        # Create Node List editor and connections list buttons
        self.list_view_editor_button = tk.Button(self.buttons_frame, text='Node List',
                                               command=lambda: self.defer_popup(lambda: open_node_list_editor(self)), **button_style)
        self.list_view_editor_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        ToolTip(self.list_view_editor_button, "Open a window that presents the nodes in a table format for quick editing", self,
        bg=lambda: ColorConfig.current.INFO_NOTE_BG,
        fg=lambda: ColorConfig.current.INFO_TEXT)
        
        self.edit_connections_button = tk.Button(self.buttons_frame, text='Connections List',
                                                command=lambda: self.defer_popup(self.open_connection_list_editor), **button_style)
        self.edit_connections_button.pack(side=tk.LEFT, padx=5, pady=5)

        ToolTip(self.edit_connections_button, "Edit connections between nodes in a list format", self,
        bg=lambda: ColorConfig.current.INFO_NOTE_BG,
        fg=lambda: ColorConfig.current.INFO_TEXT)
        
        # Add Groups button
        self.groups_button = tk.Button(self.buttons_frame, text='Groups',
                                      command=self.toggle_groups_mode, **button_style)
        # self.groups_button.pack(side=tk.LEFT, padx=5, pady=5)  # Now packed conditionally in toggle_mode()
        
        ToolTip(self.groups_button, "Create and edit rectangle groups to visually organize nodes", self,
        bg=lambda: ColorConfig.current.INFO_NOTE_BG,
        fg=lambda: ColorConfig.current.INFO_TEXT)
        
        self.edit_VLAN_button = tk.Button(self.buttons_frame, text='Edit VLAN Labels',
                                               command=lambda: self.defer_popup(self.edit_vlan_labels), **button_style)
        self.edit_VLAN_button.pack(side=tk.LEFT, padx=5, pady=5)

        ToolTip(self.edit_VLAN_button, "Edit the VLAN labels", self,
        bg=lambda: ColorConfig.current.INFO_NOTE_BG,
        fg=lambda: ColorConfig.current.INFO_TEXT)
        
        # Hide these buttons initially if starting in Operator mode
        if self.mode == "Operator":
            self.list_view_editor_button.pack_forget()
            self.edit_connections_button.pack_forget()
            self.groups_button.pack_forget()

        whoamI_button = tk.Button(self.buttons_frame, text='Who am I?', command=self.highlight_matching_nodes, **button_style)
        whoamI_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        ToolTip(whoamI_button, "Highlight node matching active system IP address", self,
        bg=lambda: ColorConfig.current.INFO_NOTE_BG,
        fg=lambda: ColorConfig.current.INFO_TEXT)

        clear_status_button = tk.Button(self.buttons_frame, text='Clear Status', command=self.clear_node_status, **button_style)
        clear_status_button.pack(side=tk.LEFT, padx=5, pady=5)

        ToolTip(clear_status_button, "Clear the status of all nodes", self,
        bg=lambda: ColorConfig.current.INFO_NOTE_BG,
        fg=lambda: ColorConfig.current.INFO_TEXT)

        ping_all_button = tk.Button(self.buttons_frame, text='Ping All', command=self.ping_all, **button_style)
        ping_all_button.pack(side=tk.LEFT, padx=5, pady=5)

        ToolTip(ping_all_button, "Ping all nodes", self,
        bg=lambda: ColorConfig.current.INFO_NOTE_BG,
        fg=lambda: ColorConfig.current.INFO_TEXT)


        # Zoom controls in bottom-left corner
        zoom_frame = tk.Frame(self.root, bg=ColorConfig.current.FRAME_BG, height=30)
        zoom_frame.place(relx=0.0, rely=1.0, anchor='sw', x=10, y=-5)
        self.zoom_frame = zoom_frame

        def make_zoom_button(text, command):
            return tk.Label(zoom_frame, text=text, font=("Helvetica", 12),
                            fg=ColorConfig.current.BUTTON_TEXT, bg=ColorConfig.current.FRAME_BG,
                            cursor="hand2", padx=5)
        
        zoom_in_btn = make_zoom_button("+", self.zoom_in)
        zoom_in_btn.pack(side=tk.LEFT)
        zoom_in_btn.bind("<Button-1>", lambda e: self.zoom_in())

        self.zoom_level_label = make_zoom_button("100%", self.reset_zoom)
        self.zoom_level_label.pack(side=tk.LEFT, padx=(5, 0))
        self.zoom_level_label.bind("<Button-1>", lambda e: self.reset_zoom())
        self.zoom_level_label.config(width=5)
        zoom_out_btn = make_zoom_button("–", self.zoom_out)
        zoom_out_btn.pack(side=tk.LEFT, padx=(5, 0))
        zoom_out_btn.bind("<Button-1>", lambda e: self.zoom_out())

        self.zoom_in_btn = zoom_in_btn
        self.zoom_out_btn = zoom_out_btn

        # Canvas below the buttons
        self.canvas = tk.Canvas(root, width=1500, height=800, bg=ColorConfig.current.FRAME_BG, highlightthickness=0)
        self.canvas.gui = self
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.zoom_frame.lift()  # Ensure zoom controls are above the canvas
        self.nodes = []
        self.stickynotes = []
        self.selected_node = None
        self.previous_selected_node = None
        
        self._pan_start_x = None
        self._pan_start_y = None

        self.canvas.bind('<Double-1>', self.create_node)
        self.canvas.bind('<B1-Motion>', self.handle_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.handle_mouse_release)
        self.canvas.bind('<Button-1>', self.handle_mouse_click)
        self.canvas.bind('<Shift-Double-1>', self.create_sticky_note)
        self.canvas.bind('<MouseWheel>', self.zoom_with_mouse)
        self.canvas.pack(fill=tk.BOTH, expand=True)  # Remove duplicate packing
        self.canvas.bind('<Button-2>', self.create_connection)
        self.canvas.bind('<Shift-Button-2>', self.remove_connection)
        self.canvas.bind('<ButtonPress-3>', self.start_pan)
        self.canvas.bind('<B3-Motion>', self.do_pan)

        #keyboard shortcuts
        self.bind_all_shortcuts()

        self.zoom_level = 1.0
        self.root.focus_set()

         # Info Panel
        self.info_panel = tk.Frame(self.root, bg=ColorConfig.current.INFO_NOTE_BG)
        self.info_panel.place(relx=1.0, rely=0.05, anchor='ne')

        info_label_style = {'font': ('Helvetica', 10), 
                            'bg': ColorConfig.current.INFO_NOTE_BG, 
                            'fg': ColorConfig.current.INFO_TEXT,
                            'anchor': 'w'}
        info_value_style = {'font': ('Helvetica', 10), 
                            'bg': ColorConfig.current.INFO_NOTE_BG, 
                            'fg': ColorConfig.current.INFO_TEXT}

        tk.Label(self.info_panel, text="Name:", **info_label_style).grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.node_name_label = tk.Label(self.info_panel, text="-", **info_value_style)
        self.node_name_label.grid(row=0, column=1, sticky='w', padx=5, pady=2)

        tk.Label(self.info_panel, text="", **info_label_style).grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.node_ip_label = tk.Label(self.info_panel, text="", **info_value_style)
        self.node_ip_label.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        self.refresh_info_panel_vlans(None, info_label_style, info_value_style)
        
        self.toggle_mode() # sets to Operator mode on startup
        self.hide_legend_on_start = tk.BooleanVar(value=False)
        self.load_NodeSailor_settings()
        if self.hide_legend_on_start.get():
            pass


        root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.update_ui_colors()

    def refresh_info_panel_vlans(self, node, info_label_style, info_value_style):
        # Remove existing VLAN label widgets from info_panel
        for label in getattr(self, 'vlan_title_labels', {}).values():
            label.destroy()
        for label in getattr(self, 'vlan_labels', {}).values():
            label.destroy()
        self.vlan_labels = {}
        self.vlan_title_labels = {}
        # Dynamically create VLAN label widgets for all VLANs in node.vlans
        if hasattr(node, "vlans") and isinstance(node.vlans, dict):
            # Sort VLANs by label for display
            # Use self.vlan_label_order if set, else sort by label
            if hasattr(self, "vlan_label_order") and self.vlan_label_order:
                ordered_keys = [v for v in self.vlan_label_order if v in node.vlans]
                # Add any remaining VLANs not in vlan_label_order at the end
                ordered_keys += [v for v in node.vlans if v not in ordered_keys]
                sorted_vlans = [(v, node.vlans[v]) for v in ordered_keys]
            else:
                sorted_vlans = sorted(node.vlans.items(), key=lambda x: self.vlan_label_names.get(x[0], x[0]))
            for i, (vlan, vlan_value) in enumerate(sorted_vlans, start=2):
                vlan_label = self.vlan_label_names.get(vlan, vlan)
                title = tk.Label(self.info_panel, text=f"{vlan_label}:", **info_label_style)
                title.grid(row=i, column=0, sticky='w', padx=5, pady=2)
                self.vlan_title_labels[vlan] = title

                self.vlan_labels[vlan] = tk.Label(self.info_panel, text=vlan_value, **info_value_style)
                self.vlan_labels[vlan].grid(row=i, column=1, sticky='w', padx=5, pady=2)

    def on_restore(self, event):
        # Lift all secondary windows that are Toplevels
        for child in self.root.winfo_children():
            if isinstance(child, (tk.Toplevel, ctk.CTkToplevel)):
                child.lift()

    def toggle_tooltips(self):
        self.show_tooltips = not self.show_tooltips
        # Update button appearance
        self.tooltip_button.config(relief=tk.SUNKEN if self.show_tooltips else tk.RAISED)

    def bind_all_shortcuts(self):
        """Bind all global keyboard shortcuts."""
        self.root.bind('<Left>', lambda event: self.pan_canvas('left'))  # Pan left
        self.root.bind('<Right>', lambda event: self.pan_canvas('right'))  # Pan right
        self.root.bind('<Up>', lambda event: self.pan_canvas('up'))  # Pan up
        self.root.bind('<Down>', lambda event: self.pan_canvas('down'))  # Pan down
        self.root.bind_all('<F1>', self.show_help)
        self.root.bind('<Control-Shift-C>', lambda event: [self.root.focus_set(), self.toggle_theme()])
        self.root.bind('<Control-s>', self.keyboard_save)
        self.root.bind('<Control-l>', self.keyboard_load)

    def regain_focus(self):
        """Force the main window to regain focus after a subwindow is closed."""
        try:
            self.root.focus_force()
            self.root.bind_all_shortcuts()
        except Exception:
            pass

    def start_move_legend(self, event):
        self.legend_window._x = event.x
        self.legend_window._y = event.y

    def do_move_legend(self, event):
        deltax = event.x - self.legend_window._x
        deltay = event.y - self.legend_window._y
        x = self.legend_window.winfo_x() + deltax
        y = self.legend_window.winfo_y() + deltay
        self.legend_window.geometry(f"+{x}+{y}")

    def add_custom_titlebar(self, window, title, on_close=None, toplevel=None):
        outer = tk.Frame(window, bg=ColorConfig.current.BORDER_COLOR, padx=2, pady=2)
        outer.pack(fill=tk.BOTH, expand=True)

        titlebar = tk.Frame(outer, bg=ColorConfig.current.FRAME_BG)
        titlebar.pack(side=tk.TOP, fill=tk.X)

        label = tk.Label(titlebar, text=title, bg=ColorConfig.current.FRAME_BG,
                        fg=ColorConfig.current.BUTTON_TEXT, font=self.custom_font)
        label.pack(side=tk.LEFT, padx=10)

        btn = tk.Button(titlebar, text='X', command=on_close or (toplevel or window).destroy,
                        bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT,
                        font=self.custom_font)
        btn.pack(side=tk.RIGHT)

        # Use the correct window to move (toplevel if provided)
        move_target = toplevel if toplevel is not None else window

        def start(event):
            move_target._x = event.x_root
            move_target._y = event.y_root

        def drag(event):
            dx = event.x_root - move_target._x
            dy = event.y_root - move_target._y
            x = move_target.winfo_x() + dx
            y = move_target.winfo_y() + dy
            move_target.geometry(f"+{x}+{y}")
            move_target._x = event.x_root
            move_target._y = event.y_root

        titlebar.bind("<ButtonPress-1>", start)
        titlebar.bind("<B1-Motion>", drag)
        label.bind("<ButtonPress-1>", start)
        label.bind("<B1-Motion>", drag)

        return outer

    def show_color_editor(self):
        if self.legend_window and self.legend_window.winfo_exists():
            self.legend_window.destroy()
            self.legend_window = None

        if hasattr(self, 'color_editor_window'):
            try:
                if self.color_editor_window.winfo_exists():
                    self.color_editor_window.lift()
                    return
            except:
                self.color_editor_window = None

        def on_close():
            try: self.color_editor_window.grab_release()
            except: pass
            self.color_editor_window.destroy()
            self.color_editor_window = None
            self.regain_focus()

        self.color_editor_window, content = self.create_popup("Color Scheme Editor", 300, 900, on_close=on_close, grab=False)
        self.color_editor_window.attributes('-topmost', True)

        theme_var = tk.StringVar(value="Dark" if ColorConfig.current == ColorConfig.Dark else "Light")

        tk.Label(content, text="Select Theme:",
                bg=ColorConfig.current.FRAME_BG,
                fg=ColorConfig.current.BUTTON_TEXT,
                font=('Helvetica', 10)).pack(pady=5)

        tk.Button(content, text="Load Colors", command=self.load_colors,
                bg=ColorConfig.current.BUTTON_BG,
                fg=ColorConfig.current.BUTTON_TEXT,
                activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
                activeforeground=ColorConfig.current.BUTTON_ACTIVE_TEXT).pack(pady=5)

        tk.Button(content, text="Save Colors", command=self.save_colors,
                bg=ColorConfig.current.BUTTON_BG,
                fg=ColorConfig.current.BUTTON_TEXT,
                activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
                activeforeground=ColorConfig.current.BUTTON_ACTIVE_TEXT).pack(pady=5)

        for mode in ["Light", "Dark"]:
            tk.Radiobutton(content, text=mode, variable=theme_var, value=mode,
                        bg=ColorConfig.current.FRAME_BG,
                        fg=ColorConfig.current.BUTTON_TEXT,
                        selectcolor=ColorConfig.current.FRAME_BG,
                        activebackground=ColorConfig.current.BUTTON_BG,
                        activeforeground=ColorConfig.current.BUTTON_TEXT).pack()

        color_frame = tk.Frame(content, bg=ColorConfig.current.FRAME_BG)
        color_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        color_entries = {}
        color_attrs = [attr for attr in dir(ColorConfig.Light)
                    if not attr.startswith('__') and attr != 'current']

        def update_color(attr):
            theme = theme_var.get()
            current_color = getattr(getattr(ColorConfig, theme), attr, "#ffffff")
            new_color = colorchooser.askcolor(title=f"Choose {attr} for {theme}", initialcolor=current_color)
            if new_color[1]:
                setattr(getattr(ColorConfig, theme), attr, new_color[1])
                color_entries[attr]['button'].config(bg=new_color[1])
                self.update_ui_colors()

        for i, attr in enumerate(color_attrs):
            tk.Label(color_frame, text=f"{attr}:", bg=ColorConfig.current.FRAME_BG,
                    fg=ColorConfig.current.BUTTON_TEXT).grid(row=i, column=0, sticky="w", pady=2)
            current_color = getattr(getattr(ColorConfig, theme_var.get()), attr, "#ffffff")
            btn = tk.Button(color_frame, text="Pick Color", bg=current_color,
                            command=lambda a=attr: update_color(a))
            btn.grid(row=i, column=1, sticky="ew", pady=2)
            color_entries[attr] = {'button': btn}

        def on_theme_change(*args):
            theme = theme_var.get()
            for attr in color_attrs:
                current_color = getattr(getattr(ColorConfig, theme), attr)
                color_entries[attr]['button'].config(bg=current_color)

        theme_var.trace("w", on_theme_change)

        tk.Button(content, text="Close", command=on_close,
                bg=ColorConfig.current.BUTTON_BG,
                fg=ColorConfig.current.BUTTON_TEXT,
                activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
                activeforeground=ColorConfig.current.BUTTON_ACTIVE_TEXT).pack(pady=10)

        self.fix_window_geometry(self.color_editor_window, 500, 900)

    def edit_vlan_labels(self):
        # Destroy any existing VLAN editor window before opening a new one
        if getattr(self, 'vlan_label_editor', None) and self.vlan_label_editor.winfo_exists():
            self.vlan_label_editor.destroy()
            self.vlan_label_editor = None

        # Withdraw the legend window if it exists
        if getattr(self, 'legend_window', None) and self.legend_window.winfo_exists():
            self.legend_window.withdraw()

        def close_vlan_editor():
            try:
                self.vlan_label_editor.grab_release()
            except:
                pass
            self.vlan_label_editor.destroy()
            self.vlan_label_editor = None
            self.regain_focus()  # Restore focus to the main window

        self.vlan_label_editor, content = self.create_popup("Edit VLAN Labels", 400, 350, on_close=close_vlan_editor, grab=False)

        entries = {}

        vlan_frame = tk.Frame(content, bg=ColorConfig.current.FRAME_BG)
        vlan_frame.grid(row=0, column=0, columnspan=3, sticky="nsew")

        # Helper to update window height dynamically (for refresh/reorder)
        def update_vlan_window_height():
            min_height = 100
            max_height = 1000
            base_height = 120  # space for controls/buttons
            per_vlan = 36      # per VLAN row
            n = len(self.vlan_label_order)
            height = min(max(min_height, base_height + per_vlan * n), max_height)
            self.vlan_label_editor.geometry(f"400x{height}")

        def refresh_vlan_entries():
            # Clear current widgets in vlan_frame
            for widget in vlan_frame.winfo_children():
                widget.destroy()
            entries.clear()
            # Use custom VLAN order for display
            for i, vlan in enumerate(self.vlan_label_order):
                tk.Label(vlan_frame, text=vlan + ":", anchor="e",
                        bg=ColorConfig.current.FRAME_BG,
                        fg=ColorConfig.current.BUTTON_TEXT,
                        font=('Helvetica', 10))\
                    .grid(row=i, column=0, padx=10, pady=5, sticky="e")
                entry = tk.Entry(vlan_frame, bg=ColorConfig.current.ENTRY_FOCUS_BG, fg=ColorConfig.current.ENTRY_TEXT, insertbackground=ColorConfig.current.ENTRY_TEXT)
                entry.insert(0, self.vlan_label_names[vlan])
                entry.grid(row=i, column=1, padx=10, pady=5)
                entries[vlan] = entry

                def make_remove(vlan_name):
                    return lambda: remove_vlan(vlan_name)
                remove_btn = tk.Button(vlan_frame, text="Remove", command=make_remove(vlan),
                                      bg=ColorConfig.current.BUTTON_BG,
                                      fg=ColorConfig.current.BUTTON_TEXT,
                                      activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
                                      activeforeground=ColorConfig.current.BUTTON_ACTIVE_TEXT,
                                      font=('Helvetica', 9))
                remove_btn.grid(row=i, column=4, padx=5, pady=5)

                # Up/Down buttons for reordering
                def make_move_up(idx):
                    return lambda: move_vlan(idx, -1)
                def make_move_down(idx):
                    return lambda: move_vlan(idx, 1)
                up_btn = tk.Button(vlan_frame, text="↑", command=make_move_up(i),
                                   bg=ColorConfig.current.BUTTON_BG,
                                   fg=ColorConfig.current.BUTTON_TEXT,
                                   activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
                                   activeforeground=ColorConfig.current.BUTTON_ACTIVE_TEXT,
                                   font=('Helvetica', 9), width=2)
                up_btn.grid(row=i, column=2, padx=2, pady=5)
                down_btn = tk.Button(vlan_frame, text="↓", command=make_move_down(i),
                                     bg=ColorConfig.current.BUTTON_BG,
                                     fg=ColorConfig.current.BUTTON_TEXT,
                                     activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
                                     activeforeground=ColorConfig.current.BUTTON_ACTIVE_TEXT,
                                     font=('Helvetica', 9), width=2)
                down_btn.grid(row=i, column=3, padx=2, pady=5)
            update_vlan_window_height()

        # Populate VLAN entries before showing window and setting geometry
        refresh_vlan_entries()
        update_vlan_window_height()
        self.vlan_label_editor.deiconify()
        self.vlan_label_editor.update_idletasks()

        def move_vlan(idx, direction):
            new_idx = idx + direction
            if 0 <= new_idx < len(self.vlan_label_order):
                self.vlan_label_order[idx], self.vlan_label_order[new_idx] = (
                    self.vlan_label_order[new_idx], self.vlan_label_order[idx]
                )
                refresh_vlan_entries()
        # Ensure the window is wide enough for all buttons
        self.vlan_label_editor.minsize(400, 350)
        # Remove static geometry setting; handled dynamically

        def add_vlan():
            # Find next available VLAN name
            base = "VLAN_"
            idx = 1
            while f"{base}{idx}" in self.vlan_label_names:
                idx += 1
            new_vlan = f"{base}{idx}"
            self.vlan_label_names[new_vlan] = ""
            self.vlan_label_order.append(new_vlan)
            refresh_vlan_entries()

        def remove_vlan(vlan):
            if vlan in self.vlan_label_names:
                del self.vlan_label_names[vlan]
                if vlan in self.vlan_label_order:
                    self.vlan_label_order.remove(vlan)
            refresh_vlan_entries()

        refresh_vlan_entries()

        add_btn = tk.Button(content, text="Add VLAN", command=add_vlan,
                            bg=ColorConfig.current.BUTTON_BG,
                            fg=ColorConfig.current.BUTTON_TEXT,
                            activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
                            activeforeground=ColorConfig.current.BUTTON_ACTIVE_TEXT,
                            font=('Helvetica', 10))
        add_btn.grid(row=1, column=0, columnspan=3, pady=5)

        def save_labels():
            # Remove VLANs that were deleted
            to_remove = [vlan for vlan in self.vlan_label_names if vlan not in entries]
            for vlan in to_remove:
                del self.vlan_label_names[vlan]
                if vlan in self.vlan_label_order:
                    self.vlan_label_order.remove(vlan)
            # Update/add VLANs
            for vlan, entry in entries.items():
                self.vlan_label_names[vlan] = entry.get()
            for vlan, label in self.vlan_title_labels.items():
                if vlan in self.vlan_label_names:
                    label.config(text=self.vlan_label_names[vlan] + ":")
            # VLAN checkboxes removed; dynamic VLAN UI is updated via refresh_vlan_entries()
            # Refresh info panel VLANs to reflect changes
            self.refresh_info_panel_vlans(
                {'font': ('Helvetica', 10), 'bg': ColorConfig.current.INFO_NOTE_BG, 'fg': ColorConfig.current.INFO_TEXT, 'anchor': 'w'},
                {'font': ('Helvetica', 10), 'bg': ColorConfig.current.INFO_NOTE_BG, 'fg': ColorConfig.current.INFO_TEXT},
                self.info_value_style
            )
            close_vlan_editor()
            self.save_network_state()

        button_frame = tk.Frame(content, bg=ColorConfig.current.FRAME_BG)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        tk.Button(button_frame, text="Save", command=save_labels,
                bg=ColorConfig.current.BUTTON_BG,
                fg=ColorConfig.current.BUTTON_TEXT,
                activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
                activeforeground=ColorConfig.current.BUTTON_ACTIVE_TEXT,
                font=('Helvetica', 10)).pack()

        final_height = self.vlan_label_editor.winfo_height()
        self.vlan_label_editor.after(1, lambda: self.vlan_label_editor.geometry(f"400x{final_height}"))

    def show_help(self, event=None):
        """
        Creates a help window with a scrollable text area that displays
        the application's help information.

        :param event: Unused
        """
        help_window = tk.Toplevel(self.root)
        help_window.title("Help - Keyboard Shortcuts and Functions")
        help_window.overrideredirect(True)
        help_window.transient(self.root)

        # Outer border frame
        outer_frame = tk.Frame(help_window, bg=ColorConfig.current.BORDER_COLOR, padx=2, pady=2)
        outer_frame.pack(fill=tk.BOTH, expand=True)

        # Title bar
        title_bar = tk.Frame(outer_frame, bg=ColorConfig.current.FRAME_BG)
        title_bar.pack(side=tk.TOP, fill=tk.X)

        title_label = tk.Label(title_bar, text="Help - Keyboard Shortcuts and Functions",
                            bg=ColorConfig.current.FRAME_BG,
                            fg=ColorConfig.current.BUTTON_TEXT,
                            font=self.custom_font)
        title_label.pack(side=tk.LEFT, padx=10)

        close_button = tk.Button(title_bar, text='X',
                                command=lambda: [help_window.destroy(), self.root.focus_force(), self.root.lift()],
                                bg=ColorConfig.current.FRAME_BG,
                                fg=ColorConfig.current.BUTTON_TEXT,
                                font=self.custom_font)
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
            ("NodeSailor v0.9.29- Help\n", "title"),
            ("\nOverview:\n", "header"),
            ("NodeSailor is a simple network visualization tool.  It allows the user to create a network map, display and test their connections with options for pinging, quick launchers for file explorer, web browser, RDP and more with the implementation of custom commands.\n", "text"),

            ("\nUser Modes:\n", "header"),
            ("- Operator: Monitor and interact with the network.\n"
             "- Configuration: Build and edit the network layout.\n", "text"),

            ("\nOperator Mode:\n", "header"),
            ("- Left Click on Node: Ping the node (Green = all assigned IP addresses connected, Yellow = partial connection, Red = no connection).\n"
             "- Right Click on Node: Open context menu.\n"
             "- Right Click and Drag: Pan the canvas.\n"
             "- Scroll Wheel: Zoom in and out.\n"
             "- Who am I?: Highlight the node matching your machine's IP.\n"
             "- Ping All: Ping every node.\n"
             "- Clear Status: Reset node status.\n", "text"),

            ("\nConfiguration Mode:\n", "header"),
            ("- Double Left Click: Create a new node.\n"
             "- Shift + Double Left Click: Add a sticky note.\n"
             "- Middle Click: Create a connection line between two nodes.\n"
             "- Shift + Middle Click: Remove connection line.\n"
             "- Left Click + Drag: Move nodes or notes.\n"
             "- Right Click: Open context menu.\n", "text"),

            ("\nGroups:\n", "header"),
            ("Groups allow the configurator to visually organize nodes into labeled rectangles. Use the Groups button to create, edit, or remove groups. Groups can be renamed and repositioned for clarity.\n", "text"),

            ("\nNode List Editor:\n", "header"),
            ("The Node List Editor presents all nodes in a table for quick editing. Use it to add, remove, or modify node properties. Access via the Node List button.\n", "text"),

            ("\nConnections List Editor:\n", "header"),
            ("The Connections Editor displays all connections in a list format. Use it to add, remove, or edit connections between nodes. Access via the Connections List button.\n", "text"),

            ("\nVLAN Checkboxes:\n", "header"),
            ("- Toggle visibility of VLAN nodes.\n", "text"),

            ("\nCustom Commands:\n", "header"),
            ("- Access through 'Start Menu > Manage Custom Commands'.\n"
             "- Use placeholders like {ip}, {name}, {file}, {web}.\n"
             "- Example: ping {ip} -t\n", "text"),

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
        self.center_window_on_screen(help_window)

    def toggle_mode(self):
        if self.mode == "Operator":
            self.mode = "Configuration"
            self.mode_button.config(text='Configuration Mode', bg=ColorConfig.current.BUTTON_CONFIGURATION_MODE)
            # Enable functionalities for Configuration mode
            self.canvas.bind('<Double-1>', self.create_node)
            self.canvas.bind('<B1-Motion>', self.move_node)
            self.canvas.bind('<Shift-Double-1>', self.create_sticky_note)
            self.canvas.bind('<Button-2>', self.create_connection)
            
            # Show configuration mode buttons
            self.list_view_editor_button.pack(side=tk.LEFT, padx=5, pady=5, after=self.mode_button)
            self.edit_connections_button.pack(side=tk.LEFT, padx=5, pady=5, after=self.list_view_editor_button)
            self.edit_VLAN_button.pack(side=tk.LEFT, padx=5, pady=5, after=self.edit_connections_button)
            self.groups_button.pack(side=tk.LEFT, padx=5, pady=5, after=self.edit_connections_button)

            # Show configuration guidance window
            show_configuration_guidance(self.root, self.center_window_on_screen, self.custom_font)
            
        else:
            self.mode = "Operator"
            self.mode_button.config(text='Operator Mode', bg=ColorConfig.current.BUTTON_BG)
            # Disable functionalities for Operator mode
            self.canvas.unbind('<Double-1>')
            self.canvas.unbind('<B1-Motion>')
            self.canvas.unbind('<Shift-Double-1>')
            self.canvas.unbind('<Button-2>')
            
            # Hide configuration mode buttons
            self.list_view_editor_button.pack_forget()
            self.edit_connections_button.pack_forget()
            self.edit_VLAN_button.pack_forget()
            self.groups_button.pack_forget()
            self.make_popup_closer("group_editor_window")()
  
    def zoom_with_mouse(self, event):
        # Hide any open connection info popups before zooming
        for node in self.nodes:
            for conn in getattr(node, "connections", []):
                if hasattr(conn, "info_popup") and conn.info_popup:
                    try:
                        conn.info_popup.destroy()
                    except Exception:
                        pass
                    conn.info_popup = None

        if event.num == 4 or event.delta > 0:
            factor = 1.1
        elif event.num == 5 or event.delta < 0:
            factor = 0.9
        else:
            return

        # Get mouse position relative to canvas
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        # Scale all canvas items visually
        self.canvas.scale("all", x, y, factor, factor)

        # Update stored node coordinates
        for node in self.nodes:
            node.x = (node.x - x) * factor + x
            node.y = (node.y - y) * factor + y
            node.update_position(node.x, node.y)

        # Update stored group rectangle coordinates
        for group in self.group_manager.groups:
            group_x1 = (group.x1 - x) * factor + x
            group_y1 = (group.y1 - y) * factor + y
            group_x2 = (group.x2 - x) * factor + x
            group_y2 = (group.y2 - y) * factor + y
            group.update_position(group_x1, group_y1, group_x2, group_y2)

        self.zoom_level *= factor
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.update_zoom_label()
    def zoom_in(self, event=None):
        bbox = self.canvas.bbox("all")
        if bbox:
            center_x = (bbox[0] + bbox[2]) / 2
            center_y = (bbox[1] + bbox[3]) / 2
        else:
            center_x = center_y = 0
        self.apply_zoom(1.1, center_x, center_y)
        self.update_zoom_label()

    def zoom_out(self, event=None):
        bbox = self.canvas.bbox("all")
        if bbox:
            center_x = (bbox[0] + bbox[2]) / 2
            center_y = (bbox[1] + bbox[3]) / 2
        else:
            center_x = center_y = 0
        self.apply_zoom(0.9, center_x, center_y)
        self.update_zoom_label()

    def reset_zoom(self, event=None):
        if self.zoom_level != 1.0:
            bbox = self.canvas.bbox("all")
            if bbox:
                center_x = (bbox[0] + bbox[2]) / 2
                center_y = (bbox[1] + bbox[3]) / 2
            else:
                center_x = center_y = 0
            self.apply_zoom(1 / self.zoom_level, center_x, center_y)
            self.update_zoom_label()

    def apply_zoom(self, factor, center_x=None, center_y=None):
        # Hide any open connection info popups before zooming
        for node in self.nodes:
            for conn in getattr(node, "connections", []):
                if hasattr(conn, "info_popup") and conn.info_popup:
                    try:
                        conn.info_popup.destroy()
                    except Exception:
                        pass
                    conn.info_popup = None

        # Use canvas center if no center provided
        if center_x is None or center_y is None:
            bbox = self.canvas.bbox("all")
            if bbox:
                center_x = (bbox[0] + bbox[2]) / 2
                center_y = (bbox[1] + bbox[3]) / 2
            else:
                center_x = center_y = 0

        # Scale all canvas items visually
        self.canvas.scale("all", center_x, center_y, factor, factor)
        self.update_zoom_label()

        # Update stored node coordinates
        for node in self.nodes:
            node.x = (node.x - center_x) * factor + center_x
            node.y = (node.y - center_y) * factor + center_y
            node.update_position(node.x, node.y)

        # Update stored group rectangle coordinates
        for group in self.group_manager.groups:
            group_x1 = (group.x1 - center_x) * factor + center_x
            group_y1 = (group.y1 - center_y) * factor + center_y
            group_x2 = (group.x2 - center_x) * factor + center_x
            group_y2 = (group.y2 - center_y) * factor + center_y
            group.update_position(group_x1, group_y1, group_x2, group_y2)

        self.zoom_level *= factor
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def update_zoom_label(self):
        percent = int(self.zoom_level * 100)
        self.zoom_level_label.config(text=f"{percent}%")


    def pan_canvas(self, direction):
        pan_speed = 1  # Adjust the panning speed
        if direction == 'left':
            self.canvas.xview_scroll(-1 * pan_speed, 'units')
        elif direction == 'right':
            self.canvas.xview_scroll(pan_speed, 'units')
        elif direction == 'up':
            self.canvas.yview_scroll(-1 * pan_speed, 'units')
        elif direction == 'down':
            self.canvas.yview_scroll(pan_speed, 'units')

    def start_pan(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def do_pan(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def update_vlan_visibility(self):
        for node in self.nodes:
            # Determine if the node should be visible or greyed out
            should_be_visible = any(self.vlan_visibility[vlan].get() for vlan in self.vlan_label_names.keys() if getattr(node, vlan))
            node_color = ColorConfig.current.NODE_DEFAULT if should_be_visible else ColorConfig.current.NODE_GREYED_OUT
            self.canvas.itemconfigure(node.shape, fill=node_color)

    def update_vlan_colors(self, node, ping_results):
        vlan_keys = list(self.vlan_label_names.keys())
        for i, vlan in enumerate(vlan_keys):
            if vlan in self.vlan_labels:
                if i < len(ping_results):
                    color = ColorConfig.current.NODE_PING_SUCCESS if ping_results[i] else ColorConfig.current.NODE_PING_FAILURE
                else:
                    color = ColorConfig.current.NODE_PING_FAILURE  # Default to failure if no result
                self.vlan_labels[vlan].config(bg=color)


    def display_legend(self):
        # Check if the legend window exists and is valid
        if self.legend_window is not None and self.legend_window.winfo_exists():
            self.legend_window.deiconify()  # Restore if minimized
            self.legend_window.lift()       # Bring to front
            #self.legend_window.grab_set()   # Ensure it has the grab
        else:
            self.legend_window = tk.Toplevel(self.root)
            self.legend_window.overrideredirect(True)
            self.legend_window.transient(self.root)
            self.legend_window.transient(self.root)
            
            # Outer frame acts as the border
            outer_frame = tk.Frame(self.legend_window, bg=ColorConfig.current.BORDER_COLOR, padx=2, pady=2)
            outer_frame.pack(fill=tk.BOTH, expand=True)
            
            # Title bar
            title_bar = tk.Frame(outer_frame, bg=ColorConfig.current.FRAME_BG)
            title_bar.pack(side=tk.TOP, fill=tk.X)

            title_label = tk.Label(title_bar, text="NodeSailor v0.9.29", bg=ColorConfig.current.FRAME_BG,
                                fg=ColorConfig.current.BUTTON_TEXT, font=self.custom_font)
            title_label.pack(side=tk.LEFT, padx=10)

            close_button = tk.Button(title_bar, text='X', command=self.close_legend,
                                    bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT,
                                    font=self.custom_font)
            close_button.pack(side=tk.RIGHT)

            # Make the title bar draggable
            title_bar.bind("<ButtonPress-1>", self.start_move_legend)
            title_bar.bind("<B1-Motion>", self.do_move_legend)
            title_label.bind("<ButtonPress-1>", self.start_move_legend)
            title_label.bind("<B1-Motion>", self.do_move_legend)
            self.legend_window.bind("<Escape>", lambda e: self.close_legend())

            # Content frame
            content_frame = tk.Frame(outer_frame, bg=ColorConfig.current.FRAME_BG)
            content_frame.pack(fill=tk.BOTH, expand=True)

            # Image
            import sys, os
            legend_path = get_resource_path('data/favicon.ico')
            img = Image.open(legend_path).resize((300, 300), Image.Resampling.LANCZOS)
            photo_img = ImageTk.PhotoImage(img)
            img_label = tk.Label(content_frame, image=photo_img, bg=ColorConfig.current.FRAME_BG)
            img_label.image = photo_img  # Keep a reference to avoid garbage collection
            img_label.pack(pady=5)

            # Button styles
            button_style = {
                'font': self.custom_font,
                'bg': ColorConfig.current.BUTTON_BG,
                'fg': ColorConfig.current.BUTTON_TEXT,
                'activebackground': ColorConfig.current.BUTTON_ACTIVE_BG,
                'activeforeground': ColorConfig.current.BUTTON_ACTIVE_TEXT,
                'relief': tk.FLAT,
                'padx': 5,
                'pady': 2
            }

            # Buttons
            create_new = tk.Button(content_frame, text='Create New Network',
                                command=lambda: [self.new_network_state(), self.close_legend()], **button_style)
            create_new.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

            save_button = tk.Button(content_frame, text='Save',
                                    command=lambda: [self.save_network_state(), self.close_legend()], **button_style)
            save_button.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

            load_button = tk.Button(content_frame, text='Load',
                                    command=lambda: [self.load_network_state(), self.close_legend()], **button_style)
            load_button.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

            self.theme_button = tk.Button(content_frame,
                                        text="Dark Mode" if ColorConfig.current == ColorConfig.Light else "Light Mode",
                                        command=self.toggle_theme, **button_style)
            self.theme_button.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            
            config_menu_btn = tk.Button(content_frame, text='Configuration Menu',
                                command=lambda: self.defer_popup(self.open_configuration_menu), **button_style)
            config_menu_btn.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

            help_button = tk.Button(content_frame, text='Help', command=self.show_help, **button_style)
            help_button.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

            close_btn = tk.Button(content_frame, text='Close', command=self.close_legend, **button_style)
            close_btn.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

            # Checkbox
            self.hide_legend_checkbox = tk.Checkbutton(
                content_frame,
                text="Hide this window on next startup and load most recent on next startup",
                variable=self.hide_legend_on_start,
                command=self.save_NodeSailor_settings,
                bg=ColorConfig.current.FRAME_BG,
                fg=ColorConfig.current.BUTTON_TEXT,
                selectcolor=ColorConfig.current.FRAME_BG,
                activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
                activeforeground=ColorConfig.current.BUTTON_ACTIVE_TEXT
            )
            self.hide_legend_checkbox.pack(pady=5)

            self.legend_window.lift()
            self.legend_window.focus_set()
            self.center_window_on_screen(self.legend_window)

    #delay window creation until after legend window is closed
    def defer_popup(self, func):
        self.close_legend()
        self.root.after(100, func)

    # This callback closes the legend window
    def close_legend(self):
        if self.legend_window and self.legend_window.winfo_exists():
            self.legend_window.destroy()
            self.legend_window = None
        self.root.focus_force()  # Stronger focus restoration
        self.root.lift()  # Bring window to the foreground
        
    def open_configuration_menu(self):
        """Open a configuration menu window with options for editing colors, VLAN labels, connections, and custom commands."""
        if hasattr(self, 'config_menu_window') and self.config_menu_window and self.config_menu_window.winfo_exists():
            self.config_menu_window.lift()
            return
            
        def close_config_menu():
            try:
                self.config_menu_window.grab_release()
            except:
                pass
            self.config_menu_window.destroy()
            self.config_menu_window = None
            self.regain_focus()
            
        self.config_menu_window, content = self.create_popup("Configuration Menu", 300, 250, on_close=close_config_menu, grab=False)
        
        # Button styles
        button_style = {
            'font': self.custom_font,
            'bg': ColorConfig.current.BUTTON_BG,
            'fg': ColorConfig.current.BUTTON_TEXT,
            'activebackground': ColorConfig.current.BUTTON_ACTIVE_BG,
            'activeforeground': ColorConfig.current.BUTTON_ACTIVE_TEXT,
            'relief': tk.FLAT,
            'padx': 5,
            'pady': 2
        }
        
        # Configuration buttons
        color_editor_button = tk.Button(content, text='Edit Colors',
                                      command=lambda: [close_config_menu(),self.defer_popup(self.show_color_editor)], **button_style)
        color_editor_button.pack(side=tk.TOP, fill=tk.X, padx=20, pady=10)
      
        custom_cmd_btn = tk.Button(content, text='Manage Custom Commands',
                                 command=lambda: [close_config_menu(),self.defer_popup(self.manage_custom_commands)], **button_style)
        custom_cmd_btn.pack(side=tk.TOP, fill=tk.X, padx=20, pady=10)
        
        # Close button
        close_btn = tk.Button(content, text='Close', command=close_config_menu, **button_style)
        close_btn.pack(side=tk.TOP, fill=tk.X, padx=20, pady=20)
        
        self.fix_window_geometry(self.config_menu_window, 300, 350)

    def save_NodeSailor_settings(self):
        state = {}
        # Update only the relevant setting and preserve others
        write_NodeSailor_settings({'HIDE_LEGEND': self.hide_legend_on_start.get()})

    def load_NodeSailor_settings(self):
        try:
            with open(NodeSailor_settings_PATH, "r") as f:
                for line in f:
                    if line.startswith("HIDE_LEGEND="):
                        value = line.strip().split("=", 1)[1].strip().lower()
                        self.hide_legend_on_start.set(value == '1' or value == 'true')
        except Exception:
            # Fallback: default to not hiding legend if file is missing/unreadable
            self.hide_legend_on_start.set(False)
        
    def center_window_on_screen(self, window):
        window.update_idletasks()  # Ensure all widgets are rendered
        # Use requested width/height since actual size might not be set yet
        width = window.winfo_width()
        height = window.winfo_height()
        # Get main window's position and size
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_width = self.root.winfo_width()
        main_height = self.root.winfo_height()
        # Calculate center position within main window
        x = main_x + (main_width - width) // 2
        y = main_y + (main_height - height) // 2
        # Ensure positive coordinates (avoid negative offsets)
        x = max(0, x)
        y = max(0, y)
        # Set geometry
        window.geometry(f'{width}x{height}+{x}+{y}')
       
    def center_window_absolute(self, window):
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')

    def on_node_select(self, node):
        # Reset the previous selected node's appearance
        if self.previous_selected_node:
            self.canvas.itemconfig(self.previous_selected_node.shape, outline=ColorConfig.current.NODE_OUTLINE_DEFAULT, width=2)

        # Update the appearance of the current selected node
        self.canvas.itemconfig(node.shape, outline=ColorConfig.current.NODE_HIGHLIGHT, width=4)  # orange outline with a width of 4

        # Update the information panel
        self.node_name_label.config(text=node.name)

        # Update the VLAN info panel dynamically
        info_label_style = {'font': ('Helvetica', 10),
                            'bg': ColorConfig.current.INFO_NOTE_BG,
                            'fg': ColorConfig.current.INFO_TEXT,
                            'anchor': 'w'}
        info_value_style = {'font': ('Helvetica', 10),
                            'bg': ColorConfig.current.INFO_NOTE_BG,
                            'fg': ColorConfig.current.INFO_TEXT}
        self.refresh_info_panel_vlans(node, info_label_style, info_value_style)

        # Update the selected and previous selected nodes
        self.previous_selected_node = node
        self.selected_node = node

    def open_node_window(self, node=None, event=None):   
        if hasattr(self, 'node_window') and self.node_window and self.node_window.winfo_exists():
            self.node_window.lift()
            return

        USE_GRAB = False  # Modal grab disabled to avoid focus/input bugs

        # Placeholders for widget references so they are accessible in close_node_editor
        name_entry = None
        VLAN_entries = {}
        remote_entry = None
        file_entry = None
        web_entry = None

        def close_node_editor():
            if USE_GRAB:
                try:
                    self.node_window.grab_release()
                except Exception:
                    pass
            try:
                self.node_window.destroy()
            except Exception:
                pass
            self.node_window = None
            # Ensure node_list_editor is re-enabled if it exists
            if hasattr(self, 'node_list_editor') and self.node_list_editor and self.node_list_editor.winfo_exists():
                # Ensure the node list editor is enabled and interactive
                try:
                    self.node_list_editor.attributes("-disabled", False)
                except Exception:
                    pass
                try:
                    self.node_list_editor.deiconify()
                    self.node_list_editor.lift()
                    self.node_list_editor.focus_force()
                except Exception:
                    pass
            # Optionally, restore focus to the main window as well
            try:
                self.root.focus_force()
            except Exception:
                pass

        # Dynamically calculate window height based on VLAN count
        num_vlans = len(self.vlan_label_names)
        if hasattr(self, "node_window_height"):
            base_height = getattr(self, "node_window_height", DEFAULT_NODE_HEIGHT)
        else:
            base_height = DEFAULT_NODE_HEIGHT
        # Dynamic: default for 4 VLANs, adjust for more/fewer
        dynamic_height = DEFAULT_NODE_HEIGHT + (num_vlans - 4) * NODE_HEIGHT_PER_VLAN
        self.node_window_height = dynamic_height
        
        win, content = self.create_popup("Edit Node" if node else "Create Node", 400, dynamic_height, on_close=close_node_editor, grab=False)
        self.node_window = win
        win.lift(self.root)
        win.attributes("-topmost", True)
        if USE_GRAB:
            try:
                win.grab_set()
            except Exception:
                pass
        win.protocol("WM_DELETE_WINDOW", close_node_editor)
        win.focus_force()

        label_args = {'bg': ColorConfig.current.FRAME_BG, 'fg': ColorConfig.current.BUTTON_TEXT, 'font': ('Helvetica', 10)}
        entry_args = {'bg': ColorConfig.current.ENTRY_FOCUS_BG, 'fg': ColorConfig.current.ENTRY_TEXT, 'insertbackground': ColorConfig.current.ENTRY_TEXT}

        # Node Name
        name_entry = tk.Entry(content, **entry_args)
        tk.Label(content, text="Node Name:", **label_args).grid(row=0, column=0, padx=10, pady=5, sticky="e")
        name_entry.grid(row=0, column=1, padx=10, pady=5)
        if node: name_entry.insert(0, node.name)
        name_entry.focus_set()
        name_entry.focus_force()

        VLAN_entries = {}
        # Sort VLANs by label for display
        # Use self.vlan_label_order if set, else sort by label
        if hasattr(self, "vlan_label_order") and self.vlan_label_order:
            ordered_keys = [v for v in self.vlan_label_order if v in self.vlan_label_names]
            # Add any remaining VLANs not in vlan_label_order at the end
            ordered_keys += [v for v in self.vlan_label_names if v not in ordered_keys]
            sorted_vlans = ordered_keys
        else:
            sorted_vlans = sorted(self.vlan_label_names.keys(), key=lambda k: self.vlan_label_names.get(k, k))
        for i, vlan in enumerate(sorted_vlans, start=1):
            vlan_label = self.vlan_label_names.get(vlan, vlan)
            tk.Label(content, text=f"{vlan_label}:", **label_args).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry = tk.Entry(content, **entry_args)
            entry.grid(row=i, column=1, padx=10, pady=5)
            if node: entry.insert(0, node.vlans.get(vlan, ""))
            VLAN_entries[vlan] = entry


        vlan_row_offset = len(self.vlan_label_names) + 1
        
        tk.Label(content, text="Remote Desktop Address: ", **label_args).grid(row=vlan_row_offset, column=0, padx=10, pady=5, sticky="e")
        remote_entry = tk.Entry(content, **entry_args)
        remote_entry.grid(row=vlan_row_offset, column=1, padx=10, pady=5)
        if node: remote_entry.insert(0, node.remote_desktop_address)
        
        tk.Label(content, text="File Path: ", **label_args).grid(row=vlan_row_offset + 1, column=0, padx=10, pady=5, sticky="e")
        file_entry = tk.Entry(content, **entry_args)
        file_entry.grid(row=vlan_row_offset + 1, column=1, padx=10, pady=5)
        if node: file_entry.insert(0, node.file_path)
        
        tk.Label(content, text="Web Config URL:", **label_args).grid(row=vlan_row_offset + 2, column=0, padx=10, pady=5, sticky="e")
        web_entry = tk.Entry(content, **entry_args)
        web_entry.grid(row=vlan_row_offset + 2, column=1, padx=10, pady=5)
        if node: web_entry.insert(0, node.web_config_url)
        
        # Calculate the row for the spacer and Save button
        save_row = vlan_row_offset + 4  # 3 fields after VLANs, 1 spacer row
        
        # Add a spacer row that expands to push the Save button to the bottom
        content.grid_rowconfigure(save_row - 1, weight=1)
        
        # Label for displaying save notes/messages (just above Save button)
        save_note_label = tk.Label(content, text="", fg="#ff9900", bg=ColorConfig.current.FRAME_BG, font=('Helvetica', 10))
        save_note_label.grid(row=save_row - 1, column=0, columnspan=2, pady=(0, 5))

        def save_node():
            if self.mode != "Configuration":
                save_note_label.config(text="Switch to Configuration mode to save or update nodes.")
                return
            name = name_entry.get()
            vlan_ips = {vlan: VLAN_entries[vlan].get() for vlan in VLAN_entries}
            remote = remote_entry.get()
            path = file_entry.get()
            web = web_entry.get()
            if node:
                node.update_info(
                    name,
                    vlans=vlan_ips,
                    remote_desktop_address=remote,
                    file_path=path,
                    web_config_url=web
                )
                self.on_node_select(node)
                self.unsaved_changes = True
            else:
                if name and event:
                    new_node = NetworkNode(
                        self.canvas,
                        name,
                        event.x,
                        event.y,
                        vlans=vlan_ips,
                        remote_desktop_address=remote,
                        file_path=path,
                        web_config_url=web
                    )
                    self.nodes.append(new_node)
                    self.on_node_select(new_node)
            if hasattr(self, 'node_list_editor') and self.node_list_editor and self.node_list_editor.winfo_exists():
                self.node_list_editor.lift()
                self.node_list_editor.focus_set()
            close_node_editor()

        tk.Button(
            content,
            text="Save",
            command=save_node,
            fg=ColorConfig.current.BUTTON_TEXT,
            bg=ColorConfig.current.BUTTON_BG,
            width=12  # Fixed width so button size does not change on resize
        ).grid(
            row=save_row,
            column=0,
            columnspan=2,
            pady=10
        )
        self.fix_window_geometry(self.node_window, 340, 360)
        

    def create_node(self, event):
        self.open_node_window(event=event)
        self.unsaved_changes = True
             
    def toggle_groups_mode(self):
        if self.groups_mode_active:
            self.groups_mode_active = False
            self.groups_button.config(relief=tk.RAISED, text="Groups")
            self.canvas.config(cursor="")
            # Hide banner label
            self.groups_banner_label.pack_forget()
            self.make_popup_closer("group_editor_window")()  # Close editor
            self.canvas.bind('<B1-Motion>', self.move_node)
        else:
            self.groups_mode_active = True
            self.groups_button.config(relief=tk.SUNKEN, text="Groups (Active)")
            self.canvas.config(cursor="crosshair")
            # Show banner label
            self.groups_banner_label.config(
                text="Groups Mode Active: Click and Drag to create a group. Click a group to edit."
            )
            self.groups_banner_label.pack(side=tk.TOP, fill=tk.X)
            self.open_group_editor()  # Open editor
            self.canvas.bind('<B1-Motion>', self.handle_mouse_drag)

    def handle_mouse_click(self, event):
        """Handle mouse click events based on the current mode"""
        if self.groups_mode_active:
            # In groups mode, select a group if clicked on one
            self.group_manager.select_group(event)
        else:
            # Normal node selection handled by the node's on_click method
            pass
    
    def handle_mouse_drag(self, event):
        """Handle mouse drag events based on the current mode"""
        if self.groups_mode_active:
            # In groups mode, update the rectangle being drawn
            if not hasattr(self.group_manager, 'drawing') or not self.group_manager.drawing:
                self.group_manager.start_drawing(event)
            else:
                self.group_manager.update_drawing(event)
        else:
            # Normal node movement
            self.move_node(event)
    
    def handle_mouse_release(self, event):
        """Handle mouse release events based on the current mode"""
        if self.groups_mode_active:
            # In groups mode, finish drawing the rectangle
            if hasattr(self.group_manager, 'drawing') and self.group_manager.drawing:
                self.group_manager.finish_drawing(event)
        else:
            # Normal node deselection
            self.deselect_node(event)
    
    def move_node(self, event):
        if not event.state & 0x001:
            canvas_x = self.canvas.canvasx(event.x)
            canvas_y = self.canvas.canvasy(event.y)

            # If no object is currently selected, check if one was clicked
            if self.selected_node is None:
                for node in self.nodes:
                    if self.canvas.find_withtag(tk.CURRENT) in (node.shape, node.text):
                        self.selected_node = node
                        break

            # Only move if a node is actively selected
            if self.selected_node:
                self.selected_node.update_position(canvas_x, canvas_y)
                self.unsaved_changes = True
            else:
                self.selected_node = None

    def deselect_node(self, event=None):
        self.selected_node = None

    def remove_node(self, node):
        if self.mode == "Configuration":
            # Remove all connections and connection labelsrelated to the node
            for connection in node.connections[:]:
                self.canvas.delete(connection.line)
                if connection.label_id:
                    self.canvas.delete(connection.label_id)
                if hasattr(connection, 'label_bg') and connection.label_bg:
                    self.canvas.delete(connection.label_bg)
                connection.node1.connections.remove(connection)
                connection.node2.connections.remove(connection)
            # Remove the node from the canvas
            self.canvas.delete(node.shape)
            self.canvas.delete(node.text)
            # Remove the node from the nodes list
            self.nodes.remove(node)
            # Clear the selected node
            self.selected_node = None
            # Clear the info panel if no node is selected
            self.node_name_label.config(text="Name: -")
            self.node_ip_label.config(text="IP: -")
            self.unsaved_changes = True
        else:
            # Show node deletion banner for 5 seconds
            self.node_banner_label.config(
                text="Switch to Configuration mode to delete nodes.",
                bg=ColorConfig.current.FRAME_BG,
                fg="#ff9900",
                font=("Helvetica", 12, "bold"),
                height=0
            )
            self.node_banner_label.place(relx=0.5, rely=1.0, relwidth=1, anchor='s')
            self.node_banner_label.lift()
            self.root.after(5000, self.node_banner_label.place_forget)
        
    def raise_all_nodes(self): # for making nodes display above the connection lines
        for node in self.nodes:
            self.canvas.tag_raise(node.shape)
            self.canvas.tag_raise(node.text)

    def clear_current_loaded(self): # for clearing the current nodes on the canvas before loading a new one
        for node in self.nodes:
            for connection in node.connections:
                self.canvas.delete(connection.line)
                if connection.label_id:
                    self.canvas.delete(connection.label_id)  # Remove connection label
                if hasattr(connection, 'label_bg') and connection.label_bg:
                    self.canvas.delete(connection.label_bg)  # Remove connection label background
            self.canvas.delete(node.shape)
            self.canvas.delete(node.text)
        self.nodes.clear()

        # Clear all stickynotes
        stickynotes = self.canvas.find_withtag("sticky_note")
        for note in stickynotes:
            self.canvas.delete(note)
        sticky_bgs = self.canvas.find_withtag("sticky_bg")
        for bg in sticky_bgs:
            self.canvas.delete(bg)
            
        # Clear all groups
        for group in self.group_manager.groups:
            self.canvas.delete(group.rectangle)
            self.canvas.delete(group.text)
        self.group_manager.groups.clear()
        self.group_manager.selected_group = None
            
    def clear_node_status(self):
        # Set the node color of all nodes to NODE_DEFAULT.
        for node in self.nodes:
            self.canvas.itemconfig(node.shape, fill=ColorConfig.current.NODE_DEFAULT)
 
    def ping_all(self):
        for node in self.nodes:
            node.ping()
    
    def show_sticky_note_popup(self, initial_text, on_ok_callback):
        # Destroy any existing sticky note popup
        if getattr(self, "sticky_note_popup", None) and self.sticky_note_popup.winfo_exists():
            try:
                self.sticky_note_popup.grab_release()
            except Exception:
                pass
            try:
                self.sticky_note_popup.destroy()
            except Exception:
                pass
            self.sticky_note_popup = None

        popup, content = self.create_popup("Sticky Note", 320, 150, grab=True)
        self.sticky_note_popup = popup
        self.center_window_absolute(popup)
        content.config(highlightthickness=0)

        label = tk.Label(
            content,
            text="Enter note text:",
            bg=ColorConfig.current.FRAME_BG,
            fg=ColorConfig.current.BUTTON_TEXT
        )
        label.pack(pady=(12, 4))
        entry = tk.Entry(
            content,
            width=40,
            bg=getattr(ColorConfig.current, "ENTRY_BG", ColorConfig.current.FRAME_BG),
            fg=ColorConfig.current.ENTRY_TEXT if hasattr(ColorConfig.current, "ENTRY_TEXT") else ColorConfig.current.BUTTON_TEXT,
            insertbackground=ColorConfig.current.ENTRY_TEXT if hasattr(ColorConfig.current, "ENTRY_TEXT") else ColorConfig.current.BUTTON_TEXT
        )
        entry.pack(padx=12, pady=(0, 12))
        popup.after(100, lambda: entry.focus_force())
        if initial_text:
            entry.insert(0, initial_text)

        def close_popup():
            try:
                if popup.grab_current() == popup:
                    popup.grab_release()
            except Exception:
                pass
            try:
                popup.destroy()
            except Exception:
                pass
            if getattr(self, "sticky_note_popup", None) == popup:
                self.sticky_note_popup = None
            # Restore focus and shortcuts to main window
            try:
                self.regain_focus()
            except Exception:
                pass

        def on_ok():
            text = entry.get()
            if text.strip():
                on_ok_callback(text)
            close_popup()

        def on_cancel():
            close_popup()

        btn_frame = tk.Frame(content, bg=ColorConfig.current.FRAME_BG)
        btn_frame.pack(pady=(0, 8))
        ok_btn = tk.Button(
            btn_frame,
            text="OK",
            width=10,
            command=on_ok,
            bg=getattr(ColorConfig.current, "BUTTON_BG", "#444"),
            fg=getattr(ColorConfig.current, "BUTTON_TEXT", "#fff"),
            activebackground=getattr(ColorConfig.current, "BUTTON_BG", "#444"),
            activeforeground=getattr(ColorConfig.current, "BUTTON_TEXT", "#fff")
        )
        ok_btn.pack(side=tk.LEFT, padx=6)
        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            width=10,
            command=on_cancel,
            bg=getattr(ColorConfig.current, "BUTTON_BG", "#444"),
            fg=getattr(ColorConfig.current, "BUTTON_TEXT", "#fff"),
            activebackground=getattr(ColorConfig.current, "BUTTON_BG", "#444"),
            activeforeground=getattr(ColorConfig.current, "BUTTON_TEXT", "#fff")
        )
        cancel_btn.pack(side=tk.LEFT, padx=6)

        content.lift()
        content.update_idletasks()
        popup.protocol("WM_DELETE_WINDOW", on_cancel)
        popup.bind('<Return>', lambda e: on_ok())
        popup.bind('<Escape>', lambda e: on_cancel())

    def create_sticky_note(self, event=None):
        if self.mode == "Configuration":
            def do_create(text):
                x, y = (event.x, event.y) if event else (50, 50)
                note = StickyNote(self.canvas, text, x, y, self)
                self.stickynotes.append(note)
                self.unsaved_changes = True
            self.show_sticky_note_popup("", do_create)

    def remove_sticky(self, sticky):
        # Erase sticky from the canvas
        self.canvas.delete(sticky.note)
        self.canvas.delete(sticky.bg_shape)

        # Remove it from the list
        if sticky in self.stickynotes:
            self.stickynotes.remove(sticky)     

    def create_connection(self, event, edit_connection=None):     # Draw or edit a connection
        if self.mode == "Configuration":
            # Check if the connection window is already open
            if hasattr(self, 'connection_window') and self.connection_window and self.connection_window.winfo_exists():
                self.connection_window.lift()
                return

            # Editing an existing connection
            if edit_connection is not None:
                def close_connection_window():
                    try:
                        self.connection_window.destroy()
                    except Exception:
                        pass
                    self.connection_window = None
                    try:
                        self.root.focus_force()
                    except Exception:
                        pass

                dialog, content = self.create_popup("Connection Details", 400, 150, on_close=close_connection_window, grab=True)
                self.center_window_absolute(dialog)
                self.connection_window = dialog
                label_label = tk.Label(content, text="Label:", bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.INFO_TEXT)
                label_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
                label_entry = tk.Entry(content, width=40, bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.ENTRY_TEXT, insertbackground=ColorConfig.current.ENTRY_TEXT)
                label_entry.grid(row=0, column=1, padx=10, pady=5)
                label_entry.insert(0, edit_connection.label if edit_connection.label else "")

                info_label = tk.Label(content, text="Info (on hover):", bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.INFO_TEXT)
                info_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
                info_entry = tk.Entry(content, width=40, bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.ENTRY_TEXT, insertbackground=ColorConfig.current.ENTRY_TEXT)
                info_entry.grid(row=1, column=1, padx=10, pady=5)
                info_entry.insert(0, edit_connection.connectioninfo if edit_connection.connectioninfo else "")

                def submit():
                    edit_connection.label = label_entry.get()
                    edit_connection.connectioninfo = info_entry.get()
                    edit_connection.update_label()
                    self.unsaved_changes = True
                    close_connection_window()

                self.connection_window.protocol("WM_DELETE_WINDOW", close_connection_window)

                ok_button = tk.Button(
                    content,
                    text="OK",
                    command=submit,
                    bg=ColorConfig.current.BUTTON_BG,
                    fg=ColorConfig.current.BUTTON_TEXT,
                    activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
                    activeforeground=ColorConfig.current.BUTTON_ACTIVE_TEXT
                )
                ok_button.grid(row=2, column=0, columnspan=2, pady=10)

                self.root.wait_window(self.connection_window)
                return

            # Creating a new connection (existing logic)
            clicked_items = self.canvas.find_withtag("current")
            if clicked_items:
                clicked_item_id = clicked_items[0]  # Get the first item's ID from the tuple
                for node in self.nodes:
                    if clicked_item_id in (node.shape, node.text):
                        if self.connection_start_node is None:
                            self.connection_start_node = node
                            return  # Return after setting the start node
                        elif self.connection_start_node != node:
                            def close_connection_window():
                                try:
                                    self.connection_window.destroy()
                                except Exception:
                                    pass
                                self.connection_window = None
                                try:
                                    self.root.focus_force()
                                except Exception:
                                    pass

                            dialog, content = self.create_popup("Connection Details", 400, 150, on_close=close_connection_window, grab=True)
                            self.center_window_absolute(dialog)
                            self.connection_window = dialog
                            label_label = tk.Label(content, text="Label:", bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.INFO_TEXT)
                            label_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
                            label_entry = tk.Entry(content, width=40, bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.ENTRY_TEXT, insertbackground=ColorConfig.current.ENTRY_TEXT)
                            label_entry.grid(row=0, column=1, padx=10, pady=5)

                            info_label = tk.Label(content, text="Info (on hover):", bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.INFO_TEXT)
                            info_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
                            info_entry = tk.Entry(content, width=40, bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.ENTRY_TEXT, insertbackground=ColorConfig.current.ENTRY_TEXT)
                            info_entry.grid(row=1, column=1, padx=10, pady=5)

                            def submit():
                                label = label_entry.get()
                                info = info_entry.get()
                                connection = ConnectionLine(self.canvas, self.connection_start_node, node, label=label, connectioninfo=info, gui=self)
                                self.connection_start_node = None
                                self.raise_all_nodes()
                                self.unsaved_changes = True
                                close_connection_window()

                            self.connection_window.protocol("WM_DELETE_WINDOW", close_connection_window)

                            ok_button = tk.Button(
                                content,
                                text="OK",
                                command=submit,
                                bg=ColorConfig.current.BUTTON_BG,
                                fg=ColorConfig.current.BUTTON_TEXT,
                                activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
                                activeforeground=ColorConfig.current.BUTTON_ACTIVE_TEXT
                            )
                            ok_button.grid(row=2, column=0, columnspan=2, pady=10)

                            self.root.wait_window(self.connection_window)
                            self.connection_start_node = None
                            self.raise_all_nodes()
                            self.unsaved_changes = True
                            return  # Return after creating the connection

    def on_alt_press(self, event):
        self.alt_pressed = True

    def on_alt_release(self, event):
        self.alt_pressed = False

    def remove_connection(self, event): 
        if self.mode == "Configuration":
            clicked_item = self.canvas.find_withtag("current")
            if clicked_item:
                clicked_item_id = clicked_item[0]
                for node in self.nodes:
                    for connection in node.connections[:]:
                        if connection.line == clicked_item_id:
                            # Remove connection from canvas
                            self.canvas.delete(connection.line)
                            if connection.label_id:
                                self.canvas.delete(connection.label_id)
                            if hasattr(connection, 'label_bg') and connection.label_bg:
                                self.canvas.delete(connection.label_bg)
                            
                            # Remove connection from both nodes
                            connection.node1.connections.remove(connection)
                            connection.node2.connections.remove(connection)

                            return  # Exit after removing connection

    def keyboard_save(self, event=None):
        self.save_network_state()

    def keyboard_load(self, event=None):
        self.load_network_state()

    def save_network_state(self):
        state = {
            'nodes': [],
            'connections': [],
            'vlan_labels': self.vlan_label_names,
            'vlan_label_order': getattr(self, 'vlan_label_order', []),
            'stickynotes': [],
            'groups': []
        }

        # Gather node data
        for node in self.nodes:
            node_data = {
                'name': node.name,
                'x': node.x,
                'y': node.y,
                'remote_desktop_address': node.remote_desktop_address,
                'file_path': node.file_path,
                'web_config_url': node.web_config_url
            }
            # Serialize all VLANs dynamically
            if hasattr(node, "vlans") and isinstance(node.vlans, dict):
                for vlan_key, vlan_value in node.vlans.items():
                    node_data[vlan_key] = vlan_value
            state['nodes'].append(node_data)

        # Gather connection data
        lines_seen = set()
        for node in self.nodes:
            for conn in node.connections:
                if conn not in lines_seen:
                    connection_data = {
                        'from': self.nodes.index(conn.node1),
                        'to': self.nodes.index(conn.node2),
                        'label': conn.label
                    }
                    if conn.connectioninfo:
                        connection_data['connectioninfo'] = conn.connectioninfo  # <-- add this
                    state['connections'].append(connection_data)
                    lines_seen.add(conn)


        # Gather sticky-note data
        for note in self.stickynotes:
            bbox = self.canvas.bbox(note.note)
            if bbox:
                # Top-left corner of the sticky note text
                x1, y1 = bbox[0], bbox[1]
                text = self.canvas.itemcget(note.note, "text")
                state['stickynotes'].append({
                    'text': text,
                    'x': x1,
                    'y': y1
                })
                
        # Gather group data
        for group in self.group_manager.groups:
            group_data = group.to_dict()
            state['groups'].append(group_data)

        # Save group color presets and window height from in-memory values or defaults
        # Always save the current in-memory color presets, including any custom presets
        state["group_color_presets"] = getattr(self.group_manager, "color_presets", DEFAULT_PRESETS)
        state["group_window_height"] = getattr(self.group_manager, "window_height", DEFAULT_HEIGHT)

        # Save node window height
        state["node_window_height"] = getattr(self, "node_window_height", DEFAULT_NODE_HEIGHT)
        
        # Add custom commands to state
        state["custom_commands"] = self.custom_commands

        # Prompt user for a file location and save the JSON file
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(state, f, indent=4)
            self.validate_and_fix_vlans(state, file_path)

        # Close the legend window if it exists
        if self.legend_window and self.legend_window.winfo_exists():
            self.legend_window.destroy()


    def new_network_state(self):
        # Confirm with the user before clearing the network state
        response = self._custom_askyesno("New Network State", "Are you sure you want to create a new network state? This will clear all current loaded data.")
        if response:
            self.clear_current_loaded()  # Clear existing nodes and connections
            self.clear_node_status()  # Reset the status of all nodes
            self.legend_window.destroy()  # Close the legend window

            # Reset VLAN labels to default values
            self.vlan_label_names = {'VLAN_1': 'VLAN_1', 'VLAN_2': 'VLAN_2', 'VLAN_3': 'VLAN_3', 'VLAN_4': 'VLAN_4'}
            self.vlan_label_order = list(self.vlan_label_names.keys())
            # Reset color presets in group_editor_config.json to defaults
            try:
                with open(get_resource_path(CONFIG_PATH), "r") as f:
                    config = json.load(f)
            except Exception:
                config = {}
            config["color_presets"] = DEFAULT_PRESETS
            with open(get_resource_path(CONFIG_PATH), "w") as f:
                json.dump(config, f, indent=4)

            # Also reset in-memory color presets to defaults
            if hasattr(self, "group_manager"):
                self.group_manager.color_presets = DEFAULT_PRESETS

            # Reset custom commands file to empty
            try:
                with open(get_resource_path("data/custom_commands.json"), "w") as f:
                    json.dump({}, f, indent=4)
                self.custom_commands = {}
                if hasattr(self, "custom_commands_listbox"):
                    self.custom_commands_listbox.delete(0, "end")
            except Exception:
                pass
    
            # Show operator guidance window if in Operator mode
            if self.mode == "Operator":
                show_operator_guidance(self.root, self.center_window_on_screen, self.custom_font)

    def validate_and_fix_vlans(self, network_data, file_path):
        """
        Ensure every node in the network data has all VLAN keys listed in 'vlan_labels'.
        If a VLAN key is missing from a node, add it with an empty string as the value.
        After fixing, overwrite the original JSON file with the updated data (pretty-printed).
        """
        vlan_labels = network_data.get("vlan_labels", {})
        if isinstance(vlan_labels, dict):
            vlan_keys = list(vlan_labels.keys())
        else:
            vlan_keys = list(vlan_labels)
        for idx, node in enumerate(network_data.get("nodes", [])):
            missing_vlans = []
            for vlan in vlan_keys:
                if vlan not in node:
                    node[vlan] = ""
                    missing_vlans.append(vlan)
            if missing_vlans:
                pass
        # Write the updated network_data back to the original JSON file
        import json
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(network_data, f, indent=4, ensure_ascii=False)
        
    def load_network_state_from_path(self, file_path):
        with open(file_path, 'r') as f:
            self.clear_current_loaded()  # Clears existing nodes, connections, and stickynotes
            state = json.load(f)

            # Reset custom commands file to empty if not present in state
            if "custom_commands" not in state or not state["custom_commands"]:
                try:
                    with open("data/custom_commands.json", "w") as fcc:
                        json.dump({}, fcc, indent=4)
                except Exception:
                    pass

            # Extract group editor config from state, fallback to defaults if missing/None
            group_color_presets = state.get("group_color_presets", DEFAULT_PRESETS)
            if not group_color_presets:
                group_color_presets = DEFAULT_PRESETS
            group_window_height = state.get("group_window_height", DEFAULT_HEIGHT)
            if not group_window_height:
                group_window_height = DEFAULT_HEIGHT

            # Load node window height
            self.node_window_height = state.get("node_window_height", DEFAULT_NODE_HEIGHT)
            
            # Ensure group_manager has up-to-date color presets
            if hasattr(self, "group_manager"):
                self.group_manager.color_presets = group_color_presets

            # Load VLAN labels only for those present in the file or referenced in nodes
            vlan_labels_in_file = set(state.get('vlan_labels', {}).keys())
            vlan_labels_in_nodes = set()
            for node_data in state.get('nodes', []):
                vlan_labels_in_nodes.update({k for k in node_data if k.startswith('VLAN_')})
            used_vlans = vlan_labels_in_file | vlan_labels_in_nodes
            self.vlan_label_names = {vlan: state.get('vlan_labels', {}).get(vlan, vlan) for vlan in used_vlans}
            # Restore VLAN order if present, else use current order
            if 'vlan_label_order' in state:
                self.vlan_label_order = [v for v in state['vlan_label_order'] if v in self.vlan_label_names]
                # Add any new VLANs not in saved order to the end
                for v in self.vlan_label_names:
                    if v not in self.vlan_label_order:
                        self.vlan_label_order.append(v)
            else:
                self.vlan_label_order = list(self.vlan_label_names.keys())
            # Update UI to only show these VLANs
            for vlan, label in self.vlan_title_labels.items():
                if vlan in self.vlan_label_names:
                    label.config(text=self.vlan_label_names[vlan] + ":")
                else:
                    label.config(text="")
            # VLAN checkboxes removed; dynamic VLAN UI is updated via refresh_vlan_entries()

            # Load nodes
            for node_data in state.get('nodes', []):
                # Extract and convert legacy VLAN keys to new structure
                vlans = {k: v for k, v in node_data.items() if k.startswith('VLAN_')}
                # Remove legacy VLAN keys from node_data to avoid TypeError
                for vlan_key in vlans.keys():
                    node_data.pop(vlan_key)
                node = NetworkNode(
                    self.canvas,
                    node_data['name'],
                    node_data['x'],
                    node_data['y'],
                    vlans=vlans,
                    remote_desktop_address=node_data.get('remote_desktop_address', ''),
                    file_path=node_data.get('file_path', ''),
                    web_config_url=node_data.get('web_config_url', '')
                )
                self.nodes.append(node)
            self.highlight_matching_nodes()

            # Load connections
            for conn_data in state.get('connections', []):
                node1 = self.nodes[conn_data['from']]
                node2 = self.nodes[conn_data['to']]
                label = conn_data.get('label', '')
                tooltip = conn_data.get('connectioninfo', None)
                ConnectionLine(self.canvas, node1, node2, label=label, connectioninfo=tooltip, gui=self)


            # Load sticky notes
            self.stickynotes.clear()
            for sn in state.get('stickynotes', []):
                note = StickyNote(self.canvas, sn['text'], sn['x'], sn['y'])
                self.stickynotes.append(note)
                
            # Load groups
            self.group_manager.groups = []
            for group_data in state.get('groups', []):
                group = RectangleGroup.from_dict(self.canvas, group_data, color_presets=group_color_presets)
                self.group_manager.groups.append(group)
                
            # Make sure groups are behind nodes and connections
            self.group_manager.send_all_to_back()
                
            # Make sure nodes appear over connection lines
            for node in self.nodes:
                node.raise_node()

        # Save this file path for "load last file" feature
        self.save_last_file_path(file_path)

        # Optional: if you want the legend window to close after loading
        if self.legend_window is not None and self.legend_window.winfo_exists():
            self.legend_window.destroy()
            self.legend_window = None
        
    def load_network_state(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'r') as f:
                self.clear_current_loaded()  # Clear existing nodes, connections and labels
                state = json.load(f)
                if state is not None:
                    self.validate_and_fix_vlans(state, file_path)
                
                # Reset custom commands file to empty if not present in state
                if "custom_commands" not in state or not state["custom_commands"]:
                    try:
                        with open("data/custom_commands.json", "w") as fcc:
                            json.dump({}, fcc, indent=4)
                    except Exception:
                        pass
                
                # Load custom commands if present
                if "custom_commands" in state:
                    self.custom_commands = state["custom_commands"]
                    self.save_custom_commands()
                
                # group_editor_config.json sync logic removed; settings are now only saved in the main save file
                # Load VLAN labels only for those present in the file or referenced in nodes
                vlan_labels_in_file = set(state.get('vlan_labels', {}).keys())
                vlan_labels_in_nodes = set()
                for node_data in state.get('nodes', []):
                    vlan_labels_in_nodes.update({k for k in node_data if k.startswith('VLAN_')})
                used_vlans = vlan_labels_in_file | vlan_labels_in_nodes
                self.vlan_label_names = {vlan: state.get('vlan_labels', {}).get(vlan, vlan) for vlan in used_vlans}
                # Restore VLAN order if present, else use current order
                if 'vlan_label_order' in state:
                    self.vlan_label_order = [v for v in state['vlan_label_order'] if v in self.vlan_label_names]
                    for v in self.vlan_label_names:
                        if v not in self.vlan_label_order:
                            self.vlan_label_order.append(v)
                else:
                    self.vlan_label_order = list(self.vlan_label_names.keys())
                # Update UI to only show these VLANs
                for vlan, label in self.vlan_title_labels.items():
                    if vlan in self.vlan_label_names:
                        label.config(text=self.vlan_label_names[vlan] + ":")
                    else:
                        label.config(text="")
                # VLAN checkboxes removed; dynamic VLAN UI is updated via refresh_vlan_entries()
                # Load nodes
                for node_data in state['nodes']:
                    # Extract and convert legacy VLAN keys to new structure
                    vlans = {k: v for k, v in node_data.items() if k.startswith('VLAN_')}
                    # Remove legacy VLAN keys from node_data to avoid TypeError
                    for vlan_key in vlans.keys():
                        node_data.pop(vlan_key)
                    node = NetworkNode(
                        self.canvas,
                        node_data['name'],
                        node_data['x'],
                        node_data['y'],
                        vlans=vlans,
                        remote_desktop_address=node_data.get('remote_desktop_address', ''),
                        file_path=node_data.get('file_path', ''),
                        web_config_url=node_data.get('web_config_url', '')
                    )
                    self.nodes.append(node)
                    self.highlight_matching_nodes()
                # Ensure gui.nodes references the loaded node list for Node List window
                self.gui.nodes = self.nodes
                # Load connections
                for conn_data in state['connections']:
                    node1 = self.nodes[conn_data['from']]
                    node2 = self.nodes[conn_data['to']]
                    label = conn_data.get('label', '')  # Get the label if it exists
                    tooltip = conn_data.get('connectioninfo', None)
                    ConnectionLine(self.canvas, node1, node2, label=label, connectioninfo=tooltip, gui=self)
                
                # Load groups
                self.group_manager.groups = []
                group_color_presets = state.get("group_color_presets", DEFAULT_PRESETS)
                if hasattr(self, "group_manager"):
                    self.group_manager.color_presets = group_color_presets
                for group_data in state.get('groups', []):
                    group = RectangleGroup.from_dict(self.canvas, group_data, color_presets=group_color_presets)
                    self.group_manager.groups.append(group)
                
                # Make sure groups are behind nodes and connections
                self.group_manager.send_all_to_back()
                
                # Raise all nodes after creating connections to ensure they appear on top
                for node in self.nodes:
                    node.raise_node()
            self.save_last_file_path(file_path)  # Save the last file path
            if self.legend_window is not None:
                self.legend_window.destroy()  # Close the legend window

        # Show operator guidance window if in Operator mode
        if self.mode == "Operator":
            show_operator_guidance(self.root, self.center_window_on_screen, self.custom_font)

    def save_last_file_path(self, file_path):
        with open(get_resource_path('data/last_file_path.ini'), 'w') as f:
            f.write(file_path)

    def load_last_file(self):
        try:
            with open(get_resource_path('data/last_file_path.ini'), 'r') as f:
                last_file_path = f.read().strip()
                if os.path.exists(last_file_path):
                    self.load_network_state_from_path(last_file_path)
                    if self.legend_window is not None:
                        self.legend_window.destroy()
                        self.legend_window = None  # Reset the attribute after destroying the window
        except FileNotFoundError:
            pass
        
    def highlight_matching_nodes(self):
        my_ips = get_ip_addresses()
        host_node_set = False  
        for node in self.nodes:
            vlan_values = getattr(node, "vlans", {}).values() if hasattr(node, "vlans") and isinstance(node.vlans, dict) else []
            if any(ip in my_ips for ip in vlan_values):
                self.flash_node(node, 9)
                self.host_node = node  # Set the host node
                host_node_set = True

    def flash_node(self, node, times, original_color=ColorConfig.current.NODE_DEFAULT, flash_color=ColorConfig.current.NODE_HOST):
        if times > 0:
            next_color = flash_color if self.canvas.itemcget(node.shape, "fill") == original_color else original_color
            self.canvas.itemconfig(node.shape, fill=next_color)
            self.canvas.after(400, lambda: self.flash_node(node, times - 1))
        else:
            self.canvas.itemconfig(node.shape, fill=flash_color)                 

    def toggle_theme(self):
        # Switch the current theme
        if ColorConfig.current == ColorConfig.Light:
            ColorConfig.current = ColorConfig.Dark
            # Only update theme_button text if it exists and is alive
            if hasattr(self, 'theme_button') and self.theme_button.winfo_exists():
                self.theme_button.config(text="Light Mode")
        else:
            ColorConfig.current = ColorConfig.Light
            # Only update theme_button text if it exists and is alive
            if hasattr(self, 'theme_button') and self.theme_button.winfo_exists():
                self.theme_button.config(text="Dark Mode")
        self.update_ui_colors()
        # Redraw all groups to reflect the new color scheme
        if hasattr(self, "group_manager") and hasattr(self.group_manager, "groups"):
            for group in self.group_manager.groups:
                group.update_properties()

# Node list editor moved to node_list.py as open_node_list_editor(gui)

    def open_connection_list_editor(self):
        open_connection_list_editor(self)
        
    def update_ui_colors(self):
        """Update all UI colors when the theme changes."""
        # Update scrollbar styles (re-apply for current theme)
        self._setup_scrollbar_styles()
        # Update groups mode banner label color
        if hasattr(self, "groups_banner_label"):
            self.groups_banner_label.config(
                bg=ColorConfig.current.FRAME_BG,
                fg="#ff9900"
            )
        # Root window
        self.root.configure(bg=ColorConfig.current.FRAME_BG)

       # Buttons frame and its buttons
        self.buttons_frame.config(bg=ColorConfig.current.FRAME_BG)
        button_style = {'bg': ColorConfig.current.BUTTON_BG, 'fg': ColorConfig.current.BUTTON_TEXT,
                        'activebackground': ColorConfig.current.BUTTON_ACTIVE_BG,
                        'activeforeground': ColorConfig.current.BUTTON_ACTIVE_TEXT}
        
        # Safely configure theme_button only if it exists
        if hasattr(self, 'theme_button') and self.theme_button.winfo_exists():
                    self.theme_button.config(**button_style)
        start_menu_button = self.buttons_frame.winfo_children()[0]
        whoamI_button = self.buttons_frame.winfo_children()[2]
        clear_status_button = self.buttons_frame.winfo_children()[3]
        ping_all_button = self.buttons_frame.winfo_children()[4]
        start_menu_button.config(**button_style)
        whoamI_button.config(**button_style)
        clear_status_button.config(**button_style)
        ping_all_button.config(**button_style)

        # Update theme button if it exists (i.e., legend window is open)
        if hasattr(self, 'theme_button') and self.theme_button.winfo_exists():
            self.theme_button.config(text="Dark Mode" if ColorConfig.current == ColorConfig.Light else "Light Mode", **button_style)
        
        # Update all buttons in the buttons frame
        for widget in self.buttons_frame.winfo_children():
            if isinstance(widget, tk.Checkbutton):
                # For Checkbutton widgets, include selectcolor
                widget.config(
                    bg=ColorConfig.current.FRAME_BG,
                    fg=ColorConfig.current.BUTTON_TEXT,
                    selectcolor=ColorConfig.current.FRAME_BG,
                    activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
                    activeforeground=ColorConfig.current.BUTTON_TEXT)
            else:
                # For other widget types (like Button), skip the selectcolor option
                widget.config(
                    bg=ColorConfig.current.BUTTON_BG,
                    fg=ColorConfig.current.BUTTON_TEXT,
                    activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
                    activeforeground=ColorConfig.current.BUTTON_TEXT)
        self.canvas.config(bg=ColorConfig.current.FRAME_BG)
        # Ensure mode button color is correct after all buttons are reset
        self.mode_button.config(
            bg=ColorConfig.current.BUTTON_CONFIGURATION_MODE if self.mode == "Configuration" else ColorConfig.current.BUTTON_BG,
            fg=ColorConfig.current.BUTTON_TEXT
        )
        self.info_panel.config(bg=ColorConfig.current.INFO_NOTE_BG)
        for child in self.info_panel.winfo_children():
            child.config(bg=ColorConfig.current.INFO_NOTE_BG, fg=ColorConfig.current.INFO_TEXT)
        
        # Update legend window if it exists
        if self.legend_window and self.legend_window.winfo_exists():
            outer_frame = self.legend_window.winfo_children()[0]
            title_bar = outer_frame.winfo_children()[0]
            content_frame = outer_frame.winfo_children()[1]
            
            outer_frame.config(bg=ColorConfig.current.BORDER_COLOR)
            title_bar.config(bg=ColorConfig.current.FRAME_BG)
            title_bar.winfo_children()[0].config(bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT)  # title_label
            title_bar.winfo_children()[1].config(bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT)  # close_button
            content_frame.config(bg=ColorConfig.current.FRAME_BG)
            
            for widget in content_frame.winfo_children():
                if isinstance(widget, tk.Label):  # Image label
                    widget.config(bg=ColorConfig.current.FRAME_BG)
                elif isinstance(widget, tk.Button):  # Buttons
                    widget.config(bg=ColorConfig.current.BUTTON_BG, fg=ColorConfig.current.BUTTON_TEXT,
                                activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
                                activeforeground=ColorConfig.current.BUTTON_ACTIVE_TEXT)
                elif isinstance(widget, tk.Checkbutton):  # Checkbox
                    widget.config(bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT,
                                selectcolor=ColorConfig.current.FRAME_BG,
                                activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
                                activeforeground=ColorConfig.current.BUTTON_ACTIVE_TEXT)
            # Update theme button text
            self.theme_button.config(text="Dark Mode" if ColorConfig.current == ColorConfig.Light else "Light Mode")

        # VLAN checkboxes
        # VLAN checkboxes are already updated in the loop above

        # Canvas
        self.canvas.config(bg=ColorConfig.current.FRAME_BG)

        # Info panel and labels
        self.info_panel.config(bg=ColorConfig.current.INFO_NOTE_BG)
        for child in self.info_panel.winfo_children():
            child.config(bg=ColorConfig.current.INFO_NOTE_BG, fg=ColorConfig.current.INFO_TEXT)
        # Reset VLAN label colors unless updated by ping
        for vlan in self.vlan_labels:
            current_bg = self.vlan_labels[vlan].cget("bg")
            if current_bg not in [ColorConfig.current.NODE_PING_SUCCESS, ColorConfig.current.NODE_PING_PARTIAL_SUCCESS, ColorConfig.current.NODE_PING_FAILURE]:
                self.vlan_labels[vlan].config(bg=ColorConfig.current.INFO_NOTE_BG)

        # Update legend window if it exists
        if self.legend_window and self.legend_window.winfo_exists():
            self.legend_window.configure(bg=ColorConfig.current.FRAME_BG)
            for widget in self.legend_window.winfo_children():
                if isinstance(widget, tk.Label):  # Image label
                    widget.config(bg=ColorConfig.current.FRAME_BG)
                elif isinstance(widget, tk.Button):  # Buttons
                    widget.config(**button_style)
                elif isinstance(widget, tk.Checkbutton):  # Checkbox
                    widget.config(bg=ColorConfig.current.FRAME_BG,
                                fg=ColorConfig.current.BUTTON_TEXT,
                                selectcolor=ColorConfig.current.FRAME_BG,
                                activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
                                activeforeground=ColorConfig.current.BUTTON_ACTIVE_TEXT)
            # Update theme button text explicitly
            if hasattr(self, 'theme_button') and self.theme_button.winfo_exists():
                self.theme_button.config(text="Dark Mode" if ColorConfig.current == ColorConfig.Light else "Light Mode", **button_style)

        # Nodes
        for node in self.nodes:
            current_fill = self.canvas.itemcget(node.shape, "fill")
            if current_fill not in [ColorConfig.current.NODE_PING_SUCCESS, ColorConfig.current.NODE_PING_PARTIAL_SUCCESS, ColorConfig.current.NODE_PING_FAILURE, ColorConfig.current.NODE_HOST]:
                self.canvas.itemconfig(node.shape, fill=ColorConfig.current.NODE_DEFAULT)
            self.canvas.itemconfig(node.shape, outline=ColorConfig.current.NODE_OUTLINE_DEFAULT)
            self.canvas.itemconfig(node.text, fill=ColorConfig.current.BUTTON_TEXT)
            if node == self.selected_node:
                self.canvas.itemconfig(node.shape, outline=ColorConfig.current.NODE_HIGHLIGHT)

        # Connections
        for node in self.nodes:
            for conn in node.connections:
                self.canvas.itemconfig(conn.line, fill=ColorConfig.current.Connections)
                if conn.label_id:
                    self.canvas.itemconfig(conn.label_id, fill=ColorConfig.current.INFO_TEXT)
                    if hasattr(conn, 'label_bg') and conn.label_bg:
                        self.canvas.itemconfig(conn.label_bg, fill=ColorConfig.current.INFO_NOTE_BG)

        # Sticky notes
        for item in self.canvas.find_withtag("sticky_note"):
            self.canvas.itemconfig(item, fill=ColorConfig.current.INFO_TEXT)
        for bg in self.canvas.find_withtag("sticky_bg"):
            self.canvas.itemconfig(bg, fill=ColorConfig.current.INFO_NOTE_BG)

        # Zoom buttons
        if hasattr(self, 'zoom_level_label') and self.zoom_level_label.winfo_exists():
            for widget in (self.zoom_in_btn, self.zoom_out_btn, self.zoom_level_label):
                widget.config(bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT)

        if hasattr(self, 'zoom_frame') and self.zoom_frame.winfo_exists():
            self.zoom_frame.config(bg=ColorConfig.current.FRAME_BG)

    def _custom_askyesno(self, title, message):

        result = [None]
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=ColorConfig.current.FRAME_BG)

        # Hide native titlebar and add custom titlebar
        dialog.overrideredirect(True)

        # Ensure dialog is above all other windows
        dialog.lift()
        dialog.attributes('-topmost', True)
        dialog.attributes('-topmost', False)

        def on_close():
            result[0] = None
            dialog.destroy()

        # --- Custom titlebar (no border color behind) ---
        #self.add_custom_titlebar(dialog, title, on_close, toplevel=dialog)

        # --- Frame as main container (border/frame), packed below titlebar ---
        outer_frame = tk.Frame(
            dialog,
            bg=ColorConfig.current.BORDER_COLOR,
            padx=2,
            pady=2
        )
        outer_frame.pack(fill="both", expand=True)
        # Move the border frame below the titlebar
        outer_frame.lift()  # Ensure it's below the titlebar if needed

        # All widgets now go inside an inner frame with FRAME_BG
        inner_frame = tk.Frame(
            outer_frame,
            bg=ColorConfig.current.FRAME_BG
        )

        inner_frame.pack(fill="both", expand=True)

        # Center the dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (250 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (120 // 2)
        dialog.geometry(f"250x138+{x}+{y}")

        label = tk.Label(
            inner_frame,
            text=message,
            bg=ColorConfig.current.FRAME_BG,
            fg=ColorConfig.current.BUTTON_TEXT,
            wraplength=220
        )
        label.pack(pady=(20, 10), padx=10)

        btn_frame = tk.Frame(inner_frame, bg=ColorConfig.current.FRAME_BG)
        btn_frame.pack(pady=(0, 10))

        def on_yes():
            result[0] = True
            dialog.destroy()

        def on_no():
            result[0] = False
            dialog.destroy()

        def on_cancel():
            result[0] = None
            dialog.destroy()

        yes_btn = tk.Button(
            btn_frame, text="Yes", width=8,
            bg=ColorConfig.current.BUTTON_BG,
            fg=ColorConfig.current.BUTTON_TEXT,
            activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
            activeforeground=ColorConfig.current.BUTTON_ACTIVE_TEXT,
            command=on_yes
        )
        yes_btn.pack(side=tk.LEFT, padx=8)

        no_btn = tk.Button(
            btn_frame, text="No", width=8,
            bg=ColorConfig.current.BUTTON_BG,
            fg=ColorConfig.current.BUTTON_TEXT,
            activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
            activeforeground=ColorConfig.current.BUTTON_ACTIVE_TEXT,
            command=on_no
        )
        no_btn.pack(side=tk.LEFT, padx=8)

        cancel_btn = tk.Button(
            btn_frame, text="Cancel", width=8,
            bg=ColorConfig.current.BUTTON_BG,
            fg=ColorConfig.current.BUTTON_TEXT,
            activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
            activeforeground=ColorConfig.current.BUTTON_ACTIVE_TEXT,
            command=on_cancel
        )
        cancel_btn.pack(side=tk.LEFT, padx=8)

        dialog.protocol("WM_DELETE_WINDOW", on_cancel)

        dialog.wait_window()
        return result[0]

    def on_close(self):
        if self.unsaved_changes:
            response = self._custom_askyesno("", "You have unsaved changes. Would you like to save before exiting?")
            if response is None:
                # Cancel pressed, abort close
                return
            if response:
                self.save_network_state()  # This should prompt the user to save the file
        self.save_window_geometry()
        self.root.destroy()

    def save_window_geometry(self):
        geometry = self.root.geometry()
        state = {}
        # Update only the relevant setting and preserve others
        write_NodeSailor_settings({'WINDOW_GEOMETRY': geometry})


    def load_window_geometry(self):
        try:
            with open(NodeSailor_settings_PATH, "r") as f:
                for line in f:
                    if line.startswith("WINDOW_GEOMETRY:"):
                        geometry = line.strip().split(":", 1)[1]
                        self.root.geometry(geometry)
        except Exception:
            # Fallback: do not set geometry if file is missing/unreadable
            pass

    def create_popup(self, title, width, height, on_close=None, grab=False):
        win = tk.Toplevel(self.root)
        win.overrideredirect(True)
        win.transient(self.root)
        win.resizable(True, True)
        win.minsize(300, 100)

        if grab:
            try: win.grab_set()
            except: pass

        def real_close():
            if grab:
                try: win.grab_release()
                except: pass
            win.destroy()

        wrapper = self.add_custom_titlebar(win, title, on_close or real_close)
        content = tk.Frame(wrapper, bg=ColorConfig.current.FRAME_BG)
        content.pack(fill=tk.BOTH, expand=True)
        content.columnconfigure(0, weight=0)
        content.columnconfigure(1, weight=1)

        # Center the popup relative to the main window
        self.center_window_on_screen(win)

        # --- BEGIN: Global Shortcut Bindings for Popups ---
        def bind_global_shortcuts(window):
            # F1 Help
            window.bind('<F1>', self.show_help)
            # Ctrl+Shift+C Color Mode
            window.bind('<Control-Shift-C>', lambda event: [self.root.focus_set(), self.toggle_theme()])
        bind_global_shortcuts(win)
        # --- END: Global Shortcut Bindings for Popups ---

        def apply_geometry():
            # Explicitly set window size first
            win.geometry(f"{width}x{height}")
            self.center_window_on_screen(win)
            win.focus_set()
            win.lift()

        win.after(1, apply_geometry)

        return win, content


    def make_popup_closer(self, attr):
        def closer():
            win = getattr(self, attr, None)
            if win and win.winfo_exists():
                win.destroy()
            setattr(self, attr, None)
            self.regain_focus()
        return closer

    #Fixes window geometry issues for vlan, Node List, Connections List and manage custom commands windows         
    def fix_window_geometry(self, window, width, height):
        window.update_idletasks()  # Make sure widget sizes are calculated
        window.geometry(f"{width}x{height}")
        self.center_window_on_screen(window)
        window.transient(self.root)
        window.lift()
        
    def open_group_editor(self, group=None):
        """Open the group editor window"""
        from group_editor import open_group_editor
        open_group_editor(self, group, color_presets=getattr(self.group_manager, "color_presets", None))

    def save_colors(self):
        colors = {
            'Light': {attr: getattr(ColorConfig.Light, attr) for attr in dir(ColorConfig.Light) if not attr.startswith('__') and attr != 'current'},
            'Dark': {attr: getattr(ColorConfig.Dark, attr) for attr in dir(ColorConfig.Dark) if not attr.startswith('__') and attr != 'current'}
        }
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(colors, f, indent=4)

    def load_colors(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'r') as f:
                colors = json.load(f)
                for attr, value in colors['Light'].items():
                    setattr(ColorConfig.Light, attr, value)
                for attr, value in colors['Dark'].items():
                    setattr(ColorConfig.Dark, attr, value)
            self.update_ui_colors()

    def load_custom_commands(self):
        try:
            with open(get_resource_path('data/custom_commands.json'), 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_custom_commands(self):
        with open(get_resource_path('data/custom_commands.json'), 'w') as f:
            json.dump(self.custom_commands, f, indent=4)