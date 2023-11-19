import tkinter as tk
from tkinter import simpledialog, messagebox, font, filedialog
import subprocess
from threading import Thread
import json
import platform
from PIL import Image, ImageTk
import socket
import os
import webbrowser

def get_ip_addresses():
    ip_addresses = []
    hostname = socket.gethostname()
    try:
        ip_address = socket.gethostbyname(hostname)
        ip_addresses.append(ip_address)
    except socket.gaierror:
        pass
    return ip_addresses

class ColorConfig:
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
    BUTTON_CONFIGURATION_MODE = 'light coral'
    INFO_PANEL_BG = 'white'
    INFO_PANEL_TEXT = 'black'
    Connections = 'dim gray'

class StickyNote:
    def __init__(self, canvas, text, x, y, font=('Helvetica', '12'), bg=ColorConfig.STICKY_NOTE_BG):
        self.canvas = canvas
        self.text = text
        self.x = x
        self.y = y
        self.bg = bg
        self.font = font
        self.bg_shape = canvas.create_rectangle(x, y, x + 100, y + 50, fill=ColorConfig.FRAME_BG, outline='')
        self.note = canvas.create_text(x, y, text=text, font=self.font, tags="sticky_note", anchor="nw")
        self.canvas.tag_bind(self.note, '<Button-1>', self.on_click)
        self.canvas.tag_bind(self.note, '<Shift-B1-Motion>', self.on_drag_notes)
        self.canvas.tag_bind(self.note, '<ButtonRelease-1>', self.on_release)
        self.adjust_note_size()
        self.type = 'sticky'
        
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
                self.last_drag_x = event.x
                self.last_drag_y = event.y
                self.adjust_note_size()
    
    def on_release(self, event):
        self.canvas.selected_object = None
        self.canvas.selected_object_type = None
    
    def adjust_note_size(self):
        bbox = self.canvas.bbox(self.note)  # Get the bounding box of the text
        if bbox:
            padding = 2
            self.canvas.coords(self.bg_shape, bbox[0]-padding, bbox[1]-padding, bbox[2]+padding, bbox[3]+padding)

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
        self.font = font.Font(family="Helvetica", size=12)  # Define font
        self.shape = canvas.create_rectangle(
            x - 15, y - 15, x + 15, y + 15,
            fill=ColorConfig.NODE_DEFAULT, outline=ColorConfig.NODE_OUTLINE_DEFAULT, width=2,  # Adjust width for a bolder outline
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
        self.canvas.coords(self.shape, x - 15, y - 15, x + 15, y + 15)
        self.canvas.coords(self.text, x, y)
        self.adjust_node_size()  # Adjust the node size initially
        for line in self.connections:
            line.update_position()

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
            if all(results):
                color = ColorConfig.NODE_PING_SUCCESS  # All IPs responded
            elif any(results):
                color = ColorConfig.NODE_PING_PARTIAL_SUCCESS  # Some IPs responded
            else:
                color = ColorConfig.NODE_PING_FAILURE   # No IPs responded
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
            context_menu = tk.Menu(self.canvas, tearoff=0)
            context_menu.add_command(label="Edit Node Information", command=self.edit_node_info)
            context_menu.add_command(label="Open Remote Desktop", command=self.open_remote_desktop)
            context_menu.add_command(label="Open File Explorer", command=self.open_file_explorer)
            context_menu.add_command(label="Open Web Browser", command=self.open_web_browser)
            context_menu.add_separator()
            context_menu.add_command(label="Delete Node", command=self.delete_node)
            context_menu.tk_popup(event.x_root, event.y_root)
            
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
        os.startfile(self.file_path)

    def open_web_browser(self):
        if not self.web_config_url:
            messagebox.showinfo("Info", "No web config URL set for this node.")
            return
        webbrowser.open(self.web_config_url, new=2)  # Open URL in a new tab, if exists
        pass
    
    def delete_node(self):
        gui.remove_node(self)

class ConnectionLine:
    def __init__(self, canvas, node1, node2, label=''):
        self.canvas = canvas
        self.node1 = node1
        self.node2 = node2
        self.line = canvas.create_line(node1.x, node1.y, node2.x, node2.y,width=2, fill=ColorConfig.Connections)
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
            self.label_bg = self.canvas.create_rectangle(bbox[0]-padding, bbox[1]-padding, bbox[2]+padding, bbox[3]+padding, fill=ColorConfig.STICKY_NOTE_BG, outline='')
            self.canvas.tag_lower(self.label_bg, self.label_id)  # Ensure the background is behind the text

    def set_label(self, label):
        self.label = label
        self.update_label()

class NetworkMapGUI:
    def __init__(self, root):
        self.root = root
        root.iconbitmap('favicon.ico')
        self.custom_font = font.Font(family="Helvetica", size=12)
        self.mode = "Configuration"
        self.selected_object_type = None
        self.connection_start_node = None
        
        # Buttons Frame
        buttons_frame = tk.Frame(root)
        buttons_frame.pack(side=tk.TOP, fill=tk.X)
        buttons_frame.config(bg=ColorConfig.FRAME_BG)
        
        # Load NodeSailor image
        img = Image.open("NodeSailorvsmall.png")
        photo_img = ImageTk.PhotoImage(img)

        # Create a button with the image
        img_button = tk.Button(buttons_frame, image=photo_img, command=self.display_legend, borderwidth=0, highlightthickness=0, relief=tk.FLAT)
        img_button.image = photo_img  # Keep a reference to the PhotoImage object
        img_button.pack(side=tk.LEFT)
        
        # Update button styles
        button_style = {'font': self.custom_font, 'bg': ColorConfig.BUTTON_BG, 'fg': ColorConfig.BUTTON_FG, 'relief': tk.GROOVE}

        save_button = tk.Button(buttons_frame, text='Save', command=self.save_network_state, **button_style)
        save_button.pack(side=tk.LEFT, padx=5, pady=5)

        load_button = tk.Button(buttons_frame, text='Load', command=self.load_network_state, **button_style)
        load_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.mode_button = tk.Button(buttons_frame, text='Configuration', command=self.toggle_mode, **button_style)
        self.mode_button.pack(side=tk.LEFT, padx=(5, 100), pady=5)

        whoamI_button = tk.Button(buttons_frame, text='Who am I?', command=self.highlight_matching_nodes, **button_style)
        whoamI_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        clear_status_button = tk.Button(buttons_frame, text='Clear Status', command=self.clear_node_status, **button_style)
        clear_status_button.pack(side=tk.LEFT, padx=5, pady=5)

        ping_all_button = tk.Button(buttons_frame, text='Ping All', command=self.ping_all, **button_style)
        ping_all_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Checkboxes for VLANs
        self.vlan_visibility = {'VLAN_100': tk.BooleanVar(value=True),
                                'VLAN_200': tk.BooleanVar(value=True),
                                'VLAN_300': tk.BooleanVar(value=True),
                                'VLAN_400': tk.BooleanVar(value=True)}

        for vlan, var in self.vlan_visibility.items():
            cb = tk.Checkbutton(buttons_frame, text=vlan, var=var, bg=ColorConfig.FRAME_BG, command=self.update_vlan_visibility)
            cb.pack(side=tk.LEFT, padx=5)

        # Canvas below the buttons
        self.canvas = tk.Canvas(root, width=1600, height=900, bg=ColorConfig.FRAME_BG, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.nodes = []
        self.selected_node = None
        self.previous_selected_node = None
        
        root.bind('<F1>', self.show_help)        
        root.bind('<plus>', self.zoom_in)  # Zoom in with '+'
        root.bind('<minus>', self.zoom_out)  # Zoom out with '-'
        root.bind('<Left>', lambda event: self.pan_canvas('left'))  # Pan left
        root.bind('<Right>', lambda event: self.pan_canvas('right'))  # Pan right
        root.bind('<Up>', lambda event: self.pan_canvas('up'))  # Pan up
        root.bind('<Down>', lambda event: self.pan_canvas('down'))  # Pan down
        self.canvas.bind('<Double-1>', self.create_node)
        self.canvas.bind('<B1-Motion>', self.move_node)
        self.canvas.bind('<Shift-Double-1>', self.create_sticky_note)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind('<Button-2>', self.create_connection)
        self.canvas.bind('<Shift-Button-2>', self.remove_connection)

         # Info Panel
        self.info_panel = tk.Frame(root, bd=2, relief=tk.SUNKEN, bg=ColorConfig.INFO_PANEL_BG)
        self.info_panel.place(relx=1.0, rely=1.0, anchor='se')

        info_label_style = {'font': ('Helvetica', 10), 'bg': ColorConfig.INFO_PANEL_BG, 'fg': 'black', 'anchor': 'w'}
        info_value_style = {'font': ('Helvetica', 10), 'bg': ColorConfig.INFO_PANEL_BG}

        tk.Label(self.info_panel, text="Name:", **info_label_style).grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.node_name_label = tk.Label(self.info_panel, text="-", **info_value_style)
        self.node_name_label.grid(row=0, column=1, sticky='w', padx=5, pady=2)

        tk.Label(self.info_panel, text="", **info_label_style).grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.node_ip_label = tk.Label(self.info_panel, text="", **info_value_style)
        self.node_ip_label.grid(row=1, column=1, sticky='w', padx=5, pady=2)

        self.vlan_labels = {}
        for i, vlan in enumerate(['VLAN_100', 'VLAN_200', 'VLAN_300', 'VLAN_400'], start=2):
            tk.Label(self.info_panel, text=f"{vlan}:", **info_label_style).grid(row=i, column=0, sticky='w', padx=5, pady=2)
            self.vlan_labels[vlan] = tk.Label(self.info_panel, text="-", **info_value_style)
            self.vlan_labels[vlan].grid(row=i, column=1, sticky='w', padx=5, pady=2)
        
        self.toggle_mode() # sets to Operator mode on startup
        self.hide_legend_on_start = tk.BooleanVar(value=False)
        self.load_legend_state()
        self.display_legend()
        self.load_last_file() 

        root.protocol("WM_DELETE_WINDOW", self.on_close)

    def show_help(self, event=None):
        help_window = tk.Toplevel(self.root)
        help_window.title("Help - Keyboard Shortcuts and Functions")
        help_window.geometry("600x400")

        text_area = tk.Text(help_window, wrap="word", font="Helvetica 10", state="disabled")
        text_area.pack(expand=True, fill="both", padx=10, pady=10)

        help_text = """
        Keyboard Shortcuts and Functions:

        \nOperator Mode:
        - Left click on Node: Ping! - Node will change colour depending on response
        - Left click drag Node: Move node
        - Right Click on Node: Open context menu for node-specific operations
        - 'Save': Save the current network state
        - 'Load': Load a saved network state
        - 'Who am I?': Identify and highlight the node where this program is running
        - 'Ping All': Ping all nodes and update their status
        - 'Clear Status': Reset the status of all nodes

        \nConfiguration Mode:
        - Double Left Click: Create a node
        - Shift + Double Left Click: Create a sticky note
        - Middle Click: Create a connection between nodes
        - Shift + Middle Click: Remove a connection
        - Right Click on Node: Open context menu for additional options (Edit, Delete, etc.)
        """

        text_area.config(state="normal")
        text_area.insert("1.0", help_text)
        text_area.tag_add("bold", "5.0", "5.end")
        text_area.tag_add("bold", "15.0", "15.end")
        text_area.tag_config("bold", font="Helvetica 10 bold")
        text_area.config(state="disabled")

    def toggle_mode(self):
        if self.mode == "Operator":
            self.mode = "Configuration"
            self.mode_button.config(text='Configuration Mode', bg=ColorConfig.BUTTON_CONFIGURATION_MODE)
            # Enable functionalities for Configuration mode
            self.canvas.bind('<Double-1>', self.create_node)
            self.canvas.bind('<B1-Motion>', self.move_node)
            self.canvas.bind('<Shift-Double-1>', self.create_sticky_note)
            self.canvas.bind('<Button-2>', self.create_connection)
            
        else:
            self.mode = "Operator"
            self.mode_button.config(text='Operator Mode', bg=ColorConfig.BUTTON_BG)
            # Disable functionalities for Operator mode
            self.canvas.unbind('<Double-1>')
            self.canvas.unbind('<B1-Motion>')
            self.canvas.unbind('<Shift-Double-1>')
            self.canvas.unbind('<Button-2>')

    def zoom_in(self, event=None):
        self.canvas.scale("all", self.canvas.winfo_width()/2, self.canvas.winfo_height()/2, 1.1, 1.1)

    def zoom_out(self, event=None):
        self.canvas.scale("all", self.canvas.winfo_width()/2, self.canvas.winfo_height()/2, 0.9, 0.9)

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

    def update_vlan_visibility(self):
        for node in self.nodes:
            # Determine if the node should be visible or greyed out
            should_be_visible = any(self.vlan_visibility[vlan].get() for vlan in ['VLAN_100', 'VLAN_200', 'VLAN_300', 'VLAN_400'] if getattr(node, vlan))
            node_color = ColorConfig.NODE_DEFAULT if should_be_visible else ColorConfig.NODE_GREYED_OUT
            self.canvas.itemconfigure(node.shape, fill=node_color)

    def update_vlan_colors(self, node, ping_results):
        
        for i, vlan in enumerate(['VLAN_100', 'VLAN_200', 'VLAN_300', 'VLAN_400']):
            # Only update if the node has an IP for this VLAN
            if getattr(node, vlan):
                color = "green" if ping_results[i] else "red"
                self.vlan_labels[vlan].config(bg=color)
            else:
                # Reset the color if there is no IP for this VLAN
                self.vlan_labels[vlan].config(bg=ColorConfig.INFO_PANEL_BG)


    def display_legend(self):
        if not self.hide_legend_on_start.get():
        
            # Create a Toplevel window
            legend_window = tk.Toplevel(self.root)
            legend_window.title("")
            legend_window.transient(self.root)  # Make the new window stay on top of the main window
            legend_window.grab_set()  # Modal: input to this window only until closed
            legend_window.iconbitmap('favicon.ico')

            # Load the legend image
            legend_image_path = "legend.png"  
            img = Image.open(legend_image_path)
            photo_img = ImageTk.PhotoImage(img)

            # Create a Label with the image
            img_label = tk.Label(legend_window, image=photo_img)
            img_label.image = photo_img  # Keep a reference to the PhotoImage object
            img_label.pack()

            # Checkbox to hide the legend window on next startup
            hide_legend_checkbox = tk.Checkbutton(legend_window, text="Hide this window on next startup", var=self.hide_legend_on_start)
            hide_legend_checkbox.pack(pady=10)

            # This callback closes the legend window
            def close_legend(event):
                legend_window.destroy()

            # Center the window on the screen
            self.center_window_on_screen(legend_window)
            
    def save_legend_state(self):
        with open("legend_state.txt", "w") as f:
            f.write(str(self.hide_legend_on_start.get()))

    def load_legend_state(self):
        try:
            with open("legend_state.txt", "r") as f:
                state = f.read().strip().lower() == 'true'
                self.hide_legend_on_start.set(state)
        except FileNotFoundError:
            pass

    def on_close(self):
        self.save_legend_state()  # Save the state of the legend window
        self.root.destroy()

    def center_window_on_screen(self, window):
        window.update_idletasks()  # Update "requested size" from geometry manager
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    def on_node_select(self, node):
        # Reset the previous selected node's appearance
        if self.previous_selected_node:
            self.canvas.itemconfig(self.previous_selected_node.shape, outline=ColorConfig.NODE_OUTLINE_DEFAULT, width=2)

        # Update the appearance of the current selected node
        self.canvas.itemconfig(node.shape, outline=ColorConfig.NODE_HIGHLIGHT, width=4)  # orange outline with a width of 4

        # Reset VLAN label colors immediately when a new node is selected
        for vlan in ['VLAN_100', 'VLAN_200', 'VLAN_300', 'VLAN_400']:
            self.vlan_labels[vlan].config(bg=ColorConfig.INFO_PANEL_BG)

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
             
    def move_node(self, event):
        if not event.state & 0x001:
            if self.selected_node:
                self.selected_node.update_position(event.x, event.y)
            else:
                for node in self.nodes:
                    if self.canvas.find_withtag(tk.CURRENT) == node.shape or self.canvas.find_withtag(tk.CURRENT) == node.text:
                        self.selected_node = node
                        break

    def add_node(self):
        name = simpledialog.askstring('Node Name', 'Enter node name:', parent=self.root)
        ip = simpledialog.askstring('Node IP Address', 'Enter node IP address:', parent=self.root)
        if name and ip:
            x, y = 50, 50
            node = NetworkNode(self.canvas, name, ip, x, y)
            self.nodes.append(node)

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
        sticky_bgs = self.canvas.find_withtag("sticky_note_bg")  # Assuming a tag is set for sticky note backgrounds
        for bg in sticky_bgs:
            self.canvas.delete(bg)
            
    def clear_node_status(self):
        # Set the node color of all nodes to NODE_DEFAULT.
        for node in self.nodes:
            self.canvas.itemconfig(node.shape, fill=ColorConfig.NODE_DEFAULT)
            
    def ping_all(self):
        for node in self.nodes:
            node.ping()
    
    def create_sticky_note(self, event=None):
        if self.mode == "Configuration":
            text = simpledialog.askstring('Sticky Note', 'Enter note text:', parent=self.root)
            if text:
                x, y = event.x, event.y if event else (50, 50)
                StickyNote(self.canvas, text, x, y)
        else:
                print("Not in configuration mode")
                
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

                            print(f"Connection between {connection.node1.name} and {connection.node2.name} removed")
                            return  # Exit after removing connection
                print("Clicked item is not a connection line")
            else:
                print("No item clicked for removal")
        else:
            print("Not in configuration mode")

    def save_network_state(self):
        state = {'nodes': [], 'connections': []}
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

        # Save connections
        lines_seen = set()  # To avoid duplicates
        for node in self.nodes:
            for conn in node.connections:
                if conn not in lines_seen:
                    connection_data = {
                        'from': self.nodes.index(conn.node1),
                        'to': self.nodes.index(conn.node2),
                        'label': conn.label  # Save the label of the connection
                    }
                    state['connections'].append(connection_data)
                    lines_seen.add(conn)

        # Prompt user for file location and save the JSON file
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(state, f, indent=4)    

    def load_network_state_from_path(self, file_path):
        with open(file_path, 'r') as f:
            self.clear_current_loaded()  # Clear existing nodes, connections, and labels
            state = json.load(f)
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

    def load_network_state(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'r') as f:
                self.clear_current_loaded()  # Clear existing nodes, connections and labels
                state = json.load(f)
            
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

    def save_last_file_path(self, file_path):
        with open('last_file_path.txt', 'w') as f:
            f.write(file_path)

    def load_last_file(self):
        try:
            with open('last_file_path.txt', 'r') as f:
                last_file_path = f.read().strip()
                if os.path.exists(last_file_path):
                    self.load_network_state_from_path(last_file_path)
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

    def flash_node(self, node, times, original_color=ColorConfig.NODE_DEFAULT, flash_color=ColorConfig.NODE_HOST):
        if times > 0:
            next_color = flash_color if self.canvas.itemcget(node.shape, "fill") == original_color else original_color
            self.canvas.itemconfig(node.shape, fill=next_color)
            self.canvas.after(400, lambda: self.flash_node(node, times - 1))
        else:
            self.canvas.itemconfig(node.shape, fill=flash_color)                 
      
if __name__ == "__main__":
    root = tk.Tk()
    root.title("NodeSailor")
    gui = NetworkMapGUI(root)
    root.mainloop()