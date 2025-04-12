import tkinter as tk
from tkinter import simpledialog, messagebox, font, filedialog, colorchooser, ttk
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

class ToolTip:
    def __init__(self, widget, text, gui, bg=None, fg=None):
        self.widget = widget
        self.text = text
        self.gui = gui
        self.bg_func = bg if callable(bg) else (lambda: bg or "#ffffe0")
        self.fg_func = fg if callable(fg) else (lambda: fg or "black")
        self.tip_window = None
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)

    def on_enter(self, event=None):
        if self.gui.show_tooltips:
            self.show_tip()

    def on_leave(self, event=None):
        self.hide_tip()

    def show_tip(self):
        if self.tip_window or not self.text:
            return
        x = self.widget.winfo_rootx()
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 2
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                         background=self.bg_func(), foreground=self.fg_func(),
                         relief='solid', borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None



class ColorConfig:
    class Light:
        NODE_DEFAULT = 'light steel blue'
        NODE_GREYED_OUT = 'gainsboro'
        NODE_HIGHLIGHT = 'gold'
        NODE_HOST = 'turquoise'
        NODE_OUTLINE_DEFAULT = 'black'
        NODE_PING_SUCCESS = 'green'
        NODE_PING_PARTIAL_SUCCESS = 'yellow'
        NODE_PING_FAILURE = 'red'
        FRAME_BG = 'white'
        INFO_NOTE_BG = 'white'
        INFO_TEXT = 'black'
        BUTTON_BG = 'white'
        BUTTON_TEXT = 'black'
        BUTTON_ACTIVE_BG = '#e0e0e0'
        BUTTON_ACTIVE_TEXT = '#000000'
        BUTTON_CONFIGURATION_MODE = 'light coral'
        Connections = 'dim gray'
        BORDER_COLOR = '#f7f7f7'

    class Dark:
        NODE_DEFAULT = '#4B5EAA'
        NODE_GREYED_OUT = '#4B5563'
        NODE_HIGHLIGHT = '#D97706'
        NODE_HOST = '#72741f'
        NODE_OUTLINE_DEFAULT = '#374151'
        NODE_PING_SUCCESS = '#047857'
        NODE_PING_PARTIAL_SUCCESS = '#B45309'
        NODE_PING_FAILURE = '#991B1B'
        FRAME_BG = "#0c0f14" #MAIN BACKBROUND
        INFO_NOTE_BG = '#111827'
        INFO_TEXT = '#8f8f8f'
        BUTTON_BG = '#4B5EAA'
        BUTTON_TEXT = '#c7c7c7'
        BUTTON_ACTIVE_BG = '#111827' #button when pressed
        BUTTON_ACTIVE_TEXT = 'black'  #button text when pressed
        BUTTON_CONFIGURATION_MODE = '#F87171'
        Connections = '#6a7586'
        BORDER_COLOR = '#374151' #f1 and legend window border colour

    # Default to Dark mode
    current = Dark

class StickyNote:
    def __init__(self, canvas, text, x, y, gui=None,
                 font=('Helvetica', '12'), bg=ColorConfig.current.INFO_NOTE_BG):
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
            fill=ColorConfig.current.INFO_TEXT,
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
                fill=ColorConfig.current.INFO_NOTE_BG)

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
                fg=ColorConfig.current.BUTTON_TEXT,
                activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
                activeforeground=ColorConfig.current.BUTTON_ACTIVE_TEXT,
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
            x, y, text=name, font=self.font,
            fill=ColorConfig.current.BUTTON_TEXT,
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
                            bg=ColorConfig.current.BUTTON_BG, fg=ColorConfig.current.BUTTON_TEXT,
                            activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
                            activeforeground=ColorConfig.current.BUTTON_ACTIVE_TEXT,
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
    def __init__(self, canvas, node1, node2, label='', connectioninfo=None):
        self.canvas = canvas
        self.node1 = node1
        self.node2 = node2
        self.line = canvas.create_line(node1.x, node1.y, node2.x, node2.y,width=2, fill=ColorConfig.current.Connections)
        self.label = label
        self.connectioninfo = connectioninfo
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
        self.label_id = self.canvas.create_text(mid_x, mid_y, text=self.label, font=('Helvetica', '12'), fill=ColorConfig.current.INFO_TEXT, tags="connection_label", anchor="center")

        self.info_popup = None

        if self.connectioninfo:
            def show_info(event):
                self.info_popup = tk.Toplevel(self.canvas)
                self.info_popup.wm_overrideredirect(True)
                self.info_popup.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
                label = tk.Label(self.info_popup, text=self.connectioninfo,
                                background=ColorConfig.current.INFO_NOTE_BG,
                                foreground=ColorConfig.current.INFO_TEXT,
                                relief='solid', borderwidth=1,
                                font=("Helvetica", 10), justify='left')
                label.pack()

            def hide_info(event):
                if self.info_popup:
                    self.info_popup.destroy()
                    self.info_popup = None

            self.canvas.tag_bind(self.label_id, "<Enter>", show_info)
            self.canvas.tag_bind(self.label_id, "<Leave>", hide_info)

            def edit_connectioninfo(event):
                dialog = tk.Toplevel(self.canvas)
                dialog.title("Edit Connection Details")
                tk.Label(dialog, text="Label:").grid(row=0, column=0, padx=10, pady=5)
                label_entry = tk.Entry(dialog, width=40)
                label_entry.insert(0, self.label)
                label_entry.grid(row=0, column=1, padx=10, pady=5)

                tk.Label(dialog, text="Info (on hover):").grid(row=1, column=0, padx=10, pady=5)
                info_entry = tk.Entry(dialog, width=40)
                info_entry.insert(0, self.connectioninfo or "")
                info_entry.grid(row=1, column=1, padx=10, pady=5)

                def submit():
                    self.label = label_entry.get()
                    self.connectioninfo = info_entry.get()
                    self.update_label()
                    dialog.destroy()

                tk.Button(dialog, text="Save", command=submit).grid(row=2, column=0, columnspan=2, pady=10)
                dialog.transient(self.canvas)
                dialog.grab_set()
                self.canvas.wait_window(dialog)

            self.canvas.tag_bind(self.label_id, "<Button-3>", edit_connectioninfo)
    
        # Recreate a background similar to StickyNote
        bbox = self.canvas.bbox(self.label_id)
        if bbox:
            padding = 2
            self.label_bg = self.canvas.create_rectangle(bbox[0]-padding, bbox[1]-padding, bbox[2]+padding, bbox[3]+padding, fill=ColorConfig.current.INFO_NOTE_BG, outline='')
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
        self.show_tooltips = False
        self.color_editor_window = None
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
                                   fg=ColorConfig.current.BUTTON_TEXT, font=self.custom_font)
        self.title_label.pack(side=tk.LEFT, padx=10)
        # make the title label draggable
        self.title_label.bind("<ButtonPress-1>", self.start_move)
        self.title_label.bind("<B1-Motion>", self.do_move)

        self.close_button = tk.Button(self.title_bar, text='X', command=self.on_close,
                                     bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT,
                                     font=self.custom_font)
        self.close_button.pack(side=tk.RIGHT)
        
        # Maximize Button
        self.maximize_button = tk.Button(self.title_bar, text='[]', command=self.maximize_restore,
                                       bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT,
                                       font=self.custom_font)
        self.maximize_button.pack(side=tk.RIGHT)

        # Minimize Button
        self.minimize_button = tk.Button(self.title_bar, text='-', command=self.minimize_window,
                                        bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT,
                                        font=self.custom_font)
        self.minimize_button.pack(side=tk.RIGHT)

        self.help_button = tk.Button(self.title_bar, text='?', command=self.toggle_tooltips,
                             bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT,
                             font=self.custom_font)
        self.help_button.pack(side=tk.RIGHT)
       
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
        self.mode_button.pack(side=tk.LEFT, padx=(5, 100), pady=5)        
        
        ToolTip(self.mode_button, "Toggle Operator/Configuration mode", self,
        bg=lambda: ColorConfig.current.INFO_NOTE_BG,
        fg=lambda: ColorConfig.current.INFO_TEXT)

        whoamI_button = tk.Button(self.buttons_frame, text='Who am I?', command=self.highlight_matching_nodes, **button_style)
        whoamI_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        ToolTip(whoamI_button, "Highlight matching nodes", self,
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
                fg=ColorConfig.current.BUTTON_TEXT,
                selectcolor=ColorConfig.current.FRAME_BG,
                activebackground=ColorConfig.current.BUTTON_BG,
                activeforeground=ColorConfig.current.BUTTON_TEXT,
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

    def toggle_tooltips(self):
        self.show_tooltips = not self.show_tooltips
        self.help_button.config(relief=tk.SUNKEN if self.show_tooltips else tk.RAISED)
        if self.show_tooltips:
            self.show_help()

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

    def add_custom_titlebar(self, window, title, on_close=None):
        outer = tk.Frame(window, bg=ColorConfig.current.BORDER_COLOR, padx=2, pady=2)
        outer.pack(fill=tk.BOTH, expand=True)

        titlebar = tk.Frame(outer, bg=ColorConfig.current.FRAME_BG)
        titlebar.pack(side=tk.TOP, fill=tk.X)

        label = tk.Label(titlebar, text=title, bg=ColorConfig.current.FRAME_BG,
                        fg=ColorConfig.current.BUTTON_TEXT, font=self.custom_font)
        label.pack(side=tk.LEFT, padx=10)

        btn = tk.Button(titlebar, text='X', command=on_close or window.destroy,
                        bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT,
                        font=self.custom_font)
        btn.pack(side=tk.RIGHT)

        def start(event):
            window._x = event.x
            window._y = event.y

        def drag(event):
            x = window.winfo_x() + event.x - window._x
            y = window.winfo_y() + event.y - window._y
            window.geometry(f"+{x}+{y}")

        titlebar.bind("<ButtonPress-1>", start)
        titlebar.bind("<B1-Motion>", drag)
        label.bind("<ButtonPress-1>", start)
        label.bind("<B1-Motion>", drag)

        return outer

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

        self.color_editor_window, content = self.create_popup("Color Scheme Editor", 400, 900, on_close=on_close, grab=False)

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


    def edit_vlan_labels(self):
        if hasattr(self, 'vlan_label_editor') and self.vlan_label_editor and self.vlan_label_editor.winfo_exists():
            self.vlan_label_editor.lift()
            return

        if self.legend_window and self.legend_window.winfo_exists():
            self.legend_window.withdraw()

        def close_vlan_editor():
            try: self.vlan_label_editor.grab_release()
            except: pass
            self.vlan_label_editor.destroy()
            self.vlan_label_editor = None

        self.vlan_label_editor, content = self.create_popup("Edit VLAN Labels", 800, 830, on_close=close_vlan_editor, grab=False)

        entries = {}
        for i, vlan in enumerate(self.vlan_label_names.keys()):
            tk.Label(content, text=vlan + ":", anchor="e",
                    bg=ColorConfig.current.FRAME_BG,
                    fg=ColorConfig.current.BUTTON_TEXT,
                    font=('Helvetica', 10))\
                .grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry = tk.Entry(content)
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
            close_vlan_editor()

        button_frame = tk.Frame(content, bg=ColorConfig.current.FRAME_BG)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        tk.Button(button_frame, text="Save", command=save_labels,
                bg=ColorConfig.current.BUTTON_BG,
                fg=ColorConfig.current.BUTTON_TEXT,
                activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
                activeforeground=ColorConfig.current.BUTTON_ACTIVE_TEXT,
                font=('Helvetica', 10)).pack()

    def show_help(self, event=None):
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
            ("NodeSailor v0.9.11 - Help\n", "title"),
            ("\nOverview:\n", "header"),
            ("NodeSailor is a simple network visualization tool.  It allows the user to create a network map, display and test their connections with options for pinging, RDP and more with the implementation of custom commands.\n", "text"),
            
            ("\nUser Modes:\n", "header"),
            ("- Operator: Monitor and interact with the network.\n"
            "- Configuration: Build and edit the network layout.\n", "text"),

            ("\nOperator Mode:\n", "header"),
            ("- Left Click on Node: Ping the node (Green = all assigned IP addresses connected, Yellow = partial connection, Red = no connection).\n"
            "- Right Click on Node: Open context menu.\n"
            "- Right Click and Drag: Pan the canvas.\n"
            "- Scroll Wheel: Zoom in and out.\n"
            "- Who am I?: Highlight then node matching your machine's IP.\n"
            "- Ping All: Ping every node.\n"
            "- Clear Status: Reset node status.\n", "text"),

            ("\nConfiguration Mode:\n", "header"),
            ("- Double Left Click: Create a new node.\n"
            "- Shift + Double Left Click: Add a sticky note.\n"
            "- Middle Click: Create a connection line between two nodes.\n"
            "- Shift + Middle Click: Remove connection line.\n"
            "- Left Click + Drag: Move nodes or notes.\n"
            "- Right Click: Open context menu.\n", "text"),

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
                self.vlan_labels[vlan].config(bg=ColorConfig.current.INFO_NOTE_BG)


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

            title_label = tk.Label(title_bar, text="Nodesailor v0.9.11", bg=ColorConfig.current.FRAME_BG,
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
            img = Image.open("_internal/legend.png").resize((404, 400), Image.Resampling.LANCZOS)
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

            color_editor_button = tk.Button(content_frame, text='Edit Colors',
                                            command=self.show_color_editor, **button_style)
            color_editor_button.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

            edit_labels_btn = tk.Button(content_frame, text='Edit VLAN Labels',
                             command=self.edit_vlan_labels, **button_style)
            edit_labels_btn.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            
            node_list_btn = tk.Button(content_frame, text='List View (Table Editor)',
                            command=self.open_node_list_editor, **button_style)
            node_list_btn.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            
            connection_list_btn = tk.Button(content_frame, text='Edit Connections',
                                command=self.open_connection_list_editor, **button_style)
            connection_list_btn.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

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
            self.vlan_labels[vlan].config(bg=ColorConfig.current.INFO_NOTE_BG)

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
        if hasattr(self, 'node_window') and self.node_window and self.node_window.winfo_exists():
            self.node_window.lift()
            return

        def close_node_editor():
            try:
                self.node_window.grab_release()
            except:
                pass
            self.node_window.destroy()
            self.node_window = None

        win, content = self.create_popup("Edit Node" if node else "Create Node", 300, 380, on_close=close_node_editor, grab=False)
        self.node_window = win


        label_args = {'bg': ColorConfig.current.FRAME_BG, 'fg': ColorConfig.current.BUTTON_TEXT, 'font': ('Helvetica', 10)}
        entry_args = {'bg': 'white', 'fg': 'black'}

        # Node Name
        tk.Label(content, text="Node Name:", **label_args).grid(row=0, column=0, padx=10, pady=5, sticky="e")
        name_entry = tk.Entry(content, **entry_args)
        name_entry.grid(row=0, column=1, padx=10, pady=5)
        if node: name_entry.insert(0, node.name)
        name_entry.focus_set()

        VLAN_entries = {}
        for i, vlan in enumerate(["VLAN_100", "VLAN_200", "VLAN_300", "VLAN_400"], start=1):
            tk.Label(content, text=f"{vlan}:", **label_args).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry = tk.Entry(content, **entry_args)
            entry.grid(row=i, column=1, padx=10, pady=5)
            if node: entry.insert(0, getattr(node, vlan))
            VLAN_entries[vlan] = entry

        tk.Label(content, text="Remote Desktop Address:", **label_args).grid(row=5, column=0, padx=10, pady=5, sticky="e")
        remote_entry = tk.Entry(content, **entry_args)
        remote_entry.grid(row=5, column=1, padx=10, pady=5)
        if node: remote_entry.insert(0, node.remote_desktop_address)

        tk.Label(content, text="File Path:", **label_args).grid(row=6, column=0, padx=10, pady=5, sticky="e")
        file_entry = tk.Entry(content, **entry_args)
        file_entry.grid(row=6, column=1, padx=10, pady=5)
        if node: file_entry.insert(0, node.file_path)

        tk.Label(content, text="Web Config URL:", **label_args).grid(row=7, column=0, padx=10, pady=5, sticky="e")
        web_entry = tk.Entry(content, **entry_args)
        web_entry.grid(row=7, column=1, padx=10, pady=5)
        if node: web_entry.insert(0, node.web_config_url)

        def save_node():
            name = name_entry.get()
            vlan_ips = {vlan: VLAN_entries[vlan].get() for vlan in VLAN_entries}
            remote = remote_entry.get()
            path = file_entry.get()
            web = web_entry.get()
            if node:
                node.update_info(name, **vlan_ips, remote_desktop_address=remote, file_path=path, web_config_url=web)
                self.on_node_select(node)
            else:
                if name and event:
                    new_node = NetworkNode(self.canvas, name, event.x, event.y, **vlan_ips,
                                        remote_desktop_address=remote, file_path=path, web_config_url=web)
                    self.nodes.append(new_node)
                    self.on_node_select(new_node)
            close_node_editor()

        tk.Button(content, text="Save", command=save_node,
                bg=ColorConfig.current.BUTTON_BG,
                fg=ColorConfig.current.BUTTON_TEXT,
                activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
                activeforeground=ColorConfig.current.BUTTON_ACTIVE_TEXT,
                font=('Helvetica', 10)).grid(row=8, column=0, columnspan=2, pady=10)



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
                            dialog = tk.Toplevel(self.root)
                            dialog.title("Connection Details")
                            tk.Label(dialog, text="Label:").grid(row=0, column=0, padx=10, pady=5)
                            label_entry = tk.Entry(dialog, width=40)
                            label_entry.grid(row=0, column=1, padx=10, pady=5)

                            tk.Label(dialog, text="Info (on hover):").grid(row=1, column=0, padx=10, pady=5)
                            info_entry = tk.Entry(dialog, width=40)
                            info_entry.grid(row=1, column=1, padx=10, pady=5)

                            def submit():
                                label = label_entry.get()
                                info = info_entry.get()
                                connection = ConnectionLine(self.canvas, self.connection_start_node, node, label=label, connectioninfo=info)
                                self.connection_start_node = None
                                self.raise_all_nodes()
                                self.unsaved_changes = True
                                dialog.destroy()

                            tk.Button(dialog, text="OK", command=submit).grid(row=2, column=0, columnspan=2, pady=10)
                            dialog.transient(self.root)
                            dialog.grab_set()
                            self.root.wait_window(dialog)
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
                tooltip = conn_data.get('connectioninfo', None)
                ConnectionLine(self.canvas, node1, node2, label=label, connectioninfo=tooltip)


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
                    tooltip = conn_data.get('connectioninfo', None)
                    ConnectionLine(self.canvas, node1, node2, label=label, connectioninfo=tooltip)

                
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
        if self.legend_window and self.legend_window.winfo_exists():
            self.legend_window.destroy()
            self.legend_window = None

        if hasattr(self, 'node_list_editor') and self.node_list_editor.winfo_exists():
            self.node_list_editor.lift()
            return

        def close_editor():
            try:
                self.node_list_editor.grab_release()
            except:
                pass
            self.node_list_editor.destroy()
            self.node_list_editor = None

        self.node_list_editor, content = self.create_popup("Node List Editor", 1100, 1000, on_close=close_editor, grab=False)
        
        container = tk.Frame(content, bg=ColorConfig.current.FRAME_BG)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg=ColorConfig.current.FRAME_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.node_list_frame = tk.Frame(canvas, bg=ColorConfig.current.FRAME_BG)

        self.node_list_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.node_list_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.list_editor_xy_fields = {}

        def rebuild_editor_content():
            for widget in self.node_list_frame.winfo_children():
                widget.destroy()

            fields = [
                ("Name", "name"),
                ("VLAN 100", "VLAN_100"),
                ("VLAN 200", "VLAN_200"),
                ("VLAN 300", "VLAN_300"),
                ("VLAN 400", "VLAN_400"),
                ("Remote Desktop", "remote_desktop_address"),
                ("File Path", "file_path"),
                ("Web URL", "web_config_url"),
                ("X", "x"),
                ("Y", "y"),
            ]

            for col_index, (label, _) in enumerate(fields):
                tk.Label(self.node_list_frame, text=label, font=('Helvetica', 10, 'bold'),
                        bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT)\
                        .grid(row=0, column=col_index, padx=5, pady=2)
            tk.Label(self.node_list_frame, text="Delete", font=('Helvetica', 10, 'bold'),
                    bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT)\
                    .grid(row=0, column=len(fields), padx=5)

            tk.Button(self.node_list_frame, text="➕ Add Node", command=add_node,
                    bg=ColorConfig.current.BUTTON_BG,
                    fg=ColorConfig.current.BUTTON_TEXT,
                    activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
                    activeforeground=ColorConfig.current.BUTTON_ACTIVE_TEXT)\
                    .grid(row=1, column=0, columnspan=len(fields)+1, sticky="w", pady=5)

            for row_index, node in enumerate(self.nodes, start=2):
                xy_fields = []
                for col_index, (label, attr) in enumerate(fields):
                    value = getattr(node, attr)
                    entry = tk.Entry(self.node_list_frame, width=15)
                    entry.insert(0, str(value))
                    entry.grid(row=row_index, column=col_index, padx=2, pady=2)

                    def make_callback(n=node, a=attr, e=entry):
                        def update_field(event):
                            val = e.get()
                            if a in ("x", "y"):
                                try:
                                    val = float(val)
                                    if a == "x":
                                        n.update_position(val, n.y)
                                    else:
                                        n.update_position(n.x, val)
                                except ValueError:
                                    return
                            else:
                                setattr(n, a, val)
                                if a == "name":
                                    n.canvas.itemconfigure(n.text, text=n.name)
                                n.adjust_node_size()
                                self.unsaved_changes = True
                        return update_field

                    entry.bind("<FocusOut>", make_callback())

                    if attr in ("x", "y"):
                        xy_fields.append(entry)

                self.list_editor_xy_fields[node] = xy_fields

                def delete_node_callback(n=node):
                    def delete():
                        self.remove_node(n)
                        rebuild_editor_content()
                    return delete

                btn = tk.Button(self.node_list_frame, text="🗑", fg="red", command=delete_node_callback())
                btn.grid(row=row_index, column=len(fields), padx=5)

        def add_node():
            new_node = NetworkNode(self.canvas, name="NewNode", x=100, y=100)
            self.nodes.append(new_node)
            self.on_node_select(new_node)
            self.unsaved_changes = True
            rebuild_editor_content()

        rebuild_editor_content()

        self.fix_window_geometry(self.node_list_editor, 1100, 1000)

    def open_connection_list_editor(self):
        if self.legend_window and self.legend_window.winfo_exists():
            self.legend_window.destroy()
            self.legend_window = None

        if hasattr(self, 'connection_list_editor') and self.connection_list_editor.winfo_exists():
            self.connection_list_editor.lift()
            return

        def close_editor():
            try:
                self.connection_list_editor.grab_release()
            except:
                pass
            self.connection_list_editor.destroy()
            self.connection_list_editor = None

        self.connection_list_editor, content = self.create_popup("Connection List Editor", 950, 600, on_close=close_editor, grab=False)

        container = tk.Frame(content, bg=ColorConfig.current.FRAME_BG)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg=ColorConfig.current.FRAME_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.connection_list_frame = tk.Frame(canvas, bg=ColorConfig.current.FRAME_BG)

        self.connection_list_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.connection_list_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def rebuild_editor_content():
            for widget in self.connection_list_frame.winfo_children():
                widget.destroy()

            headers = ["From", "To", "Label", "Info", "Delete"]
            for i, h in enumerate(headers):
                tk.Label(self.connection_list_frame, text=h, font=('Helvetica', 10, 'bold'),
                        bg=ColorConfig.current.FRAME_BG,
                        fg=ColorConfig.current.BUTTON_TEXT).grid(row=0, column=i, padx=5, pady=2)

            connections = set()
            for node in self.nodes:
                for conn in node.connections:
                    if conn not in connections:
                        connections.add(conn)

            for row_index, conn in enumerate(connections, start=1):
                tk.Label(self.connection_list_frame, text=conn.node1.name,
                        bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT)\
                    .grid(row=row_index, column=0, padx=5)
                tk.Label(self.connection_list_frame, text=conn.node2.name,
                        bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT)\
                    .grid(row=row_index, column=1, padx=5)

                label_entry = tk.Entry(self.connection_list_frame, width=30)
                label_entry.insert(0, conn.label or "")
                label_entry.grid(row=row_index, column=2, padx=5)

                info_entry = tk.Entry(self.connection_list_frame, width=50)
                info_entry.insert(0, conn.connectioninfo or "")
                info_entry.grid(row=row_index, column=3, padx=5)

                def make_update_callback(c=conn, le=label_entry, ie=info_entry):
                    def update_fields(event=None):
                        c.label = le.get()
                        c.connectioninfo = ie.get()
                        c.update_label()
                        self.unsaved_changes = True
                    return update_fields

                label_entry.bind("<FocusOut>", make_update_callback())
                info_entry.bind("<FocusOut>", make_update_callback())

                def delete_conn(c=conn):
                    self.canvas.delete(c.line)
                    if c.label_id:
                        self.canvas.delete(c.label_id)
                    if hasattr(c, 'label_bg') and c.label_bg:
                        self.canvas.delete(c.label_bg)
                    c.node1.connections.remove(c)
                    c.node2.connections.remove(c)
                    self.unsaved_changes = True
                    rebuild_editor_content()

                tk.Button(self.connection_list_frame, text="🗑", fg="red", command=lambda c=conn: delete_conn(c))\
                    .grid(row=row_index, column=4, padx=5)

        rebuild_editor_content()


    def update_ui_colors(self):
        """Update all UI colors when the theme changes."""
        # Root window
        self.root.configure(bg=ColorConfig.current.FRAME_BG)

        # Title bar and its components
        self.title_bar.config(bg=ColorConfig.current.FRAME_BG)
        self.title_label.config(bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT)
        self.help_button.config(bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT)
        self.close_button.config(bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT)
        self.maximize_button.config(bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT)
        self.minimize_button.config(bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT)

        # Resize grip
        self.resize_grip.config(bg=ColorConfig.current.FRAME_BG)

       # Buttons frame and its buttons
        self.buttons_frame.config(bg=ColorConfig.current.FRAME_BG)
        button_style = {'bg': ColorConfig.current.BUTTON_BG, 'fg': ColorConfig.current.BUTTON_TEXT, 
                        'activebackground': ColorConfig.current.BUTTON_ACTIVE_BG, 
                        'activeforeground': ColorConfig.current.BUTTON_ACTIVE_TEXT}
        self.mode_button.config(bg=ColorConfig.current.BUTTON_CONFIGURATION_MODE if self.mode == "Configuration" else ColorConfig.current.BUTTON_BG, 
                            fg=ColorConfig.current.BUTTON_TEXT)
        
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
                    fg=ColorConfig.current.BUTTON_TEXT,
                    selectcolor=ColorConfig.current.FRAME_BG, 
                    activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
                    activeforeground=ColorConfig.current.BUTTON_TEXT)
        self.canvas.config(bg=ColorConfig.current.FRAME_BG)
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
        for cb in self.buttons_frame.winfo_children()[6:10]:
            cb.config(bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT,
                    selectcolor=ColorConfig.current.FRAME_BG, activebackground=ColorConfig.current.BUTTON_BG,
                    activeforeground=ColorConfig.current.BUTTON_TEXT)

        # Canvas
        self.canvas.config(bg=ColorConfig.current.FRAME_BG)
        self.top_left_resize_grip.config(bg=ColorConfig.current.FRAME_BG)
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

    def create_popup(self, title, width, height, on_close=None, grab=True):
        win = tk.Toplevel(self.root)
        win.overrideredirect(True)
        win.transient(self.root)
        if grab:
            win.grab_set()

        def real_close():
            try:
                win.grab_release()
            except:
                pass
            win.destroy()

        wrapper = self.add_custom_titlebar(win, title, on_close or real_close)
        content = tk.Frame(wrapper, bg=ColorConfig.current.FRAME_BG)
        content.pack(fill=tk.BOTH, expand=True)

        def apply_geometry():
            self.fix_window_geometry(win, width, height)
        win.after(1, apply_geometry)

        return win, content

    #Fixes window geopetry issues for vlan, list view, edit connections and manage custom commands windows         
    def fix_window_geometry(self, window, width, height):
        window.update_idletasks()  # Make sure widget sizes are calculated
        window.geometry(f"{width}x{height}")
        self.center_window_on_screen(window)
        window.transient(self.root)
        window.lift()

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
        if self.legend_window and self.legend_window.winfo_exists():
            try: self.legend_window.grab_release()
            except: pass
            self.legend_window.destroy()
            self.legend_window = None

        if hasattr(self, 'custom_cmd_window'):
            try:
                if self.custom_cmd_window.winfo_exists():
                    self.custom_cmd_window.lift()
                    return
            except:
                self.custom_cmd_window = None

        def on_close():
            if self.custom_cmd_window:
                try: self.custom_cmd_window.grab_release()
                except: pass
                self.custom_cmd_window.destroy()
                self.custom_cmd_window = None

        self.custom_cmd_window, content = self.create_popup("Manage Custom Commands", 400, 500, on_close=on_close, grab=False)

        listbox = tk.Listbox(content, width=50, height=10)
        listbox.pack(pady=10, padx=10)

        for name in self.custom_commands.keys():
            listbox.insert(tk.END, name)

        frame = tk.Frame(content, bg=ColorConfig.current.FRAME_BG)
        frame.pack(pady=5, padx=10, fill=tk.X)

        label_args = {'bg': ColorConfig.current.FRAME_BG, 'fg': ColorConfig.current.BUTTON_TEXT, 'font': ('Helvetica', 10)}
        entry_args = {'bg': 'white', 'fg': 'black'}

        tk.Label(frame, text="Command Name:", **label_args).grid(row=0, column=0, sticky='w')
        name_entry = tk.Entry(frame, width=40, **entry_args)
        name_entry.grid(row=0, column=1, padx=5)

        tk.Label(frame, text="Command Template:", **label_args).grid(row=1, column=0, sticky='w')
        cmd_entry = tk.Entry(frame, width=40, **entry_args)
        cmd_entry.grid(row=1, column=1, padx=5)

        btn_frame = tk.Frame(content, bg=ColorConfig.current.FRAME_BG)
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

        btn_style = {
            'bg': ColorConfig.current.BUTTON_BG,
            'fg': ColorConfig.current.BUTTON_TEXT,
            'activebackground': ColorConfig.current.BUTTON_ACTIVE_BG,
            'activeforeground': ColorConfig.current.BUTTON_ACTIVE_TEXT,
            'font': ('Helvetica', 10),
            'padx': 5,
            'pady': 2
        }

        tk.Button(btn_frame, text="Add", command=add_command, **btn_style).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Edit", command=edit_command, **btn_style).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete", command=delete_command, **btn_style).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Close", command=on_close, **btn_style).pack(side=tk.LEFT, padx=5)

        tk.Label(content, text="""
    Custom Commands:
    - Use placeholders like {ip}, {name}, {file}, {web}, {rdp}, {vlan100}, etc.
    - {ip} defaults to the first non-empty VLAN address
    - Example: ping {ip} -t
    """, justify=tk.LEFT, bg=ColorConfig.current.FRAME_BG,
                fg=ColorConfig.current.INFO_TEXT, font=('Helvetica', 9),
                wraplength=380).pack(pady=10, padx=10)



if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(True, True)
    root.title("NodeSailor")
    gui = NetworkMapGUI(root)
    root.mainloop()
