import tkinter as tk
from tkinter import simpledialog, messagebox, font, filedialog, colorchooser
import subprocess
from threading import Thread
import json
import platform
from PIL import Image, ImageTk
import socket
import os
import webbrowser
import ctypes

def get_ip_addresses():
    ip_addresses = []
    hostname = socket.gethostname()
    try:
        ip_address = socket.gethostbyname(hostname)
        ip_addresses.append(ip_address)
    except socket.gaierror:
        pass
    return ip_addresses

#testing nightmode colours

class ColorConfig:
    class Light:
        FRAME_BG = '#ffffff'
        BUTTON_FG = '#000000'
        NODE_DEFAULT = 'light steel blue'
        NODE_GREYED_OUT = 'gainsboro'
        NODE_HIGHLIGHT = 'gold'
        NODE_HOST = 'turquoise'
        NODE_OUTLINE_DEFAULT = 'black'
        NODE_PING_SUCCESS = 'green'
        NODE_PING_PARTIAL_SUCCESS = 'yellow'
        NODE_PING_FAILURE = 'red'
        FRAME_BG = 'white'
        STICKY_NOTE_BG = 'white'
        STICKY_NOTE_TEXT = 'black'
        BUTTON_BG = 'white'
        BUTTON_FG = 'black'
        BUTTON_ACTIVE_BG = '#e0e0e0'
        BUTTON_ACTIVE_FG = '#000000'
        BUTTON_CONFIGURATION_MODE = 'light coral'
        INFO_PANEL_BG = '#f7f7f7'
        INFO_PANEL_TEXT = 'black'
        Connections = 'dim gray'
        BORDER_COLOR = '#f7f7f7'
        TITLE_BAR_BG = '#f7f7f7'
        LEGEND_BG = '#d9d9d9'

    class Dark:
        FRAME_BG = '#2e2e2e'
        BUTTON_FG = '#ffffff'
        NODE_DEFAULT = '#4B5EAA'
        NODE_GREYED_OUT = '#4B5563'
        NODE_HIGHLIGHT = '#D97706'
        NODE_HOST = '#72741f'
        NODE_OUTLINE_DEFAULT = '#374151'
        NODE_PING_SUCCESS = '#047857'
        NODE_PING_PARTIAL_SUCCESS = '#B45309'
        NODE_PING_FAILURE = '#991B1B'
        FRAME_BG = '#1F2937'
        STICKY_NOTE_BG = '#303745'
        STICKY_NOTE_TEXT = '#000000'
        BUTTON_BG = '#4B5EAA'
        BUTTON_FG = 'black'
        BUTTON_ACTIVE_BG = '#111827'
        BUTTON_ACTIVE_FG = 'black'
        BUTTON_CONFIGURATION_MODE = '#F87171'
        INFO_PANEL_BG = '#111827'
        INFO_PANEL_TEXT = '#8f8f8f'
        Connections = '#6a7586'
        BORDER_COLOR = '#374151'
        TITLE_BAR_BG = '#1F2937'
        LEGEND_BG = '#1F2937'

    # Default to Dark mode
    current = Dark

class StickyNote:
    def __init__(self, canvas, text, x, y, gui=None,
                 font=('Helvetica', '12'), bg=ColorConfig.current.STICKY_NOTE_BG):
        self.canvas = canvas
        self.gui = gui  # May be None if older code doesn't pass the GUI
        self.text = text
        self.x = x
        self.y = y
        self.bg = bg
        self.font = font

        # Background rectangle
        self.bg_shape = canvas.create_rectangle(
            x, y, x + 100, y + 50,
            fill=ColorConfig.current.FRAME_BG, outline='',
            tags=("sticky_bg", f"bg_{id(self)}")  # consistent with "sticky_bg"
        )
        # Text
        self.note = canvas.create_text(
            x, y,
            text=text,
            font=self.font,
            fill=ColorConfig.current.STICKY_NOTE_TEXT,
            tags=("sticky_note",),
            anchor="nw"
        )

        # Left-click drag
        self.canvas.tag_bind(self.note, '<Button-1>', self.on_click)
        self.canvas.tag_bind(self.note, '<Shift-B1-Motion>', self.on_drag_notes)
        self.canvas.tag_bind(self.note, '<ButtonRelease-1>', self.on_release)

        # Right-click context menu
        self.canvas.tag_bind(self.note, '<Button-3>', self.show_context_menu)
        self.canvas.tag_bind(self.bg_shape, '<Button-3>', self.show_context_menu)

        self.adjust_note_size()
        self.type = 'sticky'

    def adjust_note_size(self):
        bbox = self.canvas.bbox(self.note)
        if bbox:
            padding = 2
            self.canvas.coords(self.bg_shape,
                bbox[0] - padding, bbox[1] - padding,
                bbox[2] + padding, bbox[3] + padding)
            self.canvas.itemconfig(self.bg_shape,
                fill=ColorConfig.current.STICKY_NOTE_BG)

    def on_click(self, event):
        self.canvas.selected_object_type = self.type
        self.canvas.selected_object = self
        self.last_drag_x = event.x
        self.last_drag_y = event.y

    def on_drag_notes(self, event):
        if event.state & 0x001:
            if self.canvas.selected_object is self:
                dx = event.x - self.last_drag_x
                dy = event.y - self.last_drag_y
                self.canvas.move(self.note, dx, dy)
                self.canvas.move(self.bg_shape, dx, dy)
                self.last_drag_x = event.x
                self.last_drag_y = event.y
                self.adjust_note_size()

    def on_release(self, event):
        self.canvas.selected_object_type = None
        self.canvas.selected_object = None

    # Right-click menu
    def show_context_menu(self, event):
        context_menu = tk.Toplevel(self.canvas)
        context_menu.wm_overrideredirect(True)
        context_menu.wm_geometry(f"+{event.x_root}+{event.y_root}")

        menu_frame = tk.Frame(context_menu, bg=ColorConfig.current.BUTTON_BG)
        menu_frame.pack()

        def destroy_menu():
            context_menu.unbind("<FocusOut>")
            context_menu.unbind("<Escape>")
            context_menu.destroy()

        options = [
            ("Edit Note Text", self.edit_sticky_text),
            ("Delete Note", self.delete_sticky)
        ]

        for txt, cmd in options:
            btn = tk.Button(
                menu_frame, text=txt,
                command=lambda c=cmd: [c(), destroy_menu()],
                bg=ColorConfig.current.BUTTON_BG,
                fg=ColorConfig.current.BUTTON_FG,
                activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
                activeforeground=ColorConfig.current.BUTTON_ACTIVE_FG,
                relief='flat', borderwidth=0, padx=10, pady=4, anchor='w',
                font=('Helvetica', 10)
            )
            btn.pack(fill='x')

        # Clicking elsewhere or pressing Escape closes the menu
        self.canvas.bind("<Button-1>", lambda e: destroy_menu(), add="+")
        context_menu.bind("<Escape>", lambda e: destroy_menu())

    def edit_sticky_text(self):
        new_text = simpledialog.askstring(
            "Edit Note",
            "Enter new note text:",
            initialvalue=self.text
        )
        if new_text is not None:
            self.text = new_text
            self.canvas.itemconfig(self.note, text=self.text)
            self.adjust_note_size()

    def delete_sticky(self):
        # If the GUI is available, call its remove_sticky. Otherwise, just delete ourselves.
        if self.gui and hasattr(self.gui, 'remove_sticky'):
            self.gui.remove_sticky(self)
        else:
            self.canvas.delete(self.note)
            self.canvas.delete(self.bg_shape)

class NetworkNode:
    def __init__(self, canvas, name, x, y, VLAN_100='', VLAN_200='', VLAN_300='', VLAN_400='', remote_desktop_address='', file_path='', web_config_url=''):
        self.canvas = canvas
        self.name = name
        self.VLAN_100 = VLAN_100
        self.VLAN_200 = VLAN_200
        self.VLAN_300 = VLAN_300
        self.VLAN_400 = VLAN_400
        self.remote_desktop_address = remote_desktop_address
        self.file_path = file_path
        self.web_config_url = web_config_url
        self.x = x
        self.y = y
        unique_node_tag = f"node_{id(self)}"
        self.font = font.Font(family="Helvetica", size=12) 
        self.shape = canvas.create_rectangle(
            x - 15, y - 15, x + 15, y + 15,
            fill=ColorConfig.current.NODE_DEFAULT, outline=ColorConfig.current.NODE_OUTLINE_DEFAULT, width=2,  # Adjust width for a bolder outline
            tags=unique_node_tag
        )
        self.text = canvas.create_text(
            x, y, text=name, font=self.font,  # Use Helvetica font
            tags=unique_node_tag
        )
        self.adjust_node_size()  # Adjust the node size initially
        self.canvas.tag_bind(self.shape, '<Button-1>', self.on_click)
        self.canvas.tag_bind(self.text, '<Button-1>', self.on_click)
        self.canvas.tag_bind(self.shape, '<Button-3>', self.show_context_menu)
        self.canvas.tag_bind(self.text, '<Button-3>', self.show_context_menu)
        self.connections = []
        self.raise_node()
        self.type = 'node'
        
    def update_position(self, x, y):
        self.x = x
        self.y = y
        self.canvas.coords(self.text, x, y)
        self.adjust_node_size()
        for line in self.connections:
            line.update_position()
        gui = getattr(self.canvas, "gui", None)
        if gui and hasattr(gui, "list_editor_xy_fields"):
            xy_fields = gui.list_editor_xy_fields.get(self)
            if xy_fields:
                x_entry, y_entry = xy_fields
                x_entry.delete(0, tk.END)
                x_entry.insert(0, str(self.x))
                y_entry.delete(0, tk.END)
                y_entry.insert(0, str(self.y))

    def update_info(self, name, VLAN_100='', VLAN_200='', VLAN_300='', VLAN_400='', remote_desktop_address='', file_path='', web_config_url=''):
        self.name = name
        self.VLAN_100 = VLAN_100
        self.VLAN_200 = VLAN_200
        self.VLAN_300 = VLAN_300
        self.VLAN_400 = VLAN_400
        self.remote_desktop_address = remote_desktop_address
        self.file_path = file_path
        self.web_config_url = web_config_url
        self.canvas.itemconfigure(self.text, text=name)
        self.adjust_node_size()  # Resize the node to fit the new text

    def raise_node(self):
        # Use tag_raise with the 'node' tag to bring the node to the front
        unique_node_tag = f"node_{id(self)}"
        self.canvas.itemconfig(self.shape, tags=unique_node_tag)
        self.canvas.itemconfig(self.text, tags=unique_node_tag)
        self.canvas.tag_raise(unique_node_tag)
        
    def on_click(self, event):
        # Set the selected node in the GUI
        gui.on_node_select(self)
        self.canvas.selected_object_type = self.type
        self.canvas.selected_object = self
        self.last_drag_x = event.x
        self.last_drag_y = event.y
        self.ping()
        
    def ping(self):
        def run_ping(ip):
            # Check for OS and construct the command accordingly
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            command = ['ping', param, '1', ip]
            response = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            # Analyze the output for success or failure indicators
            return 'TTL=' in response.stdout or 'ttl=' in response.stdout

        def update_ui(results):
            if self.canvas.winfo_exists():  # Check if canvas still exists
                if all(results):
                    color = ColorConfig.current.NODE_PING_SUCCESS
                elif any(results):
                    color = ColorConfig.current.NODE_PING_PARTIAL_SUCCESS
                else:
                    color = ColorConfig.current.NODE_PING_FAILURE
                self.canvas.itemconfig(self.shape, fill=color)
                self.canvas.after(0, lambda: gui.update_vlan_colors(self, results))

        def ping_all_vlans():
            vlan_ips = [self.VLAN_100, self.VLAN_200, self.VLAN_300, self.VLAN_400]
            ips_to_ping = [ip for ip in vlan_ips if ip]  # Filter out empty strings
            results = [run_ping(ip) for ip in ips_to_ping] if ips_to_ping else [False]
            self.canvas.after(0, update_ui, results)

        Thread(target=ping_all_vlans).start()

    def update_shape_color(self, color):
        self.canvas.itemconfig(self.shape, fill=color)

    def adjust_node_size(self):
        bbox = self.canvas.bbox(self.text)  # Get the bounding box of the text
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        pad = 10  # Padding around the text
        # Resize the rectangle based on the text size plus padding
        self.canvas.coords(self.shape, self.x - width/2 - pad, self.y - height/2 - pad, 
                           self.x + width/2 + pad, self.y + height/2 + pad)

    def show_context_menu(self, event):
        context_menu = tk.Toplevel(self.canvas)
        context_menu.wm_overrideredirect(True)  # Removes OS borders and title bar
        context_menu.wm_geometry(f"+{event.x_root}+{event.y_root}")

        # Frame for menu items (no border from OS)
        menu_frame = tk.Frame(context_menu, bg=ColorConfig.current.BUTTON_BG)
        menu_frame.pack()

        options = [
            ("Edit Node Information", self.edit_node_info),
            ("Open Remote Desktop", self.open_remote_desktop),
            ("Open File Explorer", self.open_file_explorer),
            ("Open Web Browser", self.open_web_browser),
            ("Delete Node", self.delete_node)
        ]

        # Add custom commands
        for name, cmd in gui.custom_commands.items():
            options.append((name, lambda c=cmd: self.execute_custom_command(c)))

        def destroy_menu():
            context_menu.unbind("<FocusOut>")
            context_menu.unbind("<Escape>")
            for btn in menu_frame.winfo_children():
                btn.unbind("<Enter>")
                btn.unbind("<Leave>")
            context_menu.destroy()

        for text, command in options:
            btn = tk.Button(menu_frame, text=text, command=lambda c=command: [c(), destroy_menu()],
                            bg=ColorConfig.current.BUTTON_BG, fg=ColorConfig.current.BUTTON_FG,
                            activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
                            activeforeground=ColorConfig.current.BUTTON_ACTIVE_FG,
                            relief='flat', borderwidth=0, padx=10, pady=4, anchor='w',
                            font=('Helvetica', 10))
            btn.pack(fill='x')
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=ColorConfig.current.BUTTON_ACTIVE_BG))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=ColorConfig.current.BUTTON_BG))

        self.canvas.bind("<Button-1>", lambda e: destroy_menu(), add="+")
        context_menu.bind("<Escape>", lambda e: destroy_menu())

    def edit_node_info(self):
        gui.open_node_window(node=self)

    def open_remote_desktop(self):
        if not self.remote_desktop_address:
            messagebox.showinfo("Info", "No remote desktop address set for this node.")
            return
        if platform.system() == "Windows":
            # Use the Windows Remote Desktop Connection command (mstsc)
            subprocess.Popen(f"mstsc /v:{self.remote_desktop_address}", shell=True)
        else:
            messagebox.showinfo("Info", "Remote desktop feature is not supported on this operating system.")

    def open_file_explorer(self):
        if not self.file_path:
            messagebox.showinfo("Info", "No file path set for this node.")
            return

        def try_open():
            try:
                os.startfile(self.file_path)
            except OSError as e:
                # Use after() to show the error in the main thread
                self.canvas.after(0, lambda: messagebox.showerror("Error", f"Failed to open '{self.file_path}': {str(e)}"))

        Thread(target=try_open, daemon=True).start()

    def open_web_browser(self):
        if not self.web_config_url:
            messagebox.showinfo("Info", "No web config URL set for this node.")
            return
        webbrowser.open(self.web_config_url, new=2)  # Open URL in a new tab, if exists
        pass
    
    def delete_node(self):
        gui.remove_node(self)

    def execute_custom_command(self, command_template):
        context = {
            'name': self.name,
            'ip': '',  # First valid IP will be assigned below
            'file': self.file_path or '',
            'web': self.web_config_url or '',
            'rdp': self.remote_desktop_address or '',
            'vlan100': self.VLAN_100 or '',
            'vlan200': self.VLAN_200 or '',
            'vlan300': self.VLAN_300 or '',
            'vlan400': self.VLAN_400 or ''
        }

        # Pick first available IP as the default {ip}
        for vlan in ['vlan100', 'vlan200', 'vlan300', 'vlan400']:
            if context[vlan]:
                context['ip'] = context[vlan]
                break

        try:
            command = command_template.format(**context)
            if platform.system() == "Windows":
                subprocess.Popen(f'start cmd /k "{command}"', shell=True)
            else:
                subprocess.Popen(['x-terminal-emulator', '-e', command])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to execute command: {str(e)}")


class ConnectionLine:
    def __init__(self, canvas, node1, node2, label=''):
        self.canvas = canvas
        self.node1 = node1
        self.node2 = node2
        self.line = canvas.create_line(node1.x, node1.y, node2.x, node2.y,width=2, fill=ColorConfig.current.Connections)
        self.label = label
        self.label_id = None
        if label:
            self.update_label()
        node1.connections.append(self)
        node2.connections.append(self)

    def update_position(self):
        self.canvas.coords(self.line, self.node1.x, self.node1.y, self.node2.x, self.node2.y)
        if self.label_id:
            self.update_label()  # Update label position
            
    def update_label(self):
        
        if self.label_id:
            self.canvas.delete(self.label_id)
            if hasattr(self, 'label_bg') and self.label_bg:
                self.canvas.delete(self.label_bg)

        # Calculate midpoint for the label
        mid_x = (self.node1.x + self.node2.x) / 2
        mid_y = (self.node1.y + self.node2.y) / 2

        # Create a text object similar to StickyNote
        self.label_id = self.canvas.create_text(mid_x, mid_y, text=self.label, font=('Helvetica', '12'), tags="connection_label", anchor="center")

        # Recreate a background similar to StickyNote
        bbox = self.canvas.bbox(self.label_id)
        if bbox:
            padding = 2
            self.label_bg = self.canvas.create_rectangle(bbox[0]-padding, bbox[1]-padding, bbox[2]+padding, bbox[3]+padding, fill=ColorConfig.current.STICKY_NOTE_BG, outline='')
            self.canvas.tag_lower(self.label_bg, self.label_id)  # Ensure the background is behind the text

    def set_label(self, label):
        self.label = label
        self.update_label()

class NetworkMapGUI:
    def __init__(self, root):
        self.root = root
        self.load_window_geometry()  # Load saved window size and position
        root.iconbitmap('_internal/favicon.ico')
        self.root.overrideredirect(True)
        self.root.configure(bg=ColorConfig.current.FRAME_BG)
        self.custom_font = font.Font(family="Helvetica", size=12)
        self.vlan_label_names = {
            'VLAN_100': 'VLAN_100',
            'VLAN_200': 'VLAN_200',
            'VLAN_300': 'VLAN_300',
            'VLAN_400': 'VLAN_400'
        }
        
        # Load custom commands
        self.custom_commands = self.load_custom_commands()
        
        # Make the window appear in the taskbar (Windows only)
        if platform.system() == "Windows":
            hwnd = self.root.winfo_id()
            # Get current extended style
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)  # GWL_EXSTYLE
            # Remove WS_EX_TOOLWINDOW (if present) and add WS_EX_APPWINDOW
            style &= ~0x00000080  # Remove WS_EX_TOOLWINDOW
            style |= 0x00040000   # Add WS_EX_APPWINDOW
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, style)
            
        # Resize Grip (bottom-right corner)
        self.resize_grip = tk.Frame(self.root, width=15, height=15, bg=ColorConfig.current.FRAME_BG, cursor='sizing')
        self.resize_grip.place(relx=1.0, rely=1.0, anchor='se', x=-2, y=-2)
        self.resize_grip.lift()
        self.resize_grip.bind("<ButtonPress-1>", self.start_resize)
        self.resize_grip.bind("<B1-Motion>", self.on_resize_grip_drag)
        self.resize_grip.bind("<ButtonRelease-1>", self.stop_resize)

        # Custom Title Bar
        self.title_bar = tk.Frame(self.root, bg=ColorConfig.current.FRAME_BG, relief='raised')
        self.title_bar.pack(side=tk.TOP, fill=tk.X)

        # Make the title bar draggable
        self.title_bar.bind("<ButtonPress-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)

        # Top-left resize grip (beside title)
        self.top_left_resize_grip = tk.Frame(self.title_bar, width=15, height=15, bg=ColorConfig.current.FRAME_BG, cursor='sizing')
        self.top_left_resize_grip.pack(side=tk.LEFT, padx=(2, 5))
        self.top_left_resize_grip.bind("<ButtonPress-1>", self.start_resize_top_left)
        self.top_left_resize_grip.bind("<B1-Motion>", self.on_resize_grip_drag_top_left)
        self.top_left_resize_grip.bind("<ButtonRelease-1>", self.stop_resize)

        self.title_label = tk.Label(self.title_bar, text="NodeSailor", bg=ColorConfig.current.FRAME_BG,
                                   fg=ColorConfig.current.BUTTON_FG, font=self.custom_font)
        self.title_label.pack(side=tk.LEFT, padx=10)
        # make the title label draggable
        self.title_label.bind("<ButtonPress-1>", self.start_move)
        self.title_label.bind("<B1-Motion>", self.do_move)

        self.close_button = tk.Button(self.title_bar, text='X', command=self.on_close,
                                     bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_FG,
                                     font=self.custom_font)
        self.close_button.pack(side=tk.RIGHT)
        
        # Maximize Button
        self.maximize_button = tk.Button(self.title_bar, text='[]', command=self.maximize_restore,
                                       bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_FG,
                                       font=self.custom_font)
        self.maximize_button.pack(side=tk.RIGHT)

        # Minimize Button
        self.minimize_button = tk.Button(self.title_bar, text='-', command=self.minimize_window,
                                        bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_FG,
                                        font=self.custom_font)
        self.minimize_button.pack(side=tk.RIGHT)
               
        self.is_maximized = False #track if maximized
        
        # Bind dragging events
        self.title_bar.bind('<Button-1>', self.start_move)
        self.title_bar.bind('<B1-Motion>', self.do_move)
        self.title_label.bind('<Button-1>', self.start_move)
        self.title_label.bind('<B1-Motion>', self.do_move)
        
        self.mode = "Configuration"
        self.selected_object_type = None
        self.connection_start_node = None
        self.legend_window = None
        self.unsaved_changes = False

        # Buttons Frame
        self.buttons_frame = tk.Frame(root)
        self.buttons_frame.pack(side=tk.TOP, fill=tk.X)
        self.buttons_frame.config(bg=ColorConfig.current.FRAME_BG)      
     
        # Update button styles
        button_style = {
            'font': self.custom_font,
            'bg': ColorConfig.current.BUTTON_BG,
            'fg': ColorConfig.current.BUTTON_FG,
            'activebackground': ColorConfig.current.BUTTON_ACTIVE_BG,
            'activeforeground': ColorConfig.current.BUTTON_ACTIVE_FG,
            'padx': 5,
            'pady': 2
        }

        start_menu_style = button_style.copy()  # Create a copy to avoid modifying the original
        start_menu_style['font'] = ("Helvetica", 12, "bold")  # Override font with bold version

        start_menu_button = tk.Button(self.buttons_frame, text="Start Menu", command=self.display_legend, **start_menu_style)
        start_menu_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.mode_button = tk.Button(self.buttons_frame, text='Configuration', command=self.toggle_mode, **button_style)
        self.mode_button.pack(side=tk.LEFT, padx=(5, 100), pady=5)        
        
        whoamI_button = tk.Button(self.buttons_frame, text='Who am I?', command=self.highlight_matching_nodes, **button_style)
        whoamI_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        clear_status_button = tk.Button(self.buttons_frame, text='Clear Status', command=self.clear_node_status, **button_style)
        clear_status_button.pack(side=tk.LEFT, padx=5, pady=5)

        ping_all_button = tk.Button(self.buttons_frame, text='Ping All', command=self.ping_all, **button_style)
        ping_all_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Checkboxes for VLANs
        self.vlan_visibility = {'VLAN_100': tk.BooleanVar(value=True),
                                'VLAN_200': tk.BooleanVar(value=True),
                                'VLAN_300': tk.BooleanVar(value=True),
                                'VLAN_400': tk.BooleanVar(value=True)}

        self.vlan_checkboxes = {}
        for vlan, var in self.vlan_visibility.items():
            cb = tk.Checkbutton(
                self.buttons_frame,
                text=self.vlan_label_names[vlan],
                variable=var,
                bg=ColorConfig.current.FRAME_BG,
                fg=ColorConfig.current.BUTTON_FG,
                selectcolor=ColorConfig.current.FRAME_BG,
                activebackground=ColorConfig.current.BUTTON_BG,
                activeforeground=ColorConfig.current.BUTTON_FG,
                command=self.update_vlan_visibility
            )
            cb.pack(side=tk.LEFT, padx=5)
            self.vlan_checkboxes[vlan] = cb

        # Zoom controls in bottom-left corner
        zoom_frame = tk.Frame(self.root, bg=ColorConfig.current.FRAME_BG, height=30)
        zoom_frame.place(relx=0.0, rely=1.0, anchor='sw', x=10, y=-5)
        self.zoom_frame = zoom_frame

        def make_zoom_button(text, command):
            return tk.Label(zoom_frame, text=text, font=("Helvetica", 12),
                            fg=ColorConfig.current.BUTTON_FG, bg=ColorConfig.current.FRAME_BG,
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
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=(5, 25))
        self.nodes = []
        self.stickynotes = []
        self.selected_node = None
        self.previous_selected_node = None
        
        self._pan_start_x = None
        self._pan_start_y = None

        self.root.bind_all('<F1>', self.show_help)
        root.bind('<Left>', lambda event: self.pan_canvas('left'))  # Pan left
        root.bind('<Right>', lambda event: self.pan_canvas('right'))  # Pan right
        root.bind('<Up>', lambda event: self.pan_canvas('up'))  # Pan up
        root.bind('<Down>', lambda event: self.pan_canvas('down'))  # Pan down
        self.root.bind('<Control-Shift-C>', lambda event: [self.root.focus_set(), self.toggle_theme()])
        self.canvas.bind('<Double-1>', self.create_node)
        self.canvas.bind('<B1-Motion>', self.move_node)
        self.canvas.bind('<ButtonRelease-1>', self.deselect_node)
        self.canvas.bind('<Shift-Double-1>', self.create_sticky_note)
        self.canvas.bind('<MouseWheel>', self.zoom_with_mouse)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind('<Button-2>', self.create_connection)
        self.canvas.bind('<Shift-Button-2>', self.remove_connection)
        self.canvas.bind('<ButtonPress-3>', self.start_pan)
        self.canvas.bind('<B3-Motion>', self.do_pan)
        self.root.bind('<Control-s>', self.keyboard_save)
        self.root.bind('<Control-l>', self.keyboard_load)
        self.zoom_level = 1.0
        self.root.focus_set()

         # Info Panel
        self.info_panel = tk.Frame(self.root, bg=ColorConfig.current.INFO_PANEL_BG)
        self.info_panel.place(relx=1.0, rely=0.05, anchor='ne')

        info_label_style = {'font': ('Helvetica', 10), 
                            'bg': ColorConfig.current.INFO_PANEL_BG, 
                            'fg': ColorConfig.current.INFO_PANEL_TEXT,
                            'anchor': 'w'}
        info_value_style = {'font': ('Helvetica', 10), 
                            'bg': ColorConfig.current.INFO_PANEL_BG, 
                            'fg': ColorConfig.current.INFO_PANEL_TEXT}

        tk.Label(self.info_panel, text="Name:", **info_label_style).grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.node_name_label = tk.Label(self.info_panel, text="-", **info_value_style)
        self.node_name_label.grid(row=0, column=1, sticky='w', padx=5, pady=2)

        tk.Label(self.info_panel, text="", **info_label_style).grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.node_ip_label = tk.Label(self.info_panel, text="", **info_value_style)
        self.node_ip_label.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        self.vlan_labels = {}
        self.vlan_title_labels = {}
        for i, vlan in enumerate(['VLAN_100', 'VLAN_200', 'VLAN_300', 'VLAN_400'], start=2):
            title = tk.Label(self.info_panel, text=self.vlan_label_names[vlan] + ":", **info_label_style)
            title.grid(row=i, column=0, sticky='w', padx=5, pady=2)
            self.vlan_title_labels[vlan] = title

            self.vlan_labels[vlan] = tk.Label(self.info_panel, text="-", **info_value_style)
            self.vlan_labels[vlan].grid(row=i, column=1, sticky='w', padx=5, pady=2)

        
        self.toggle_mode() # sets to Operator mode on startup
        self.hide_legend_on_start = tk.BooleanVar(value=False)
        self.load_legend_state()
        if self.hide_legend_on_start.get():
            self.load_last_file()  # Load the last file without displaying the legend
        else:
            self.display_legend()  # Display the legend window

        root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Reposition the resize grip (important for keeping it in the corner)
        self.resize_grip.place(relx=1.0, rely=1.0, anchor="se")

        self.update_ui_colors()

    def start_move_legend(self, event):
        self.legend_window._x = event.x
        self.legend_window._y = event.y

    def do_move_legend(self, event):
        deltax = event.x - self.legend_window._x
        deltay = event.y - self.legend_window._y
        x = self.legend_window.winfo_x() + deltax
        y = self.legend_window.winfo_y() + deltay
        self.legend_window.geometry(f"+{x}+{y}")

    def start_resize(self, event):
        self.start_x = event.x_root
        self.start_y = event.y_root
        self.initial_width = self.root.winfo_width()
        self.initial_height = self.root.winfo_height()

    def on_resize_grip_drag(self, event):
        delta_x = event.x_root - self.start_x
        delta_y = event.y_root - self.start_y
        new_width = self.initial_width + delta_x
        new_height = self.initial_height + delta_y
        self.root.geometry(f"{new_width}x{new_height}")

    def stop_resize(self, event):
        self.start_x = None
        self.start_y = None

    def start_resize_top_left(self, event):
        self.start_x = event.x_root
        self.start_y = event.y_root
        self.initial_width = self.root.winfo_width()
        self.initial_height = self.root.winfo_height()
        self.initial_x = self.root.winfo_x()
        self.initial_y = self.root.winfo_y()

    def on_resize_grip_drag_top_left(self, event):
        delta_x = event.x_root - self.start_x
        delta_y = event.y_root - self.start_y
        new_width = max(self.initial_width - delta_x, 100)
        new_height = max(self.initial_height - delta_y, 100)
        new_x = self.initial_x + delta_x
        new_y = self.initial_y + delta_y
        self.root.geometry(f"{new_width}x{new_height}+{new_x}+{new_y}")

    def minimize_window(self):
        self.root.state('iconic')

    def maximize_restore(self):
        if self.is_maximized:
            self.root.state('normal')
            self.is_maximized = False
            self.maximize_button.config(text='[]')
        else:
            self.root.state('zoomed')
            self.is_maximized = True
            self.maximize_button.config(text='[ ]')

    def start_move(self, event):
        """Capture the initial mouse position for dragging."""
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        """Move the window based on mouse movement."""
        if not self.is_maximized:
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.root.winfo_x() + deltax
            y = self.root.winfo_y() + deltay
            self.root.geometry(f"+{x}+{y}")

    def show_color_editor(self):
        """Open a window to edit ColorConfig attributes."""
        editor_window = tk.Toplevel(self.root)
        editor_window.title("Color Scheme Editor")
        editor_window.geometry("400x600")
        editor_window.transient(self.root)  # Tie it to the main window
        editor_window.grab_set()  # Make it modal

        # Theme selection
        theme_var = tk.StringVar(value="Dark")  # Default to Dark
        tk.Label(editor_window, text="Select Theme:").pack(pady=5)
        tk.Button(editor_window, text="Load Colors", command=self.load_colors).pack(pady=5)
        tk.Button(editor_window, text="Save Colors", command=self.save_colors).pack(pady=5)
        tk.Radiobutton(editor_window, text="Light", variable=theme_var, value="Light").pack()
        tk.Radiobutton(editor_window, text="Dark", variable=theme_var, value="Dark").pack()

        # Frame for color entries
        color_frame = tk.Frame(editor_window)
        color_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # List of ColorConfig attributes (excluding 'current')
        color_attrs = [attr for attr in dir(ColorConfig.Light) if not attr.startswith('__') and attr != 'current']
        color_entries = {}

        def update_color(attr):
            """Open color chooser and update the button's background."""
            theme = theme_var.get()
            current_color = getattr(getattr(ColorConfig, theme), attr)
            new_color = colorchooser.askcolor(title=f"Choose {attr} for {theme}", initialcolor=current_color)
            if new_color[1]:  # If a color was selected (not canceled)
                setattr(getattr(ColorConfig, theme), attr, new_color[1])  # Update ColorConfig
                color_entries[attr]['button'].config(bg=new_color[1])  # Update button color
                self.update_ui_colors()  # Apply changes live

        # Populate the frame with color options
        for i, attr in enumerate(color_attrs):
            tk.Label(color_frame, text=f"{attr}:").grid(row=i, column=0, sticky="w", pady=2)
            current_color = getattr(getattr(ColorConfig, theme_var.get()), attr)
            btn = tk.Button(color_frame, text="Pick Color", bg=current_color,
                            command=lambda a=attr: update_color(a))
            btn.grid(row=i, column=1, sticky="ew", pady=2)
            color_entries[attr] = {'button': btn}

        # Update colors when theme changes
        def on_theme_change(*args):
            theme = theme_var.get()
            for attr in color_attrs:
                current_color = getattr(getattr(ColorConfig, theme), attr)
                color_entries[attr]['button'].config(bg=current_color)

        theme_var.trace("w", on_theme_change)

        # Close button
        tk.Button(editor_window, text="Close", command=editor_window.destroy).pack(pady=10)

    def edit_vlan_labels(self):
        label_window = tk.Toplevel(self.root)
        label_window.title("Edit VLAN Labels")
        label_window.geometry("300x250")
        entries = {}

        for i, vlan in enumerate(self.vlan_label_names.keys()):
            tk.Label(label_window, text=vlan + ":").grid(row=i, column=0, padx=10, pady=5)
            entry = tk.Entry(label_window)
            entry.insert(0, self.vlan_label_names[vlan])
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries[vlan] = entry

        def save_labels():
            for vlan, entry in entries.items():
                self.vlan_label_names[vlan] = entry.get()
            for vlan, label in self.vlan_title_labels.items():
                label.config(text=self.vlan_label_names[vlan] + ":")
            for vlan, cb in self.vlan_checkboxes.items():
                cb.config(text=self.vlan_label_names[vlan])
            label_window.destroy()

        tk.Button(label_window, text="Save", command=save_labels).grid(row=5, column=0, columnspan=2, pady=10)

    def show_help(self, event=None):
        help_window = tk.Toplevel(self.root)
        help_window.title("Help - Keyboard Shortcuts and Functions")
        help_window.geometry("1000x800")
        help_window.overrideredirect(True)
        help_window.transient(self.root)

        # Outer frame for border
        outer_frame = tk.Frame(help_window, bg=ColorConfig.current.BORDER_COLOR, padx=2, pady=2)
        outer_frame.pack(fill=tk.BOTH, expand=True)

        # Title bar
        title_bar = tk.Frame(outer_frame, bg=ColorConfig.current.LEGEND_BG)
        title_bar.pack(side=tk.TOP, fill=tk.X)

        title_label = tk.Label(title_bar, text="Help - Keyboard Shortcuts and Functions",
                            bg=ColorConfig.current.LEGEND_BG, fg=ColorConfig.current.BUTTON_FG,
                            font=self.custom_font)
        title_label.pack(side=tk.LEFT, padx=10)

        close_button = tk.Button(title_bar, text='X', 
                                command=lambda: [help_window.destroy(), self.root.focus_force(), self.root.lift()],
                                bg=ColorConfig.current.LEGEND_BG, fg=ColorConfig.current.BUTTON_FG,
                                font=self.custom_font)
        close_button.pack(side=tk.RIGHT)

        # Make the title bar draggable (like legend)
        title_bar.bind("<ButtonPress-1>", self.start_move_legend)  # Reusing legend's move method
        title_bar.bind("<B1-Motion>", self.do_move_legend)
        title_label.bind("<ButtonPress-1>", self.start_move_legend)
        title_label.bind("<B1-Motion>", self.do_move_legend)
        help_window.bind('<Escape>', lambda e: help_window.destroy())

        # Content frame
        content_frame = tk.Frame(outer_frame, bg=ColorConfig.current.LEGEND_BG)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Text area
        text_area = tk.Text(content_frame, wrap="word", font="Helvetica 10",
                            bg=ColorConfig.current.LEGEND_BG, fg=ColorConfig.current.BUTTON_FG,
                            state="disabled")
        text_area.pack(expand=True, fill="both", padx=10, pady=10)

        help_text = """
        NodeSailor v0.9.10 - Help

        Overview:
        NodeSailor is a network visualization tool.

        User Modes:
        - Operator: Monitor and interact with the network.
        - Configuration: Build and edit the network layout.

        Operator Mode:
        - Left Click on Node: Ping the node (Green = all VLANs up, Yellow = partial, Red = none).
        - Right Click on Node: Open context menu (Edit Node, Remote Desktop, File Explorer, Web Browser, Delete).
        - 'Who am I?': Highlight nodes matching the user machine's IP addresses.
        - 'Ping All': Ping all nodes and update their status.
        - 'Clear Status': Reset all node colors to default.

        Configuration Mode:
        - Double Left Click: Create a new node.
        - Shift + Double Left Click: Add a sticky note.
        - Middle Click on Node: Start/end a connection line between nodes (prompts for a label).
        - Shift + Middle Click on Line: Remove a connection.
        - Left Click + Drag: Move nodes or sticky notes (Shift + Drag for sticky notes).
        - Right Click on Node: Open context menu for editing or deletion.

        Node Context Menu:
        - Edit Node Information: Modify name, VLAN IPs, remote desktop, file path, or web URL.
        - Open Remote Desktop: Launch RDP (Windows only) using the node's address.
        - Open File Explorer: Open the specified file path.
        - Open Web Browser: Open the node's web config URL.
        - Delete Node: Remove the node and its connections (Configuration mode only).
        - Custom Commands: User-defined commands that can be executed on the node's IP address.

        VLAN Checkboxes:
        - Toggle visibility of nodes based on VLANs (checked = visible, unchecked = greyed out).

        Custom Commands:
        - Access through 'Manage Custom Commands' in the Start Menu
        - Use {ip} as a placeholder for the node's IP address in command templates
        - Commands appear in the node's context menu
        - Example: ping {ip} -t will ping the node's IP address until the user stops it
        """

        text_area.config(state="normal")
        text_area.insert("1.0", help_text)
        text_area.tag_add("bold", "1.0", "4.end")
        text_area.tag_add("bold", "7.0", "7.end")
        text_area.tag_add("bold", "11.0", "11.end")
        text_area.tag_add("bold", "18.0", "18.end")
        text_area.tag_add("bold", "26.0", "26.end")
        text_area.tag_add("bold", "33.0", "33.end")
        text_area.tag_config("bold", font="Helvetica 10 bold")
        text_area.config(state="disabled")

        # Center the window (reuse existing method)
        help_window.lift()        # Bring to front
        help_window.focus_set()   # Set focus
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
            
        else:
            self.mode = "Operator"
            self.mode_button.config(text='Operator Mode', bg=ColorConfig.current.BUTTON_BG)
            # Disable functionalities for Operator mode
            self.canvas.unbind('<Double-1>')
            self.canvas.unbind('<B1-Motion>')
            self.canvas.unbind('<Shift-Double-1>')
            self.canvas.unbind('<Button-2>')
  
    def zoom_with_mouse(self, event):
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

        self.zoom_level *= factor
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.update_zoom_label()
    def zoom_in(self, event=None):
        self.apply_zoom(1.1)
        self.update_zoom_label()

    def zoom_out(self, event=None):
        self.apply_zoom(0.9)
        self.update_zoom_label()

    def reset_zoom(self, event=None):
        if self.zoom_level != 1.0:
            self.apply_zoom(1 / self.zoom_level)
            self.update_zoom_label()

    def apply_zoom(self, factor):
        # Scale all canvas items visually
        self.canvas.scale("all", 0, 0, factor, factor)
        self.update_zoom_label()
        
        # Update stored node coordinates
        for node in self.nodes:
            node.x *= factor
            node.y *= factor
            node.update_position(node.x, node.y)

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
            should_be_visible = any(self.vlan_visibility[vlan].get() for vlan in ['VLAN_100', 'VLAN_200', 'VLAN_300', 'VLAN_400'] if getattr(node, vlan))
            node_color = ColorConfig.current.NODE_DEFAULT if should_be_visible else ColorConfig.current.NODE_GREYED_OUT
            self.canvas.itemconfigure(node.shape, fill=node_color)

    def update_vlan_colors(self, node, ping_results):
        for i, vlan in enumerate(['VLAN_100', 'VLAN_200', 'VLAN_300', 'VLAN_400']):
            if getattr(node, vlan):
                color = ColorConfig.current.NODE_PING_SUCCESS if ping_results[i] else ColorConfig.current.NODE_PING_FAILURE
                self.vlan_labels[vlan].config(bg=color)
            else:
                self.vlan_labels[vlan].config(bg=ColorConfig.current.INFO_PANEL_BG)


    def display_legend(self):
        # Check if the legend window exists and is valid
        if self.legend_window is not None and self.legend_window.winfo_exists():
            self.legend_window.deiconify()  # Restore if minimized
            self.legend_window.lift()       # Bring to front
            self.legend_window.grab_set()   # Ensure it has the grab
        else:
            self.legend_window = tk.Toplevel(self.root)
            self.legend_window.overrideredirect(True)
            self.legend_window.transient(self.root)
            self.legend_window.transient(self.root)
            
            # Outer frame acts as the border
            outer_frame = tk.Frame(self.legend_window, bg=ColorConfig.current.BORDER_COLOR, padx=2, pady=2)
            outer_frame.pack(fill=tk.BOTH, expand=True)
            
            # Title bar
            title_bar = tk.Frame(outer_frame, bg=ColorConfig.current.LEGEND_BG)
            title_bar.pack(side=tk.TOP, fill=tk.X)

            title_label = tk.Label(title_bar, text="Nodesailor v0.9.10", bg=ColorConfig.current.LEGEND_BG,
                                fg=ColorConfig.current.BUTTON_FG, font=self.custom_font)
            title_label.pack(side=tk.LEFT, padx=10)

            close_button = tk.Button(title_bar, text='X', command=self.close_legend,
                                    bg=ColorConfig.current.LEGEND_BG, fg=ColorConfig.current.BUTTON_FG,
                                    font=self.custom_font)
            close_button.pack(side=tk.RIGHT)

            # Make the title bar draggable
            title_bar.bind("<ButtonPress-1>", self.start_move_legend)
            title_bar.bind("<B1-Motion>", self.do_move_legend)
            title_label.bind("<ButtonPress-1>", self.start_move_legend)
            title_label.bind("<B1-Motion>", self.do_move_legend)
            self.legend_window.bind("<Escape>", lambda e: self.close_legend())

            # Content frame
            content_frame = tk.Frame(outer_frame, bg=ColorConfig.current.LEGEND_BG)
            content_frame.pack(fill=tk.BOTH, expand=True)

            # Image
            img = Image.open("_internal/legend.png").resize((404, 400), Image.Resampling.LANCZOS)
            photo_img = ImageTk.PhotoImage(img)
            img_label = tk.Label(content_frame, image=photo_img, bg=ColorConfig.current.LEGEND_BG)
            img_label.image = photo_img  # Keep a reference to avoid garbage collection
            img_label.pack(pady=5)

            # Button styles
            button_style = {
                'font': self.custom_font,
                'bg': ColorConfig.current.BUTTON_BG,
                'fg': ColorConfig.current.BUTTON_FG,
                'activebackground': ColorConfig.current.BUTTON_ACTIVE_BG,
                'activeforeground': ColorConfig.current.BUTTON_ACTIVE_FG,
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

            color_editor_button = tk.Button(content_frame, text='Edit Colors',
                                            command=self.show_color_editor, **button_style)
            color_editor_button.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

            edit_labels_btn = tk.Button(content_frame, text='Edit VLAN Labels',
                             command=self.edit_vlan_labels, **button_style)
            edit_labels_btn.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            
            node_list_btn = tk.Button(content_frame, text='List View (Table Editor)',
                            command=self.open_node_list_editor, **button_style)
            node_list_btn.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            
            custom_cmd_btn = tk.Button(content_frame, text='Manage Custom Commands',
                                     command=self.manage_custom_commands, **button_style)
            custom_cmd_btn.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

            help_button = tk.Button(content_frame, text='Help', command=self.show_help, **button_style)
            help_button.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

            close_btn = tk.Button(content_frame, text='Close', command=self.close_legend, **button_style)
            close_btn.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

            # Checkbox
            self.hide_legend_checkbox = tk.Checkbutton(
                content_frame,
                text="Hide this window on next startup and load most recent on next startup",
                variable=self.hide_legend_on_start,
                command=self.save_legend_state,
                bg=ColorConfig.current.LEGEND_BG,
                fg=ColorConfig.current.BUTTON_FG,
                selectcolor=ColorConfig.current.LEGEND_BG,
                activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
                activeforeground=ColorConfig.current.BUTTON_ACTIVE_FG
            )
            self.hide_legend_checkbox.pack(pady=5)

            self.legend_window.lift()
            self.legend_window.focus_set()
            self.center_window_on_screen(self.legend_window)

    # This callback closes the legend window
    def close_legend(self):
        if self.legend_window and self.legend_window.winfo_exists():
            self.legend_window.destroy()
            self.legend_window = None
        self.root.focus_force()  # Stronger focus restoration
        self.root.lift()  # Bring window to the foreground

    def save_legend_state(self):
        state = {}
        try:
            with open("_internal/legend_state.txt", "r") as f:
                for line in f:
                    if ':' in line:
                        key, value = line.strip().split(':', 1)
                        state[key] = value
        except FileNotFoundError:
            pass

        state['HIDE_LEGEND'] = str(self.hide_legend_on_start.get())
        
        try:
            with open("_internal/legend_state.txt", "w") as f:
                for key, value in state.items():
                    f.write(f"{key}:{value}\n")
        except Exception as e:
            print(f"Error writing legend state: {e}")

    def load_legend_state(self):
        try:
            with open("_internal/legend_state.txt", "r") as f:
                for line in f:
                    if line.startswith("HIDE_LEGEND:"):
                        value = line.strip().split(":", 1)[1].lower()
                        self.hide_legend_on_start.set(value == 'true')
        except FileNotFoundError:
            pass
        
    def center_window_on_screen(self, window):
        window.update_idletasks()  # Ensure all widgets are rendered
        # Use requested width/height since actual size might not be set yet
        width = window.winfo_reqwidth()
        height = window.winfo_reqheight()
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
       
    def on_node_select(self, node):
        # Reset the previous selected node's appearance
        if self.previous_selected_node:
            self.canvas.itemconfig(self.previous_selected_node.shape, outline=ColorConfig.current.NODE_OUTLINE_DEFAULT, width=2)

        # Update the appearance of the current selected node
        self.canvas.itemconfig(node.shape, outline=ColorConfig.current.NODE_HIGHLIGHT, width=4)  # orange outline with a width of 4

        # Reset VLAN label colors immediately when a new node is selected
        for vlan in ['VLAN_100', 'VLAN_200', 'VLAN_300', 'VLAN_400']:
            self.vlan_labels[vlan].config(bg=ColorConfig.current.INFO_PANEL_BG)

        # Update the information panel
        self.node_name_label.config(text=node.name)
        
        # Update the selected and previous selected nodes
        self.previous_selected_node = node
        self.selected_node = node

        # Update the VLAN information
        for vlan_key in ['VLAN_100', 'VLAN_200', 'VLAN_300', 'VLAN_400']:
            vlan_value = getattr(node, vlan_key, "-")
            self.vlan_labels[vlan_key].config(text=vlan_value)

    def open_node_window(self, node=None, event=None):
        window = tk.Toplevel(self.canvas)
        window.title("Edit Node" if node else "Create Node")
        window.geometry("300x380")

        # Entry for Node Name
        tk.Label(window, text="Node Name:").grid(row=0, column=0, padx=10, pady=10)
        name_entry = tk.Entry(window)
        name_entry.grid(row=0, column=1, padx=10, pady=10)
        if node: 
            name_entry.insert(0, node.name)

        # Entries for VLAN IP Addresses
        VLAN_entries = {}
        for i, vlan in enumerate(["VLAN_100", "VLAN_200", "VLAN_300", "VLAN_400"], start=1):
            tk.Label(window, text=f"{vlan}:").grid(row=i, column=0, padx=10, pady=10)
            VLAN_entry = tk.Entry(window)
            VLAN_entry.grid(row=i, column=1, padx=10, pady=10)
            if node:
                VLAN_entry.insert(0, getattr(node, vlan))
            VLAN_entries[vlan] = VLAN_entry

        # Entry for Remote Desktop Address
        tk.Label(window, text="Remote Desktop Address:").grid(row=5, column=0, padx=10, pady=10)
        remote_desktop_entry = tk.Entry(window)
        remote_desktop_entry.grid(row=5, column=1, padx=10, pady=10)
        if node:
            remote_desktop_entry.insert(0, node.remote_desktop_address)

        # Entry for File Path
        tk.Label(window, text="File Path:").grid(row=6, column=0, padx=10, pady=10)
        file_path_entry = tk.Entry(window)
        file_path_entry.grid(row=6, column=1, padx=10, pady=10)
        if node:
            file_path_entry.insert(0, node.file_path)

        # Entry for Web Config URL
        tk.Label(window, text="Web Config URL:").grid(row=7, column=0, padx=10, pady=10)
        web_config_url_entry = tk.Entry(window)
        web_config_url_entry.grid(row=7, column=1, padx=10, pady=10)
        if node:
            web_config_url_entry.insert(0, node.web_config_url)

        def save_node():
            name = name_entry.get()
            vlan_ips = {vlan: VLAN_entries[vlan].get() for vlan in VLAN_entries}
            remote_desktop_address = remote_desktop_entry.get()
            file_path = file_path_entry.get()
            web_config_url = web_config_url_entry.get()
            if node:
                node.update_info(name, **vlan_ips, remote_desktop_address=remote_desktop_address, file_path=file_path, web_config_url=web_config_url)
                self.on_node_select(node)  # Update selected node info
            else:
                if name:
                    new_node = NetworkNode(self.canvas, name, event.x, event.y, **vlan_ips, remote_desktop_address=remote_desktop_address, file_path=file_path, web_config_url=web_config_url)
                    self.nodes.append(new_node)
                    self.on_node_select(new_node)
            window.destroy()

        save_button = tk.Button(window, text="Save", command=save_node)
        save_button.grid(row=8, column=0, columnspan=2, pady=10)

    def create_node(self, event):
        self.open_node_window(event=event)
        self.unsaved_changes = True
             
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
            # Remove all connections related to the node
            for connection in node.connections[:]:
                self.canvas.delete(connection.line)
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
            messagebox.showinfo('Remove Node', 'Switch to Configuration mode to delete nodes.')
        
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
            
    def clear_node_status(self):
        # Set the node color of all nodes to NODE_DEFAULT.
        for node in self.nodes:
            self.canvas.itemconfig(node.shape, fill=ColorConfig.current.NODE_DEFAULT)
 
    def ping_all(self):
        for node in self.nodes:
            node.ping()
    
    def create_sticky_note(self, event=None):
        if self.mode == "Configuration":
            text = simpledialog.askstring('Sticky Note', 'Enter note text:', parent=self.root)
            if text:
                x, y = event.x, event.y if event else (50, 50)
                note = StickyNote(self.canvas, text, x, y, self)
                self.stickynotes.append(note)
                self.unsaved_changes = True

    def remove_sticky(self, sticky):
        # Erase sticky from the canvas
        self.canvas.delete(sticky.note)
        self.canvas.delete(sticky.bg_shape)

        # Remove it from the list
        if sticky in self.stickynotes:
            self.stickynotes.remove(sticky)     

    def create_connection(self, event):     # Draw a connection line
        if self.mode == "Configuration":
            clicked_items = self.canvas.find_withtag("current")
            if clicked_items:
                clicked_item_id = clicked_items[0]  # Get the first item's ID from the tuple
                for node in self.nodes:
                    if clicked_item_id in (node.shape, node.text):
                        if self.connection_start_node is None:
                            self.connection_start_node = node
                            return  # Return after setting the start node
                        elif self.connection_start_node != node:
                            label = simpledialog.askstring("Label", "Enter label for connection:", parent=self.root)
                            connection = ConnectionLine(self.canvas, self.connection_start_node, node, label=label)
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
            'stickynotes': []
        }

        # Gather node data
        for node in self.nodes:
            node_data = {
                'name': node.name,
                'VLAN_100': node.VLAN_100,
                'VLAN_200': node.VLAN_200,
                'VLAN_300': node.VLAN_300,
                'VLAN_400': node.VLAN_400,
                'x': node.x,
                'y': node.y,
                'remote_desktop_address': node.remote_desktop_address,
                'file_path': node.file_path,
                'web_config_url': node.web_config_url
            }
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

        # Prompt user for a file location and save the JSON file
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(state, f, indent=4)

        # Close the legend window if it exists
        if self.legend_window and self.legend_window.winfo_exists():
            self.legend_window.destroy()


    def new_network_state(self):
        # Confirm with the user before clearing the network state
        response = messagebox.askyesno("New Network State", "Are you sure you want to create a new network state? This will clear all current loaded data.")
        if response:
            self.clear_current_loaded()  # Clear existing nodes and connections
            self.clear_node_status()  # Reset the status of all nodes
            self.legend_window.destroy()  # Close the legend window

    def load_network_state_from_path(self, file_path):
        with open(file_path, 'r') as f:
            self.clear_current_loaded()  # Clears existing nodes, connections, and stickynotes
            state = json.load(f)

            # Load custom VLAN labels (if present)
            if 'vlan_labels' in state:
                self.vlan_label_names.update(state['vlan_labels'])
                for vlan, label in self.vlan_title_labels.items():
                    label.config(text=self.vlan_label_names[vlan] + ":")
                for vlan, cb in self.vlan_checkboxes.items():
                    cb.config(text=self.vlan_label_names[vlan])

            # Load nodes
            for node_data in state.get('nodes', []):
                node = NetworkNode(
                    self.canvas,
                    node_data['name'],
                    node_data['x'],
                    node_data['y'],
                    VLAN_100=node_data.get('VLAN_100', ''),
                    VLAN_200=node_data.get('VLAN_200', ''),
                    VLAN_300=node_data.get('VLAN_300', ''),
                    VLAN_400=node_data.get('VLAN_400', ''),
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
                ConnectionLine(self.canvas, node1, node2, label=label)

            # Load sticky notes
            self.stickynotes.clear()
            for sn in state.get('stickynotes', []):
                note = StickyNote(self.canvas, sn['text'], sn['x'], sn['y'])
                self.stickynotes.append(note)

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
                if 'vlan_labels' in state:
                    self.vlan_label_names.update(state['vlan_labels'])
                    for vlan, label in self.vlan_title_labels.items():
                        label.config(text=self.vlan_label_names[vlan] + ":")
                    for vlan, cb in self.vlan_checkboxes.items():
                        cb.config(text=self.vlan_label_names[vlan])
                # Load nodes
                for node_data in state['nodes']:
                    node = NetworkNode(
                        self.canvas, 
                        node_data['name'], 
                        node_data['x'], 
                        node_data['y'],
                        VLAN_100=node_data.get('VLAN_100', ''),
                        VLAN_200=node_data.get('VLAN_200', ''),
                        VLAN_300=node_data.get('VLAN_300', ''),
                        VLAN_400=node_data.get('VLAN_400', ''),
                        # Load new variables
                        remote_desktop_address=node_data.get('remote_desktop_address', ''),
                        file_path=node_data.get('file_path', ''),
                        web_config_url=node_data.get('web_config_url', '')
                    )
                    self.nodes.append(node)
                    self.highlight_matching_nodes()
                # Load connections
                for conn_data in state['connections']:
                    node1 = self.nodes[conn_data['from']]
                    node2 = self.nodes[conn_data['to']]
                    label = conn_data.get('label', '')  # Get the label if it exists
                    ConnectionLine(self.canvas, node1, node2, label=label)
                
                # Raise all nodes after creating connections to ensure they appear on top
                for node in self.nodes:
                    node.raise_node()
            self.save_last_file_path(file_path)  # Save the last file path
            self.legend_window.destroy()  # Close the legend window

    def save_last_file_path(self, file_path):
        with open('_internal/last_file_path.txt', 'w') as f:
            f.write(file_path)

    def load_last_file(self):
        try:
            with open('_internal/last_file_path.txt', 'r') as f:
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
            if any(ip in my_ips for ip in [node.VLAN_100, node.VLAN_200, node.VLAN_300, node.VLAN_400]):
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

    def start_move(self, event):
        """Capture the initial mouse position for dragging."""
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        """Move the window based on mouse movement."""
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def open_node_list_editor(self):
        if self.legend_window:
            self.legend_window.withdraw()
        window = tk.Toplevel(self.root)
        window.title("Live Node Editor")
        window.geometry("1250x600")

        container = tk.Frame(window)
        container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(container)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        headers = ["Name", "VLAN_100", "VLAN_200", "VLAN_300", "VLAN_400",
                "RDP", "File Path", "Web URL", "X", "Y"]
        for col, header in enumerate(headers):
            tk.Label(scrollable_frame, text=header, font=("Helvetica", 10, "bold")).grid(row=0, column=col, padx=4, pady=4)

        row_widgets = []
        live_xy_fields = {}

        def refresh_editor():
            for widgets in row_widgets:
                for w in widgets:
                    w.destroy()
            row_widgets.clear()

            for i, node in enumerate(self.nodes, start=1):
                this_node = node
                widgets = []
                
                def create_field(col, initial_value, callback):
                    entry = tk.Entry(scrollable_frame, width=15)
                    entry.insert(0, initial_value)
                    entry.grid(row=i, column=col, padx=2, pady=2)
                    entry.bind("<KeyRelease>", lambda event, e=entry: callback(e.get()))
                    widgets.append(entry)
                    return entry

                def make_updater(attr):
                    return lambda val, n=this_node: (
                        setattr(n, attr, val),
                        n.update_info(n.name, n.VLAN_100, n.VLAN_200, n.VLAN_300, n.VLAN_400,
                                    n.remote_desktop_address, n.file_path, n.web_config_url)
                    )

                create_field(0, this_node.name, make_updater("name"))
                create_field(1, this_node.VLAN_100, make_updater("VLAN_100"))
                create_field(2, this_node.VLAN_200, make_updater("VLAN_200"))
                create_field(3, this_node.VLAN_300, make_updater("VLAN_300"))
                create_field(4, this_node.VLAN_400, make_updater("VLAN_400"))
                create_field(5, this_node.remote_desktop_address, make_updater("remote_desktop_address"))
                create_field(6, this_node.file_path, make_updater("file_path"))
                create_field(7, this_node.web_config_url, make_updater("web_config_url"))

                def update_x(val, n=this_node):
                    try:
                        n.x = float(val)
                        n.update_position(n.x, n.y)
                    except ValueError:
                        pass

                def update_y(val, n=this_node):
                    try:
                        n.y = float(val)
                        n.update_position(n.x, n.y)
                    except ValueError:
                        pass

                x_entry = create_field(8, str(this_node.x), update_x)
                y_entry = create_field(9, str(this_node.y), update_y)
                live_xy_fields[this_node] = (x_entry, y_entry)

                # Remove button
                def remove_this_node(n=this_node):
                    self.canvas.delete(n.shape)
                    self.canvas.delete(n.text)
                    for conn in n.connections[:]:
                        self.canvas.delete(conn.line)
                        if conn.label_id:
                            self.canvas.delete(conn.label_id)
                        if hasattr(conn, 'label_bg') and conn.label_bg:
                            self.canvas.delete(conn.label_bg)
                        conn.node1.connections.remove(conn)
                        conn.node2.connections.remove(conn)
                    self.nodes.remove(n)
                    refresh_editor()

                btn = tk.Button(scrollable_frame, text="Remove", command=remove_this_node)
                btn.grid(row=i, column=10, padx=4)
                widgets.append(btn)

                live_xy_fields[this_node] = (x_entry, y_entry)
                row_widgets.append(widgets)

            self.list_editor_xy_fields = live_xy_fields

        def add_node():
            # Generate unique name
            base_name = "NewNode"
            existing_names = {node.name for node in self.nodes}
            name = base_name
            counter = 1
            while name in existing_names:
                name = f"{base_name}_{counter}"
                counter += 1

            # Auto Y-offset based on number of nodes
            y = 100 + len(self.nodes) * 100

            node = NetworkNode(self.canvas, name, 100, y)
            self.nodes.append(node)
            node.raise_node()
            refresh_editor()
            canvas.update_idletasks()
            canvas.yview_moveto(1.0)

        # Add/Close buttons at bottom
        btn_frame = tk.Frame(window)
        btn_frame.pack(fill=tk.X, pady=10)

        tk.Button(btn_frame, text="Add Node", command=add_node).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Close", command=window.destroy).pack(side=tk.RIGHT, padx=10)

        refresh_editor()
       
    def update_ui_colors(self):
        """Update all UI colors when the theme changes."""
        # Root window
        self.root.configure(bg=ColorConfig.current.FRAME_BG)

        # Title bar and its components
        self.title_bar.config(bg=ColorConfig.current.FRAME_BG)
        self.title_label.config(bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_FG)
        self.close_button.config(bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_FG)
        self.maximize_button.config(bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_FG)
        self.minimize_button.config(bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_FG)

        # Resize grip
        self.resize_grip.config(bg=ColorConfig.current.FRAME_BG)

       # Buttons frame and its buttons
        self.buttons_frame.config(bg=ColorConfig.current.FRAME_BG)
        button_style = {'bg': ColorConfig.current.BUTTON_BG, 'fg': ColorConfig.current.BUTTON_FG, 
                        'activebackground': ColorConfig.current.BUTTON_ACTIVE_BG, 
                        'activeforeground': ColorConfig.current.BUTTON_ACTIVE_FG}
        self.mode_button.config(bg=ColorConfig.current.BUTTON_CONFIGURATION_MODE if self.mode == "Configuration" else ColorConfig.current.BUTTON_BG, 
                            fg=ColorConfig.current.BUTTON_FG)
        
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
        
        for cb in self.buttons_frame.winfo_children()[5:9]:  # Adjusted indices since theme_button is removed
            cb.config(
                    bg=ColorConfig.current.FRAME_BG, 
                    fg=ColorConfig.current.BUTTON_FG,
                    selectcolor=ColorConfig.current.FRAME_BG, 
                    activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
                    activeforeground=ColorConfig.current.BUTTON_FG)
        self.canvas.config(bg=ColorConfig.current.FRAME_BG)
        self.info_panel.config(bg=ColorConfig.current.INFO_PANEL_BG)
        for child in self.info_panel.winfo_children():
            child.config(bg=ColorConfig.current.INFO_PANEL_BG, fg=ColorConfig.current.INFO_PANEL_TEXT)
        
        # Update legend window if it exists
        if self.legend_window and self.legend_window.winfo_exists():
            outer_frame = self.legend_window.winfo_children()[0]
            title_bar = outer_frame.winfo_children()[0]
            content_frame = outer_frame.winfo_children()[1]
            
            outer_frame.config(bg=ColorConfig.current.BORDER_COLOR)
            title_bar.config(bg=ColorConfig.current.LEGEND_BG)
            title_bar.winfo_children()[0].config(bg=ColorConfig.current.LEGEND_BG, fg=ColorConfig.current.BUTTON_FG)  # title_label
            title_bar.winfo_children()[1].config(bg=ColorConfig.current.LEGEND_BG, fg=ColorConfig.current.BUTTON_FG)  # close_button
            content_frame.config(bg=ColorConfig.current.LEGEND_BG)
            
            for widget in content_frame.winfo_children():
                if isinstance(widget, tk.Label):  # Image label
                    widget.config(bg=ColorConfig.current.LEGEND_BG)
                elif isinstance(widget, tk.Button):  # Buttons
                    widget.config(bg=ColorConfig.current.BUTTON_BG, fg=ColorConfig.current.BUTTON_FG,
                                activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
                                activeforeground=ColorConfig.current.BUTTON_ACTIVE_FG)
                elif isinstance(widget, tk.Checkbutton):  # Checkbox
                    widget.config(bg=ColorConfig.current.LEGEND_BG, fg=ColorConfig.current.BUTTON_FG,
                                selectcolor=ColorConfig.current.LEGEND_BG,
                                activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
                                activeforeground=ColorConfig.current.BUTTON_ACTIVE_FG)
            # Update theme button text
            self.theme_button.config(text="Dark Mode" if ColorConfig.current == ColorConfig.Light else "Light Mode")

        # VLAN checkboxes
        for cb in self.buttons_frame.winfo_children()[6:10]:
            cb.config(bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_FG,
                    selectcolor=ColorConfig.current.FRAME_BG, activebackground=ColorConfig.current.BUTTON_BG,
                    activeforeground=ColorConfig.current.BUTTON_FG)

        # Canvas
        self.canvas.config(bg=ColorConfig.current.FRAME_BG)
        self.top_left_resize_grip.config(bg=ColorConfig.current.FRAME_BG)
        # Info panel and labels
        self.info_panel.config(bg=ColorConfig.current.INFO_PANEL_BG)
        for child in self.info_panel.winfo_children():
            child.config(bg=ColorConfig.current.INFO_PANEL_BG, fg=ColorConfig.current.INFO_PANEL_TEXT)
        # Reset VLAN label colors unless updated by ping
        for vlan in self.vlan_labels:
            current_bg = self.vlan_labels[vlan].cget("bg")
            if current_bg not in [ColorConfig.current.NODE_PING_SUCCESS, ColorConfig.current.NODE_PING_PARTIAL_SUCCESS, ColorConfig.current.NODE_PING_FAILURE]:
                self.vlan_labels[vlan].config(bg=ColorConfig.current.INFO_PANEL_BG)

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
                                fg=ColorConfig.current.BUTTON_FG,
                                selectcolor=ColorConfig.current.FRAME_BG,
                                activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
                                activeforeground=ColorConfig.current.BUTTON_ACTIVE_FG)
            # Update theme button text explicitly
            if hasattr(self, 'theme_button') and self.theme_button.winfo_exists():
                self.theme_button.config(text="Dark Mode" if ColorConfig.current == ColorConfig.Light else "Light Mode", **button_style)

        # Nodes
        for node in self.nodes:
            current_fill = self.canvas.itemcget(node.shape, "fill")
            if current_fill not in [ColorConfig.current.NODE_PING_SUCCESS, ColorConfig.current.NODE_PING_PARTIAL_SUCCESS, ColorConfig.current.NODE_PING_FAILURE, ColorConfig.current.NODE_HOST]:
                self.canvas.itemconfig(node.shape, fill=ColorConfig.current.NODE_DEFAULT)
            self.canvas.itemconfig(node.shape, outline=ColorConfig.current.NODE_OUTLINE_DEFAULT)
            if node == self.selected_node:
                self.canvas.itemconfig(node.shape, outline=ColorConfig.current.NODE_HIGHLIGHT)

        # Connections
        for node in self.nodes:
            for conn in node.connections:
                self.canvas.itemconfig(conn.line, fill=ColorConfig.current.Connections)
                if conn.label_id:
                    self.canvas.itemconfig(conn.label_id, fill=ColorConfig.current.STICKY_NOTE_TEXT)
                    if hasattr(conn, 'label_bg') and conn.label_bg:
                        self.canvas.itemconfig(conn.label_bg, fill=ColorConfig.current.STICKY_NOTE_BG)

        # Sticky notes
        for item in self.canvas.find_withtag("sticky_note"):
            self.canvas.itemconfig(item, fill=ColorConfig.current.STICKY_NOTE_TEXT)
        for bg in self.canvas.find_withtag("sticky_bg"):
            self.canvas.itemconfig(bg, fill=ColorConfig.current.STICKY_NOTE_BG)

        # Zoom buttons
        if hasattr(self, 'zoom_level_label') and self.zoom_level_label.winfo_exists():
            for widget in (self.zoom_in_btn, self.zoom_out_btn, self.zoom_level_label):
                widget.config(bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_FG)

        if hasattr(self, 'zoom_frame') and self.zoom_frame.winfo_exists():
            self.zoom_frame.config(bg=ColorConfig.current.FRAME_BG)

    def on_close(self):
        if self.unsaved_changes:
            if messagebox.askyesno("Unsaved Changes", "You have unsaved changes. Would you like to save before exiting?"):
                self.save_network_state()  # This should prompt the user to save the file
        self.save_window_geometry()
        self.root.destroy()

    def save_window_geometry(self):
        geometry = self.root.geometry()
        state = {}
        try:
            with open("_internal/legend_state.txt", "r") as f:
                for line in f:
                    if ':' in line:
                        key, value = line.strip().split(':', 1)
                        state[key] = value
        except FileNotFoundError:
            pass

        state['WINDOW_GEOMETRY'] = geometry
    
        try:
            with open("_internal/legend_state.txt", "w") as f:
                for key, value in state.items():
                    f.write(f"{key}:{value}\n")
        except Exception as e:
            print(f"Error saving window geometry: {e}")


    def load_window_geometry(self):
        try:
            with open("_internal/legend_state.txt", "r") as f:
                for line in f:
                    if line.startswith("WINDOW_GEOMETRY:"):
                        geometry = line.strip().split(":", 1)[1]
                        self.root.geometry(geometry)
        except FileNotFoundError:
            pass


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
            with open('_internal/custom_commands.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_custom_commands(self):
        with open('_internal/custom_commands.json', 'w') as f:
            json.dump(self.custom_commands, f, indent=4)

    def manage_custom_commands(self):
        window = tk.Toplevel(self.root)
        window.title("Manage Custom Commands")
        window.geometry("400x500")
        window.transient(self.root)
        window.grab_set()

        # Create listbox for commands
        listbox = tk.Listbox(window, width=50, height=15)
        listbox.pack(pady=10, padx=10)

        # Populate listbox
        for name in self.custom_commands.keys():
            listbox.insert(tk.END, name)

        # Entry fields
        frame = tk.Frame(window)
        frame.pack(pady=10, padx=10, fill=tk.X)

        tk.Label(frame, text="Command Name:").grid(row=0, column=0, sticky='w')
        name_entry = tk.Entry(frame, width=40)
        name_entry.grid(row=0, column=1, padx=5)

        tk.Label(frame, text="Command Template:").grid(row=1, column=0, sticky='w')
        cmd_entry = tk.Entry(frame, width=40)
        cmd_entry.grid(row=1, column=1, padx=5)

        # Buttons frame
        btn_frame = tk.Frame(window)
        btn_frame.pack(pady=10)

        def add_command():
            name = name_entry.get().strip()
            cmd = cmd_entry.get().strip()
            if name and cmd:
                self.custom_commands[name] = cmd
                listbox.insert(tk.END, name)
                name_entry.delete(0, tk.END)
                cmd_entry.delete(0, tk.END)
                self.save_custom_commands()

        def edit_command():
            selection = listbox.curselection()
            if selection:
                name = listbox.get(selection[0])
                cmd = self.custom_commands[name]
                name_entry.delete(0, tk.END)
                cmd_entry.delete(0, tk.END)
                name_entry.insert(0, name)
                cmd_entry.insert(0, cmd)

        def delete_command():
            selection = listbox.curselection()
            if selection:
                name = listbox.get(selection[0])
                del self.custom_commands[name]
                listbox.delete(selection[0])
                self.save_custom_commands()

        tk.Button(btn_frame, text="Add", command=add_command).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Edit", command=edit_command).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete", command=delete_command).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Close", command=window.destroy).pack(side=tk.LEFT, padx=5)

        # Help text
        help_text = """
        Custom Commands:
        - Access through 'Manage Custom Commands' in the Start Menu
        - Use placeholders like {ip}, {name}, {file}, {web}, {rdp}, {vlan100}, etc.
        - {ip} defaults to the first non-empty VLAN address
        - Examples:
            ping {ip} -t
        """
        tk.Label(window, text=help_text, justify=tk.LEFT).pack(pady=10, padx=10)

if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(True, True)
    root.title("NodeSailor")
    gui = NetworkMapGUI(root)
    root.mainloop()
