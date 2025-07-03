import tkinter as tk
from colors import ColorConfig

def show_display_options_window(gui):
    # Destroy any existing display options window before opening a new one
    if getattr(gui, 'display_options_window', None) and gui.display_options_window.winfo_exists():
        gui.display_options_window.destroy()
        gui.display_options_window = None

    # Withdraw the legend window if it exists
    if getattr(gui, 'legend_window', None) and gui.legend_window.winfo_exists():
        gui.legend_window.withdraw()

    def close_display_options_window():
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

    # BooleanVars for checkboxes
    vlan_var = tk.BooleanVar(value=True)
    conn_var = tk.BooleanVar(value=True)
    conn_label_var = tk.BooleanVar(value=True)
    notes_var = tk.BooleanVar(value=True)
    groups_var = tk.BooleanVar(value=True)

    def update_display():
        # VLANs (nodes)
        for node in getattr(gui, "nodes", []):
            state = tk.NORMAL if vlan_var.get() else tk.HIDDEN
            gui.canvas.itemconfigure(node.shape, state=state)
            gui.canvas.itemconfigure(node.text, state=state)
        # Connections
        for node in getattr(gui, "nodes", []):
            for conn in getattr(node, "connections", []):
                gui.canvas.itemconfigure(conn.line, state=tk.NORMAL if conn_var.get() else tk.HIDDEN)
                if hasattr(conn, "label_id") and conn.label_id:
                    gui.canvas.itemconfigure(conn.label_id, state=tk.NORMAL if conn_label_var.get() and conn_var.get() else tk.HIDDEN)
                if hasattr(conn, "label_bg") and conn.label_bg:
                    gui.canvas.itemconfigure(conn.label_bg, state=tk.NORMAL if conn_label_var.get() and conn_var.get() else tk.HIDDEN)
        # Sticky Notes
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

    # Checkboxes
    tk.Checkbutton(options_frame, text="Show VLANs", variable=vlan_var, command=update_display, bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT, selectcolor=ColorConfig.current.FRAME_BG).grid(row=0, column=0, sticky="w", padx=10, pady=5, columnspan=2)
    tk.Checkbutton(options_frame, text="Show Connections", variable=conn_var, command=update_display, bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT, selectcolor=ColorConfig.current.FRAME_BG).grid(row=1, column=0, sticky="w", padx=10, pady=5, columnspan=2)
    tk.Checkbutton(options_frame, text="Show Connection Labels", variable=conn_label_var, command=update_display, bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT, selectcolor=ColorConfig.current.FRAME_BG).grid(row=2, column=0, sticky="w", padx=10, pady=5, columnspan=2)
    tk.Checkbutton(options_frame, text="Show Sticky Notes", variable=notes_var, command=update_display, bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT, selectcolor=ColorConfig.current.FRAME_BG).grid(row=3, column=0, sticky="w", padx=10, pady=5, columnspan=2)
    tk.Checkbutton(options_frame, text="Show Groups", variable=groups_var, command=update_display, bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT, selectcolor=ColorConfig.current.FRAME_BG).grid(row=4, column=0, sticky="w", padx=10, pady=5, columnspan=2)

    # VLAN section (reuse original logic)
    vlan_frame = tk.Frame(options_frame, bg=ColorConfig.current.FRAME_BG)
    vlan_frame.grid(row=5, column=0, columnspan=3, sticky="nsew")

    def update_vlan_window_height():
        min_height = 100
        max_height = 1000
        base_height = 180  # space for controls/buttons
        per_vlan = 36      # per VLAN row
        n = len(gui.vlan_label_order)
        height = min(max(min_height, base_height + per_vlan * n), max_height)
        gui.display_options_window.geometry(f"250x{height}")

    def refresh_vlan_entries():
        # Clear current widgets in vlan_frame
        for widget in vlan_frame.winfo_children():
            widget.destroy()

        # "Show All" button to reset visibility
        def show_all_nodes():
            for node in getattr(gui, "nodes", []):
                gui.canvas.itemconfigure(node.shape, state=tk.NORMAL)
                gui.canvas.itemconfigure(node.text, state=tk.NORMAL)
        show_all_btn = tk.Button(
            vlan_frame, text="Show All Nodes", command=show_all_nodes,
            bg=ColorConfig.current.BUTTON_BG,
            fg=ColorConfig.current.BUTTON_TEXT,
            activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
            activeforeground=ColorConfig.current.BUTTON_ACTIVE_TEXT,
            font=('Helvetica', 9)
        )
        show_all_btn.grid(row=0, column=3, padx=5, pady=5, sticky="e")

        # Use custom VLAN order for display
        for i, vlan in enumerate(gui.vlan_label_order):
            row_idx = i + 1  # Offset by 1 for Show All button
            tk.Label(
                vlan_frame,
                text=gui.vlan_label_names.get(vlan, vlan) + ":",
                anchor="e",
                bg=ColorConfig.current.FRAME_BG,
                fg=ColorConfig.current.BUTTON_TEXT,
                font=('Helvetica', 10)
            ).grid(row=row_idx, column=0, padx=10, pady=5, sticky="e")

            # Toggle visibility button for this VLAN
            def make_toggle_vlan(vlan_name):
                def toggle_nodes():
                    for node in getattr(gui, "nodes", []):
                        # Show node if VLAN is present and non-empty
                        if hasattr(node, "vlans") and node.vlans.get(vlan_name):
                            gui.canvas.itemconfigure(node.shape, state=tk.NORMAL)
                            gui.canvas.itemconfigure(node.text, state=tk.NORMAL)
                        else:
                            gui.canvas.itemconfigure(node.shape, state=tk.HIDDEN)
                            gui.canvas.itemconfigure(node.text, state=tk.HIDDEN)
                return toggle_nodes
            toggle_btn = tk.Button(
                vlan_frame, text="Show Only", command=make_toggle_vlan(vlan),
                bg=ColorConfig.current.BUTTON_BG,
                fg=ColorConfig.current.BUTTON_TEXT,
                activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
                activeforeground=ColorConfig.current.BUTTON_ACTIVE_TEXT,
                font=('Helvetica', 9)
            )
            toggle_btn.grid(row=row_idx, column=3, padx=5, pady=5)
        update_vlan_window_height()

    refresh_vlan_entries()
    update_vlan_window_height()
    gui.display_options_window.deiconify()
    gui.display_options_window.update_idletasks()
    gui.display_options_window.minsize(250, 400)
    final_height = gui.display_options_window.winfo_height()
    gui.display_options_window.after(1, lambda: gui.display_options_window.geometry(f"250x{final_height}"))