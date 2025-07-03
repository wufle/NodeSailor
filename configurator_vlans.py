import tkinter as tk
from colors import ColorConfig

def edit_vlan_labels_window(gui):
    # Destroy any existing VLAN editor window before opening a new one
    if getattr(gui, 'vlan_label_editor', None) and gui.vlan_label_editor.winfo_exists():
        gui.vlan_label_editor.destroy()
        gui.vlan_label_editor = None

    # Withdraw the legend window if it exists
    if getattr(gui, 'legend_window', None) and gui.legend_window.winfo_exists():
        gui.legend_window.withdraw()

    def close_vlan_editor():
        try:
            gui.vlan_label_editor.grab_release()
        except:
            pass
        gui.vlan_label_editor.destroy()
        gui.vlan_label_editor = None
        gui.regain_focus()  # Restore focus to the main window

    gui.vlan_label_editor, content = gui.create_popup("Edit VLANs", 370, 350, on_close=close_vlan_editor, grab=False)

    entries = {}

    vlan_frame = tk.Frame(content, bg=ColorConfig.current.FRAME_BG)
    vlan_frame.grid(row=0, column=0, columnspan=3, sticky="nsew")
    
    content.grid_rowconfigure(0, weight=1)  # vlan_frame row
    content.grid_rowconfigure(2, weight=0)  # button_frame row
    content.grid_columnconfigure(0, weight=1)
    
    # Helper to update window height dynamically (for refresh/reorder)
    def update_vlan_window_height():
        min_height = 100
        max_height = 1000
        base_height = 120  # space for controls/buttons
        per_vlan = 36      # per VLAN row
        n = len(gui.vlan_label_order)
        height = min(max(min_height, base_height + per_vlan * n), max_height)
        gui.vlan_label_editor.geometry(f"370x{height}")

    def refresh_vlan_entries():
        # Clear current widgets in vlan_frame
        for widget in vlan_frame.winfo_children():
            widget.destroy()
        entries.clear()

        # "Show All" button to reset visibility
        def show_all_nodes():
            for node in getattr(gui, "nodes", []):
                gui.canvas.itemconfigure(node.shape, state=tk.NORMAL)
                gui.canvas.itemconfigure(node.text, state=tk.NORMAL)

        # Use custom VLAN order for display
        for i, vlan in enumerate(gui.vlan_label_order):
            row_idx = i + 1  # Offset by 1 for Show All button
            tk.Label(vlan_frame, text=vlan + ":", anchor="e",
                    bg=ColorConfig.current.FRAME_BG,
                    fg=ColorConfig.current.BUTTON_TEXT,
                    font=('Helvetica', 10))\
                .grid(row=row_idx, column=0, padx=10, pady=5, sticky="e")
            entry = tk.Entry(vlan_frame, bg=ColorConfig.current.ENTRY_FOCUS_BG, fg=ColorConfig.current.ENTRY_TEXT, insertbackground=ColorConfig.current.ENTRY_TEXT)
            entry.insert(0, gui.vlan_label_names[vlan])
            entry.grid(row=row_idx, column=1, padx=10, pady=5)
            entries[vlan] = entry

            def make_remove(vlan_name):
                return lambda: remove_vlan(vlan_name)
            remove_btn = tk.Button(vlan_frame, text="Remove", command=make_remove(vlan),
                                  bg=ColorConfig.current.BUTTON_BG,
                                  fg=ColorConfig.current.BUTTON_TEXT,
                                  activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
                                  activeforeground=ColorConfig.current.BUTTON_ACTIVE_TEXT,
                                  font=('Helvetica', 9))
            remove_btn.grid(row=row_idx, column=4, padx=5, pady=5)

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
            up_btn.grid(row=row_idx, column=2, padx=2, pady=5)
            down_btn = tk.Button(vlan_frame, text="↓", command=make_move_down(i),
                                 bg=ColorConfig.current.BUTTON_BG,
                                 fg=ColorConfig.current.BUTTON_TEXT,
                                 activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
                                 activeforeground=ColorConfig.current.BUTTON_ACTIVE_TEXT,
                                 font=('Helvetica', 9), width=2)
            down_btn.grid(row=row_idx, column=3, padx=2, pady=5)

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
        update_vlan_window_height()

    # Populate VLAN entries before showing window and setting geometry
    refresh_vlan_entries()
    update_vlan_window_height()
    gui.vlan_label_editor.deiconify()
    gui.vlan_label_editor.update_idletasks()

    def move_vlan(idx, direction):
        new_idx = idx + direction
        if 0 <= new_idx < len(gui.vlan_label_order):
            gui.vlan_label_order[idx], gui.vlan_label_order[new_idx] = (
                gui.vlan_label_order[new_idx], gui.vlan_label_order[idx]
            )
            refresh_vlan_entries()
    # Ensure the window is wide enough for all buttons
    gui.vlan_label_editor.minsize(370, 350)
    # Remove static geometry setting; handled dynamically

    def add_vlan():
        # Find next available VLAN name
        base = "VLAN_"
        idx = 1
        while f"{base}{idx}" in gui.vlan_label_names:
            idx += 1
        new_vlan = f"{base}{idx}"
        gui.vlan_label_names[new_vlan] = ""
        gui.vlan_label_order.append(new_vlan)
        refresh_vlan_entries()

    def remove_vlan(vlan):
        if vlan in gui.vlan_label_names:
            del gui.vlan_label_names[vlan]
            if vlan in gui.vlan_label_order:
                gui.vlan_label_order.remove(vlan)
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
        to_remove = [vlan for vlan in gui.vlan_label_names if vlan not in entries]
        for vlan in to_remove:
            del gui.vlan_label_names[vlan]
            if vlan in gui.vlan_label_order:
                gui.vlan_label_order.remove(vlan)
        # Update/add VLANs
        # Track VLANs before update
        prev_vlans = set(gui.vlan_label_names.keys())
        for vlan, entry in entries.items():
            gui.vlan_label_names[vlan] = entry.get()
        # Detect new VLANs (present now, not before)
        new_vlans = set(gui.vlan_label_names.keys()) - prev_vlans
        # Add new VLANs to all nodes' in-memory vlans structure
        for vlan in new_vlans:
            for node in getattr(gui, "nodes", []):
                # Assume node.vlans is a dict; skip if already present
                if hasattr(node, "vlans"):
                    if vlan not in node.vlans:
                        node.vlans[vlan] = {}  # or appropriate default value
        for vlan, label in gui.vlan_title_labels.items():
            if vlan in gui.vlan_label_names:
                label.config(text=gui.vlan_label_names[vlan] + ":")
        # Refresh info panel VLANs to reflect changes
        for node in getattr(gui, "nodes", []):
            gui.refresh_info_panel_vlans(node, {'font': ('Helvetica', 10), 'bg': ColorConfig.current.INFO_NOTE_BG, 'fg': ColorConfig.current.INFO_TEXT, 'anchor': 'w'}, gui.info_value_style)
        close_vlan_editor()
        gui.save_network_state()

    button_frame = tk.Frame(content, bg=ColorConfig.current.FRAME_BG)
    button_frame.grid(row=2, column=0, columnspan=3, pady=10)
    tk.Button(button_frame, text="Save", command=save_labels,
            bg=ColorConfig.current.BUTTON_BG,
            fg=ColorConfig.current.BUTTON_TEXT,
            activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
            activeforeground=ColorConfig.current.BUTTON_ACTIVE_TEXT,
            font=('Helvetica', 10)).pack()

    final_height = gui.vlan_label_editor.winfo_height()
    gui.vlan_label_editor.after(1, lambda: gui.vlan_label_editor.geometry(f"370x{final_height}"))
