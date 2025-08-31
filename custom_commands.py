import tkinter as tk

def manage_custom_commands(gui_self):
    ColorConfig = gui_self.ColorConfig if hasattr(gui_self, "ColorConfig") else __import__("colors").ColorConfig
    if getattr(gui_self, 'custom_cmd_window', None) and gui_self.custom_cmd_window.winfo_exists():
        gui_self.custom_cmd_window.lift()
        return

    win, content = gui_self.create_popup("Manage Custom Commands", 900, 600, on_close=gui_self.make_popup_closer("custom_cmd_window"), grab=False)
    gui_self.custom_cmd_window = win

    listbox = tk.Listbox(content, width=50, height=10,
                            bg=ColorConfig.current.ROW_BG_EVEN,
                            fg=ColorConfig.current.ENTRY_TEXT,
                            selectbackground=ColorConfig.current.ENTRY_FOCUS_BG,
                            selectforeground=ColorConfig.current.BUTTON_TEXT)
    listbox.pack(pady=10, padx=10)
    gui_self.custom_commands_listbox = listbox

    for name in gui_self.custom_commands.keys():
        listbox.insert(tk.END, name)

    def on_command_select(event):
        selection = listbox.curselection()
        if selection:
            name = listbox.get(selection[0])
            cmd_info = gui_self.custom_commands.get(name, "")
            if isinstance(cmd_info, dict):
                cmd = cmd_info.get("template", "")
                applicable_nodes = cmd_info.get("applicable_nodes", None)
            else:
                cmd = cmd_info
                applicable_nodes = None
            name_entry.delete(0, tk.END)
            cmd_entry.delete("1.0", tk.END)
            name_entry.insert(0, name)
            cmd_entry.insert("1.0", cmd)
            if applicable_nodes is None:
                applicability_var.set(True)
                for n in node_names:
                    node_vars[n].set(False)
            else:
                applicability_var.set(False)
                for n in node_names:
                    node_vars[n].set(n in applicable_nodes)

    listbox.bind("<<ListboxSelect>>", on_command_select)

    frame = tk.Frame(content, bg=ColorConfig.current.FRAME_BG)
    frame.pack(pady=10, padx=20, fill=tk.X)
    
    label_args = {'bg': ColorConfig.current.FRAME_BG, 'fg': ColorConfig.current.BUTTON_TEXT, 'font': ('Helvetica', 10)}
    entry_args = {'bg': ColorConfig.current.ENTRY_FOCUS_BG, 'fg': ColorConfig.current.ENTRY_TEXT, 'insertbackground': ColorConfig.current.ENTRY_TEXT}
    
    tk.Label(frame, text="Command Name:", **label_args).grid(row=0, column=0, sticky='w', pady=(0, 8))
    name_entry = tk.Entry(frame, width=40, font=('Helvetica', 10), **entry_args)
    name_entry.grid(row=0, column=1, padx=5, pady=(0, 8), sticky='ew')
    
    tk.Label(frame, text="Command Template:", **label_args).grid(row=1, column=0, sticky='nw')
    cmd_entry = tk.Text(frame, width=80, height=6, font=('Helvetica', 10), **entry_args)
    cmd_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
    
    frame.grid_columnconfigure(1, weight=1)

    # Applicability controls
    applicability_var = tk.BooleanVar(value=True)
    applicability_chk = tk.Checkbutton(
        frame, text="Applicable to all nodes", variable=applicability_var,
        bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT, font=('Helvetica', 10),
        selectcolor=ColorConfig.current.FRAME_BG
    )
    applicability_chk.grid(row=2, column=0, sticky='w', pady=(8, 0), columnspan=2)
    
    # Node selection scrollable frame (hidden by default)
    node_names = [n.name for n in getattr(gui_self, "nodes", [])]
    node_vars = {n: tk.BooleanVar(value=False) for n in node_names}
    node_select_label = tk.Label(frame, text="Select applicable nodes:", **label_args)

    node_select_canvas = tk.Canvas(frame, width=320, height=120, bg=ColorConfig.current.ENTRY_FOCUS_BG, highlightthickness=0)
    node_select_scrollbar = tk.Scrollbar(
        frame,
        orient="vertical",
        command=node_select_canvas.yview,
        bg=ColorConfig.current.FRAME_BG,  # scrollbar background
        troughcolor=ColorConfig.current.ENTRY_FOCUS_BG,  # trough color
        activebackground=ColorConfig.current.FRAME_BG,  # slider active color
        highlightbackground=ColorConfig.current.BORDER_COLOR,  # border color
        highlightcolor=ColorConfig.current.BORDER_COLOR,  # border color when focused
        borderwidth=2  # slightly thicker border for dark mode
    )
    node_select_inner_frame = tk.Frame(node_select_canvas, bg=ColorConfig.current.ENTRY_FOCUS_BG)
    node_select_inner_frame_id = node_select_canvas.create_window((0, 0), window=node_select_inner_frame, anchor="nw")
    node_select_canvas.configure(yscrollcommand=node_select_scrollbar.set)

    # Mouse wheel support for Canvas scrolling
    def _on_mousewheel(event):
        if event.delta:
            node_select_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        elif event.num == 4:  # Linux scroll up
            node_select_canvas.yview_scroll(-1, "units")
        elif event.num == 5:  # Linux scroll down
            node_select_canvas.yview_scroll(1, "units")

    node_select_canvas.bind_all("<MouseWheel>", _on_mousewheel)      # Windows/macOS
    node_select_canvas.bind_all("<Button-4>", _on_mousewheel)        # Linux scroll up
    node_select_canvas.bind_all("<Button-5>", _on_mousewheel)        # Linux scroll down

    node_vars = {}
    for idx, name in enumerate(node_names):
        var = tk.BooleanVar(value=False)
        node_vars[name] = var
        cb = tk.Checkbutton(node_select_inner_frame, text=name, variable=var,
                            bg=ColorConfig.current.ENTRY_FOCUS_BG, fg=ColorConfig.current.ENTRY_TEXT,
                            font=('Helvetica', 10), anchor="w", selectcolor=ColorConfig.current.FRAME_BG)
        cb.pack(fill="x", padx=2, pady=1)

    def _on_frame_configure(event):
        node_select_canvas.configure(scrollregion=node_select_canvas.bbox("all"))
    node_select_inner_frame.bind("<Configure>", _on_frame_configure)
    
    def toggle_node_select(*_):
        print(f"[DEBUG] toggle_node_select: applicability_var={applicability_var.get()}")
        if applicability_var.get():
            print("[DEBUG] Node selection panel hidden")
            node_select_label.grid_remove()
            node_select_canvas.grid_remove()
            node_select_scrollbar.grid_remove()
        else:
            print("[DEBUG] Node selection panel shown")
            node_select_label.grid(row=3, column=0, sticky='nw')
            node_select_canvas.grid(row=3, column=1, padx=(5,0), pady=5, sticky='ew')
            node_select_scrollbar.grid(row=3, column=2, sticky='ns', padx=(0,5), pady=5)
    
    applicability_var.trace_add("write", toggle_node_select)
    toggle_node_select()
    
    btn_frame = tk.Frame(content, bg=ColorConfig.current.FRAME_BG)
    btn_frame.pack(pady=10)

    def new_command():
        name_entry.delete(0, tk.END)
        cmd_entry.delete("1.0", tk.END)

    def delete_command():
        selection = listbox.curselection()
        if selection:
            name = listbox.get(selection[0])
            del gui_self.custom_commands[name]
            listbox.delete(selection[0])
            name_entry.delete(0, tk.END)
            cmd_entry.delete("1.0", tk.END)

    def save_command():
        name = name_entry.get().strip()
        cmd = cmd_entry.get("1.0", tk.END).strip()
        if applicability_var.get():
            applicable_nodes = None
        else:
            applicable_nodes = [n for n in node_names if node_vars[n].get()]
        if name and cmd:
            gui_self.custom_commands[name] = {
                "template": cmd,
                "applicable_nodes": applicable_nodes
            }
            # Update listbox if new
            if name not in listbox.get(0, tk.END):
                listbox.insert(tk.END, name)

    btn_style = {
        'bg': ColorConfig.current.BUTTON_BG,
        'fg': ColorConfig.current.BUTTON_TEXT,
        'activebackground': ColorConfig.current.BUTTON_ACTIVE_BG,
        'activeforeground': ColorConfig.current.BUTTON_ACTIVE_TEXT,
        'font': ('Helvetica', 10),
        'padx': 5,
        'pady': 2
    }

    tk.Button(btn_frame, text="New", command=new_command, **btn_style).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Delete", command=delete_command, **btn_style).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Save", command=save_command, **btn_style).pack(side=tk.LEFT, padx=5)

    tk.Label(content, text="""
                
Custom Commands:
- Use placeholders like {ip}, {name}, {file}, {web}, {rdp}, {vlan100}, etc.
- {ip} defaults to the first non-empty VLAN address
- Example: ping {ip} -t
""", justify=tk.LEFT, bg=ColorConfig.current.FRAME_BG,
            fg=ColorConfig.current.INFO_TEXT, font=('Helvetica', 9),
            wraplength=380).pack(pady=10, padx=10)

    gui_self.fix_window_geometry(gui_self.custom_cmd_window, 600, 550)