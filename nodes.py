from colors import ColorConfig
import tkinter as tk
from tkinter import messagebox, simpledialog, font
import subprocess
import platform
import os
import webbrowser
import threading

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
        gui = self.canvas.gui
        if gui and hasattr(gui, "list_editor_xy_fields"):
            xy_fields = gui.list_editor_xy_fields.get(self)
            if xy_fields:
                try:
                    x_entry, y_entry = xy_fields
                    if x_entry.winfo_exists():
                        x_entry.delete(0, tk.END)
                        x_entry.insert(0, str(int(self.x)))
                    if y_entry.winfo_exists():
                        y_entry.delete(0, tk.END)
                        y_entry.insert(0, str(int(self.y)))
                except tk.TclError:
                    pass  # Ignore if widget is destroyed

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
        gui = self.canvas.gui
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
            response = subprocess.run(command, creationflags=subprocess.CREATE_NO_WINDOW, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
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
                gui = self.canvas.gui
                self.canvas.after(0, lambda: gui.update_vlan_colors(self, results))

        def ping_all_vlans():
            vlan_ips = [self.VLAN_100, self.VLAN_200, self.VLAN_300, self.VLAN_400]
            ips_to_ping = [ip for ip in vlan_ips if ip]  # Filter out empty strings
            results = [run_ping(ip) for ip in ips_to_ping] if ips_to_ping else [False]
            self.canvas.after(0, update_ui, results)

        threading.Thread(target=ping_all_vlans).start()

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

    # Class variable to track the globally open context menu
    open_context_menu = None

    def show_context_menu(self, event):
        gui = self.canvas.gui
        
        # Ensure only one context menu is open at a time across all nodes
        if NetworkNode.open_context_menu is not None:
            try:
                NetworkNode.open_context_menu.destroy()
            except Exception:
                pass
            NetworkNode.open_context_menu = None

        context_menu = tk.Toplevel(self.canvas)
        context_menu.wm_overrideredirect(True)  # Removes OS borders and title bar
        context_menu.wm_geometry(f"+{event.x_root}+{event.y_root}")
        NetworkNode.open_context_menu = context_menu

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
            if isinstance(cmd, dict):
                template = cmd.get("template", "")
                applicable_nodes = cmd.get("applicable_nodes", None)
                if applicable_nodes is not None and self.name not in applicable_nodes:
                    continue
            else:
                template = cmd
            options.append((name, lambda c=template: self.execute_custom_command(c)))

        def destroy_menu():
            try:
                context_menu.unbind("<FocusOut>")
                context_menu.unbind("<Escape>")
                for btn in menu_frame.winfo_children():
                    btn.unbind("<Enter>")
                    btn.unbind("<Leave>")
                context_menu.destroy()
            except tk.TclError:
                pass  # Ignore if window is already destroyed
            # Reset the class-level reference
            NetworkNode.open_context_menu = None

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
        gui = self.canvas.gui
        gui.open_node_window(node=self)

    def open_remote_desktop(self):
        if not self.remote_desktop_address:
            messagebox.showinfo("Info", "No remote desktop address set for this node.")
            return
        if platform.system() == "Windows":
            # Use the Windows Remote Desktop Connection command (mstsc)
            subprocess.Popen(f'mstsc /v:{self.remote_desktop_address}', shell=True)
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

        threading.Thread(target=try_open, daemon=True).start()

    def open_web_browser(self):
        if not self.web_config_url:
            messagebox.showinfo("Info", "No web config URL set for this node.")
            return
        webbrowser.open(self.web_config_url, new=2)  # Open URL in a new tab, if exists
        pass
      
    def delete_node(self):
        gui = self.canvas.gui
        
        if self.connections:
            result = messagebox.askyesno(
                "Delete Node",
                f"'{self.name}' is connected to {len(self.connections)} other node(s).\n\n"
                "Do you want to delete this node and remove all its connections?"
            )
            if not result:
                return
        gui.remove_node(self)

    def execute_custom_command(self, command_template):
        gui = self.canvas.gui
        
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
                import tempfile, os
                with tempfile.NamedTemporaryFile('w', suffix='.bat', delete=False) as bat_file:
                    bat_file.write('@echo off\n')
                    bat_file.write(command)
                    bat_file.write('\n')
                    bat_file.write('start "" cmd /c del "%~f0" >nul 2>&1\n')
                    bat_path = bat_file.name
                subprocess.Popen(f'start cmd /k "{bat_path}"', shell=True)
            else:
                subprocess.Popen(['x-terminal-emulator', '-e', command])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to execute command: {str(e)}")