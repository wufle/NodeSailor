import tkinter as tk
from colors import ColorConfig

def show_operator_vlans_window(gui):
    # Destroy any existing VLAN window before opening a new one
    if getattr(gui, 'operator_vlan_window', None) and gui.operator_vlan_window.winfo_exists():
        gui.operator_vlan_window.destroy()
        gui.operator_vlan_window = None

    # Withdraw the legend window if it exists
    if getattr(gui, 'legend_window', None) and gui.legend_window.winfo_exists():
        gui.legend_window.withdraw()

    def close_vlan_window():
        try:
            gui.operator_vlan_window.grab_release()
        except:
            pass
        gui.operator_vlan_window.destroy()
        gui.operator_vlan_window = None
        gui.regain_focus()  # Restore focus to the main window

    gui.operator_vlan_window, content = gui.create_popup("View VLANs", 200, 350, on_close=close_vlan_window, grab=False)

    vlan_frame = tk.Frame(content, bg=ColorConfig.current.FRAME_BG)
    vlan_frame.grid(row=0, column=0, columnspan=3, sticky="nsew")

    def update_vlan_window_height():
        min_height = 100
        max_height = 1000
        base_height = 120  # space for controls/buttons
        per_vlan = 36      # per VLAN row
        n = len(gui.vlan_label_order)
        height = min(max(min_height, base_height + per_vlan * n), max_height)
        gui.operator_vlan_window.geometry(f"200x{height}")

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
    gui.operator_vlan_window.deiconify()
    gui.operator_vlan_window.update_idletasks()
    gui.operator_vlan_window.minsize(200, 350)
    final_height = gui.operator_vlan_window.winfo_height()
    gui.operator_vlan_window.after(1, lambda: gui.operator_vlan_window.geometry(f"200x{final_height}"))