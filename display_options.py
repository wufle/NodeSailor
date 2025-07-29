import tkinter as tk
from colors import ColorConfig

def show_display_options_window(gui):
    # Store state in RAM for session persistence only
    if not hasattr(gui, "display_options_state"):
        gui.display_options_state = {}

    state = gui.display_options_state

    # Destroy any existing display options window before opening a new one
    if getattr(gui, 'display_options_window', None) and gui.display_options_window.winfo_exists():
        gui.display_options_window.destroy()
        gui.display_options_window = None

    # Withdraw the legend window if it exists
    if getattr(gui, 'legend_window', None) and gui.legend_window.winfo_exists():
        gui.legend_window.withdraw()

    def close_display_options_window():
        save_state()
        try:
            gui.display_options_window.grab_release()
        except:
            pass
        gui.display_options_window.destroy()
        gui.display_options_window = None
        gui.regain_focus()  # Restore focus to the main window

    gui.display_options_window, content = gui.create_popup("Display Options", 250, 400, on_close=close_display_options_window, grab=False)

    options_frame = tk.Frame(content, bg=ColorConfig.current.FRAME_BG)
    options_frame.grid(row=0, column=0, columnspan=3, sticky="nsew")

    # BooleanVars for checkboxes (except VLANs)
    conn_var = tk.BooleanVar(value=state.get("show_connections", True))
    conn_label_var = tk.BooleanVar(value=state.get("show_connection_labels", True))
    notes_var = tk.BooleanVar(value=state.get("show_notes", True))
    groups_var = tk.BooleanVar(value=state.get("show_groups", True))

    # Node/Text size slider state
    node_size_var = tk.IntVar(value=state.get("node_size", 14))  # Default size 14

    # VLAN checkboxes state
    vlan_vars = {}

    def save_state():
        state["show_connections"] = conn_var.get()
        state["show_connection_labels"] = conn_label_var.get()
        state["show_notes"] = notes_var.get()
        state["show_groups"] = groups_var.get()
        state["vlans"] = {vlan: var.get() for vlan, var in vlan_vars.items()}

    def update_display():
        save_state()
        # Sync GUI toggles for connection and label visibility
        gui.show_connections = conn_var.get()
        gui.show_connection_labels = conn_label_var.get()

        # Update node and text size
        node_size = node_size_var.get()
        state["node_size"] = node_size
        for node in getattr(gui, "nodes", []):
            try:
                node.font.configure(size=node_size)
                node.adjust_node_size(node_size)
            except Exception:
                pass

        # VLANs (nodes): Show node if any checked VLAN matches
        checked_vlans = [vlan for vlan, var in vlan_vars.items() if var.get()]
        for node in getattr(gui, "nodes", []):
            show = False
            if hasattr(node, "vlans"):
                for vlan in checked_vlans:
                    if node.vlans.get(vlan):
                        show = True
                        break
            state_ = tk.NORMAL if show else tk.HIDDEN
            gui.canvas.itemconfigure(node.shape, state=state_)
            gui.canvas.itemconfigure(node.text, state=state_)
        # Connections: Redraw all connections to ensure correct visibility
        for node in getattr(gui, "nodes", []):
            for conn in getattr(node, "connections", []):
                conn.draw_line()
                conn.update_label()
        # Sticky Notes

        # Ensure nodes are always on top after redraw
        if hasattr(gui, "raise_all_nodes"):
            gui.raise_all_nodes()
        for note in getattr(gui, "stickynotes", []):
            note_state = tk.NORMAL if notes_var.get() else tk.HIDDEN
            gui.canvas.itemconfigure(note.note, state=note_state)
            if hasattr(note, "bg_shape"):
                gui.canvas.itemconfigure(note.bg_shape, state=note_state)
        # Groups
        if hasattr(gui, "group_manager"):
            for group in getattr(gui.group_manager, "groups", []):
                group_state = tk.NORMAL if groups_var.get() else tk.HIDDEN
                gui.canvas.itemconfigure(group.rectangle, state=group_state)
                gui.canvas.itemconfigure(group.text, state=group_state)

    # Checkboxes (no VLANs/global)
    tk.Checkbutton(options_frame, text="Show Connections", variable=conn_var, command=update_display, bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT, selectcolor=ColorConfig.current.FRAME_BG).grid(row=0, column=0, sticky="w", padx=10, pady=5, columnspan=2)
    tk.Checkbutton(options_frame, text="Show Connection Labels", variable=conn_label_var, command=update_display, bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT, selectcolor=ColorConfig.current.FRAME_BG).grid(row=1, column=0, sticky="w", padx=10, pady=5, columnspan=2)
    tk.Checkbutton(options_frame, text="Show Sticky Notes", variable=notes_var, command=update_display, bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT, selectcolor=ColorConfig.current.FRAME_BG).grid(row=2, column=0, sticky="w", padx=10, pady=5, columnspan=2)
    tk.Checkbutton(options_frame, text="Show Groups", variable=groups_var, command=update_display, bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT, selectcolor=ColorConfig.current.FRAME_BG).grid(row=3, column=0, sticky="w", padx=10, pady=5, columnspan=2)

    # Node/Text Size Slider
    tk.Label(options_frame, text="Node/Text Size", bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT).grid(row=4, column=0, sticky="w", padx=10, pady=(10, 0), columnspan=2)
    node_size_slider = tk.Scale(
        options_frame,
        from_=8, to=32, orient=tk.HORIZONTAL,
        variable=node_size_var,
        command=lambda v: update_display(),
        bg=ColorConfig.current.FRAME_BG,
        fg=ColorConfig.current.BUTTON_TEXT,
        troughcolor=ColorConfig.current.BUTTON_BG,
        highlightbackground=ColorConfig.current.FRAME_BG,
        activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
        sliderrelief=tk.RAISED,
        length=180,
        showvalue=True,
        resolution=1
    )
    node_size_slider.grid(row=5, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))

    # VLAN section (checkboxes for each VLAN)
    vlan_frame = tk.Frame(options_frame, bg=ColorConfig.current.FRAME_BG)
    vlan_frame.grid(row=6, column=0, columnspan=3, sticky="nsew")

    def update_vlan_window_height():
        min_height = 100
        max_height = 1000
        base_height = 300 
        per_vlan = 36      # per VLAN row
        n = len(gui.vlan_label_order)
        height = min(max(min_height, base_height + per_vlan * n), max_height)
        gui.display_options_window.geometry(f"250x{height}")

    def refresh_vlan_entries():
        # Clear current widgets in vlan_frame
        for widget in vlan_frame.winfo_children():
            widget.destroy()
        vlan_vars.clear()

        # Add header label before VLAN checkboxes
        header_label = tk.Label(
            vlan_frame,
            text="Toggle VLAN Visibility:",
            bg=ColorConfig.current.FRAME_BG,
            fg=ColorConfig.current.BUTTON_TEXT,
            font=('Helvetica', 11)
        )
        header_label.grid(row=0, column=0, padx=10, pady=(10, 1), sticky="w")

        # Use custom VLAN order for display
        for i, vlan in enumerate(gui.vlan_label_order):
            row_idx = i + 1  # Offset by 1 to account for header
            vlan_vars[vlan] = tk.BooleanVar(value=state.get("vlans", {}).get(vlan, True))
            def vlan_callback(vlan_name=vlan):
                update_display()
                save_state()
            tk.Checkbutton(
                vlan_frame,
                text=gui.vlan_label_names.get(vlan, vlan),
                variable=vlan_vars[vlan],
                command=vlan_callback,
                bg=ColorConfig.current.FRAME_BG,
                fg=ColorConfig.current.BUTTON_TEXT,
                selectcolor=ColorConfig.current.FRAME_BG,
                font=('Helvetica', 10)
            ).grid(row=row_idx, column=0, padx=10, pady=5, sticky="w")
        update_vlan_window_height()

    refresh_vlan_entries()
    update_vlan_window_height()
    gui.display_options_window.deiconify()
    gui.display_options_window.update_idletasks()
    gui.display_options_window.minsize(250, 450)
    final_height = gui.display_options_window.winfo_height()
    gui.display_options_window.after(1, lambda: gui.display_options_window.geometry(f"250x{final_height}"))