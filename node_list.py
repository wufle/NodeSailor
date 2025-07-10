import tkinter as tk
from tkinter import ttk
import math

from colors import ColorConfig
from tooltip import ToolTip
from nodes import NetworkNode

def open_node_list_editor(gui):
    if getattr(gui, 'legend_window', None) and gui.legend_window.winfo_exists():
        gui.legend_window.destroy()
        gui.legend_window = None

    if getattr(gui, 'node_list_editor', None) and gui.node_list_editor.winfo_exists():
        gui.node_list_editor.lift()
        return

    def close_editor():
        try:
            gui.node_list_editor.grab_release()
        except Exception:
            pass
        gui.node_list_editor.destroy()
        gui.node_list_editor = None
        gui.regain_focus()

    win, content = gui.create_popup("Node List Editor", 1100, 900, on_close=close_editor, grab=False)
    gui.node_list_editor = win
    win.lift(gui.root)
    win.attributes("-topmost", True)
    # Initialize global variables for column resizing
    global resizing_column, start_x, original_width
    resizing_column = None
    start_x = 0
    original_width = 0

    # --- helper: convert pixels → character columns for this font ---
    def px_to_cols(px, min_cols=3):
        """Return the smallest Entry ‘width’ (in characters) that will fill ≥ px."""
        glyph_px = gui.custom_font.measure("0") or 8   # average width of one glyph
        return max(min_cols, math.ceil(px / glyph_px))  #  <-  round **up**

    # Dictionary to store all Entry widgets for each column
    gui.column_entries = {}

    # Add refresh button at the top
    button_frame = tk.Frame(content, bg=ColorConfig.current.FRAME_BG)
    button_frame.pack(fill=tk.X, padx=5, pady=5)

    refresh_btn = tk.Button(button_frame, text="🔄 Refresh List", 
                        command=lambda: rebuild_editor_content(),
                        bg=ColorConfig.current.BUTTON_BG,
                        fg=ColorConfig.current.BUTTON_TEXT,
                        activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
                        activeforeground=ColorConfig.current.BUTTON_ACTIVE_TEXT)
    refresh_btn.pack(side=tk.LEFT, padx=5)

    container = tk.Frame(content, bg=ColorConfig.current.FRAME_BG)
    container.pack(fill="both", expand=True)

    canvas = tk.Canvas(container, bg=ColorConfig.current.FRAME_BG, highlightthickness=0)
    theme = "Dark" if ColorConfig.current == ColorConfig.Dark else "Light"
    v_scrollbar = ttk.Scrollbar(container, orient="vertical", style=f"{theme}Scrollbar.Vertical.TScrollbar", command=canvas.yview)
    canvas.configure(yscrollcommand=v_scrollbar.set)
    v_scrollbar.pack(side="right", fill="y")
    gui.node_list_frame = tk.Frame(canvas, bg=ColorConfig.current.FRAME_BG)

    gui.node_list_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    # Create window with the frame inside the canvas, allowing it to expand horizontally
    inner_window = canvas.create_window((0, 0), window=gui.node_list_frame, anchor="nw")

    def resize_canvas(event):
        # Always update the canvas window to match the frame's required width
        # This ensures horizontal scrolling works properly when columns are resized
        frame_reqwidth = gui.node_list_frame.winfo_reqwidth()
        canvas_width = canvas.winfo_width()
        # Set the canvas window width to the frame's required width
        # This allows the frame to expand horizontally as needed
        canvas.itemconfig(inner_window, width=max(frame_reqwidth, canvas_width))
    canvas.bind("<Configure>", resize_canvas)

    canvas.bind("<Configure>", resize_canvas)

    canvas.configure(yscrollcommand=v_scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    container.pack(fill="both", expand=True)
    v_scrollbar.pack(side="right", fill="y")

    gui.list_editor_xy_fields = {}

    def rebuild_editor_content():
        # Clear all widgets in the header row to force indicator update
        for widget in gui.node_list_frame.grid_slaves(row=4):
            widget.destroy()
        # Always sort gui.nodes according to current sort settings
        if hasattr(gui, 'sort_column') and gui.sort_column is not None:
            attr = fields[gui.sort_column][1]
            def get_sort_key(node):
                if hasattr(node, "vlans") and attr in node.vlans:
                    value = node.vlans.get(attr, "")
                else:
                    value = getattr(node, attr, "")
                if attr in ("x", "y"):
                    return float(value) if value else 0
                return str(value).lower() if value else ""
            gui.nodes = sorted(gui.nodes, key=get_sort_key, reverse=gui.sort_reverse)
        else:
            gui.nodes = sorted(gui.nodes, key=lambda n: n.name.lower())
        if not hasattr(gui, "column_widths") or not isinstance(gui.column_widths, dict):
            gui.column_widths = {}
        column_widths = gui.column_widths
        for col_index, (label, attr) in enumerate(fields):
            if col_index not in column_widths:
                if attr in ("x", "y"):
                    entry_width = 2
                elif attr in ("file_path", "web_config_url"):
                    entry_width = 15
                elif attr == "remote_desktop_address":
                    entry_width = 10
                else:
                    entry_width = 9
                glyph_px = gui.custom_font.measure("0") or 8
                initial_width = entry_width * glyph_px + 10
                column_widths[col_index] = initial_width
        gui.column_widths = column_widths

        # Only destroy the existing nodes table content
        for widget in gui.node_list_frame.winfo_children():
            if widget.grid_info()['row'] >= 3:  # Only destroy widgets in the existing nodes section
                widget.destroy()

        # Reset column entries tracking
        gui.column_entries = {col_index: [] for col_index in range(len(fields))}

        # Update "add new node row" entries with stored column widths
        for col_index in range(len(fields)):
            if col_index in column_widths and column_widths[col_index] > 50:
                for widget in gui.node_list_frame.winfo_children():
                    grid_info = widget.grid_info()
                    if grid_info and grid_info['row'] == 1 and grid_info['column'] == col_index:
                        if isinstance(widget, tk.Entry):
                            # Convert pixel width to character width
                            char_width = max(3, int(column_widths[col_index] / 8))
                            widget.config(width=char_width)
                            # Add to column entries tracking
                            if col_index in gui.column_entries:
                                gui.column_entries[col_index].append(widget)

        # ── Add “new node” row (always shown) ───────────────────────────────

        tk.Label(gui.node_list_frame, text="Add new node:",
                font=('Helvetica', 12, 'bold'),
                bg=ColorConfig.current.FRAME_BG,
                fg=ColorConfig.current.BUTTON_TEXT) \
        .grid(row=0, column=0, columnspan=len(fields)+1,
                sticky="w", pady=5)

        gui.new_node_entries = []
        for col_index, (label, attr) in enumerate(fields):
            # sensible default widths
            if attr in ("x", "y"):
                entry_width = 4
            elif attr in ("file_path", "web_config_url"):
                entry_width = 60
            elif attr == "remote_desktop_address":
                entry_width = 20
            else:
                entry_width = 15

            # honour any saved column resize
            if col_index in column_widths and column_widths[col_index] > 50:
                entry_width = max(entry_width,
                                px_to_cols(column_widths[col_index]))

            e = tk.Entry(gui.node_list_frame, width=entry_width,
                        font=('Helvetica', 10),
                        bg=ColorConfig.current.ROW_BG_EVEN,
                        fg=ColorConfig.current.ENTRY_TEXT,
                        relief='solid', borderwidth=1,
                        highlightthickness=0)
            e.grid(row=1, column=col_index,
                padx=1, pady=3, ipady=3, sticky="nsew")

            gui.column_entries.setdefault(col_index, []).append(e)
            gui.new_node_entries.append(e)

            # Add entry to column tracking
            gui.column_entries.setdefault(col_index, []).append(e)
            # Focus highlight
            def on_focus_in(event, e=e):
                e.config(bg=ColorConfig.current.ENTRY_FOCUS_BG)
                e.select_range(0, tk.END)
                return 'break'
            def on_focus_out(event, e=e):
                e.config(bg=ColorConfig.current.ROW_BG_EVEN)
                return 'break'
            e.bind('<FocusIn>', on_focus_in)
            e.bind('<FocusOut>', on_focus_out)
            e.bind('<Return>', on_focus_out)
            e.bind('<Tab>', on_focus_out)
            # Tooltip for truncated cells
            if attr in ("file_path", "web_config_url"):
                ToolTip(e, "", gui, bg="#ffffe0", fg="black")

        def add_new_node():
            # Get values from entries
            values = {fields[i][1]: entry.get() for i, entry in enumerate(gui.new_node_entries)}

            # Set default values if not provided
            name = values.get('name', 'NewNode')
            try:
                x = float(values.get('x', '100')) if values.get('x') else 100
                y = float(values.get('y', '100')) if values.get('y') else 100
            except ValueError:
                x, y = 100, 100  # Default values if conversion fails

            # Create new node
            # Build VLANs dictionary dynamically
            vlans = {vlan: values.get(vlan, '') for vlan in getattr(gui, 'vlan_label_order', gui.vlan_label_names.keys())}
            new_node = NetworkNode(gui.canvas, name=name, x=x, y=y,
                                vlans=vlans,
                                remote_desktop_address=values.get('remote_desktop_address', ''),
                                file_path=values.get('file_path', ''),
                                web_config_url=values.get('web_config_url', ''))

            # Add to nodes list
            gui.nodes.append(new_node)
            gui.on_node_select(new_node)
            gui.unsaved_changes = True

            # Clear entry fields
            for entry in gui.new_node_entries:
                entry.delete(0, tk.END)

            # Rebuild the editor content
            rebuild_editor_content()

        add_btn = tk.Button(gui.node_list_frame, text="➕ Add",
                            command=add_new_node,
                            bg=ColorConfig.current.BUTTON_BG,
                            fg=ColorConfig.current.BUTTON_TEXT,
                            activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
                            activeforeground=ColorConfig.current.BUTTON_ACTIVE_TEXT)
        add_btn.grid(row=1, column=len(fields), padx=5)

        # Add header for existing nodes
        tk.Label(gui.node_list_frame, text="Existing Nodes:", font=('Helvetica', 12, 'bold'),
                bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT)\
                .grid(row=3, column=0, columnspan=len(fields)+1, sticky="w", pady=5)

        # Create column headers with sorting indicators
        for col_index, (label, _) in enumerate(fields):
            header_frame = tk.Frame(gui.node_list_frame, bg=ColorConfig.current.HEADER_BG, highlightbackground=ColorConfig.current.CELL_BORDER, highlightthickness=1)
            header_frame.grid(row=4, column=col_index, padx=1, pady=3, ipady=3, sticky="ew")

            header_label = tk.Label(
                header_frame,
                text=label,
                font=('Helvetica', 10, 'bold'),
                bg=ColorConfig.current.HEADER_BG,
                fg=ColorConfig.current.HEADER_TEXT,
            )
            header_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

            # Add column divider for resizing (always at the far right)
            divider = tk.Frame(header_frame, width=4, bg='#666666', cursor="sb_h_double_arrow")
            divider.pack(side=tk.RIGHT, fill=tk.Y, pady=2)

            # Add sorting indicator (just left of divider if present)
            if getattr(gui, 'sort_column', None) == col_index:
                indicator = "▼" if gui.sort_reverse else "▲"
                indicator_label = tk.Label(header_frame, text=indicator, font=('Helvetica', 10, 'bold'),
                                          bg=ColorConfig.current.FRAME_BG, fg=ColorConfig.current.BUTTON_TEXT)
                indicator_label.pack(side=tk.RIGHT, padx=2)

            # Make header clickable (sorting only, not resizing)
            header_label.bind("<Button-1>", lambda e, i=col_index: sort_nodes(i))

            def start_resize(event, col=col_index):
                global resizing_column, start_x_root, original_width
                resizing_column = col
                start_x_root = event.x_root

                # Find the header frame to get its original width
                for widget in gui.node_list_frame.winfo_children():
                    grid_info = widget.grid_info()
                    if grid_info and grid_info['row'] == 4 and grid_info['column'] == col:
                        original_width = widget.winfo_width()
                        break

                # Bind to the entire window for better mouse tracking
                gui.node_list_editor.bind("<B1-Motion>", resize_column)
                gui.node_list_editor.bind("<ButtonRelease-1>", end_resize)

            def resize_column(event):
                """Live column‑drag with minimal redraw/flicker."""
                global resizing_column, start_x_root, original_width
                if resizing_column is None:
                    return

                dx = event.x_root - start_x_root
                new_width = max(40, original_width + dx)
                gui.column_widths[resizing_column] = new_width

                # Only update the relevant column's width in real time
                gui.node_list_frame.grid_columnconfigure(resizing_column, minsize=new_width)

                def apply_to_entries():
                    char_w = px_to_cols(new_width)
                    for e in gui.column_entries.get(resizing_column, []):
                        if e.winfo_exists():
                            e.config(width=char_w)
                    frame_reqwidth = gui.node_list_frame.winfo_reqwidth()
                    canvas.itemconfig(inner_window, width=frame_reqwidth)
                    canvas.configure(scrollregion=canvas.bbox("all"))

                if getattr(gui, "_resize_job", None):
                    gui.node_list_frame.after_cancel(gui._resize_job)
                gui._resize_job = gui.node_list_frame.after_idle(apply_to_entries)
                ensure_editor_can_fit()

            def end_resize(event):
                global resizing_column

                # Unbind the motion and release events
                if resizing_column is not None:
                    gui.node_list_editor.unbind("<B1-Motion>")
                    gui.node_list_editor.unbind("<ButtonRelease-1>")
                    # Trigger a full rebuild if needed (to reflow or persist)
                    rebuild_editor_content()

                resizing_column = None

            divider.bind("<ButtonPress-1>", lambda event, col=col_index: start_resize(event, col))

        # Add delete button     
        header_label = tk.Label(
            gui.node_list_frame, text="Delete",
            font=('Helvetica', 10, 'bold'),
            bg=ColorConfig.current.HEADER_BG, fg=ColorConfig.current.HEADER_TEXT,
            padx=8, pady=4, borderwidth=1, relief='solid')
        header_label.grid(row=4, column=len(fields), padx=1, pady=1, sticky="nsew")
        gui.node_list_frame.grid_columnconfigure(len(fields), weight=0, minsize=80)

        # Use the current sort order
        # Use the current sorted gui.nodes list
        for row_index, node in enumerate(gui.nodes, start=5):
            xy_fields = []
            for col_index, (label, attr) in enumerate(fields):
                # Fetch VLAN value from node.vlans mapping if present
                if hasattr(node, "vlans") and attr in getattr(node, "vlans", {}):
                    value = node.vlans.get(attr, "")
                elif hasattr(node, "data") and isinstance(node.data, dict) and "vlans" in node.data and attr in node.data["vlans"]:
                    value = node.data["vlans"].get(attr, "")
                else:
                    value = getattr(node, attr, "")
                # Set column widths
                if attr in ("x", "y"):
                    entry_width = 4
                    # Format to 0 decimal places if possible
                    try:
                        value_str = "{:.0f}".format(float(value))
                    except (ValueError, TypeError):
                        value_str = str(value)
                elif attr in ("file_path", "web_config_url"):
                    entry_width = 60
                    value_str = str(value)
                elif attr == "remote_desktop_address":
                    entry_width = 20
                    value_str = str(value)
                else:
                    entry_width = 15
                    value_str = str(value)
                # Alternating row background
                row_bg = ColorConfig.current.ROW_BG_EVEN if (row_index % 2 == 0) else ColorConfig.current.ROW_BG_ODD
                entry = tk.Entry(
                        gui.node_list_frame,
                        font=('Helvetica', 10),
                        bg=row_bg,
                        fg=ColorConfig.current.ENTRY_TEXT,
                        relief='solid', borderwidth=1, highlightthickness=0,
                        width=entry_width
                )
                entry.grid(row=row_index, column=col_index,
                        padx=1, pady=3, ipady=3, sticky="nsew")
                entry.insert(0, value_str)
                entry.grid(row=row_index, column=col_index, padx=1, pady=3, ipady=3)

                # Add entry to column tracking
                if col_index in gui.column_entries:
                    gui.column_entries[col_index].append(entry)
                # Focus highlight
                def on_focus_in(event, e=entry):
                    e.config(bg=ColorConfig.current.ENTRY_FOCUS_BG)
                    e.select_range(0, tk.END)
                    return 'break'
                def on_focus_out(event, n=node, a=attr, e=entry):
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
                        if a.startswith("VLAN_"):
                            vlan_id_str = a[5:]
                            vlan_id_int = int(vlan_id_str)
                            possible_keys = [vlan_id_str, vlan_id_int, f"VLAN_{vlan_id_str}"]
                            for key in possible_keys:
                                if key in n.vlans:
                                    n.vlans[key] = val
                                    break
                            else:
                                n.vlans[vlan_id_str] = val
                        else:
                            setattr(n, a, val)
                        if a == "name":
                            n.canvas.itemconfigure(n.text, text=n.name)
                        n.adjust_node_size()
                        gui.unsaved_changes = True
                    # Restore row background
                    e.config(bg=row_bg)
                    return 'break'
                entry.bind('<FocusIn>', on_focus_in)
                entry.bind('<FocusOut>', on_focus_out)
                entry.bind('<Return>', on_focus_out)
                entry.bind('<Tab>', on_focus_out)
                # Tooltip for truncated cells
                if attr in ("file_path", "web_config_url") and len(value_str) > entry_width:
                    ToolTip(entry, value_str, gui, bg="#ffffe0", fg="black")

                # Simplified event bindings
                def on_focus_in(event, e=entry):
                    e.select_range(0, tk.END)
                    return 'break'  # Prevent default focus behavior

                def on_focus_out(event, n=node, a=attr, e=entry):
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
                        if a.startswith("VLAN_"):
                            vlan_id_str = a[5:]
                            vlan_id_int = int(vlan_id_str)
                            possible_keys = [vlan_id_str, vlan_id_int, f"VLAN_{vlan_id_str}"]
                            for key in possible_keys:
                                if key in n.vlans:
                                    n.vlans[key] = val
                                    break
                            else:
                                n.vlans[vlan_id_str] = val
                        else:
                            setattr(n, a, val)
                        if a == "name":
                            n.canvas.itemconfigure(n.text, text=n.name)
                        n.adjust_node_size()
                        gui.unsaved_changes = True
                    return 'break'  # Prevent default focus behavior

                entry.bind('<FocusIn>', on_focus_in)
                entry.bind('<FocusOut>', on_focus_out)
                entry.bind('<Return>', on_focus_out)
                entry.bind('<Tab>', on_focus_out)

                if attr in ("x", "y"):
                    xy_fields.append(entry)

            gui.list_editor_xy_fields[node] = xy_fields

            def delete_node_callback(n=node):
                def delete():
                    gui.remove_node(n)
                    rebuild_editor_content()
                return delete

            def ensure_editor_can_fit():
                gui.node_list_editor.update_idletasks()          # sizes are now real
                need_px  = gui.node_list_frame.winfo_reqwidth() + 20   # + margin
                have_px  = gui.node_list_editor.winfo_width()
                if need_px > have_px:                             # grow only – never shrink
                    h_px = gui.node_list_editor.winfo_height()
                    x, y = gui.node_list_editor.winfo_x(), gui.node_list_editor.winfo_y()
                    gui.node_list_editor.geometry(f"{need_px}x{h_px}+{x}+{y}")

            # ── add delete button ──   
            del_btn = tk.Button(
                gui.node_list_frame,
                text="🗑",
                fg="red",
                bg=row_bg,
                borderwidth=1,
                relief='solid',
                command=delete_node_callback(node)
            )
            del_btn.grid(row=row_index, column=len(fields), padx=1, pady=1, sticky="nsew")

        # ── set the grid’s minsize once so Refresh doesn’t grow columns ──
        for col_index, px in column_widths.items():
            gui.node_list_frame.grid_columnconfigure(col_index, minsize=px)

            # keep Entry widgets aligned with the header
            char_w = px_to_cols(px)
            for e in gui.column_entries.get(col_index, []):
                if e.winfo_exists():
                    e.config(width=char_w)

        ensure_editor_can_fit()

    # Initialize the fields list
    fields = [("Name", "name")]
    # Add VLAN fields dynamically
    for vlan in getattr(gui, 'vlan_label_order', gui.vlan_label_names.keys()):
        label = gui.vlan_label_names.get(vlan, vlan)
        fields.append((label, vlan))
    fields += [
        ("RDP Address", "remote_desktop_address"),
        ("File Path", "file_path"),
        ("Web URL", "web_config_url"),
        ("X", "x"),
        ("Y", "y"),
    ]

    # Dynamically add any extra fields found in node data
    all_node_keys = set()
    for node in getattr(gui, 'nodes', []):
        all_node_keys.update(node.__dict__.keys() if hasattr(node, '__dict__') else node.keys())
    # Flatten fields to a set of attribute names already present
    existing_attrs = set(attr for _, attr in fields)
    # Add any missing keys as columns (skip private/dunder and already present)
    for key in sorted(all_node_keys):
        if not key.startswith('_') and key not in existing_attrs:
            fields.append((key.replace('_', ' ').title(), key))

    # Filter out specified columns by label or attribute (case-insensitive)
    HIDE_LABELS = {"canvas", "connections", "font", "shape", "text", "type", "vlans", "last drag x", "last drag y"}
    HIDE_ATTRS = {"canvas", "connections", "font", "shape", "text", "type", "vlans", "last_drag_x", "last_drag_y"}
    fields = [
        (label, attr)
        for (label, attr) in fields
        if label.strip().lower() not in HIDE_LABELS and attr.strip().lower() not in HIDE_ATTRS
    ]

    # Initialize sorting state
    if not hasattr(gui, 'sort_column'):
        gui.sort_column = 0  # Default to sorting by name
        gui.sort_reverse = False

    def sort_nodes(column_index):
        attr = fields[column_index][1]
        if gui.sort_column == column_index:
            gui.sort_reverse = not gui.sort_reverse
        else:
            gui.sort_column = column_index
            gui.sort_reverse = False

        def get_sort_key(node):
            # Handle VLAN columns by attribute key
            if hasattr(node, "vlans") and attr in node.vlans:
                value = node.vlans.get(attr, "")
            else:
                value = getattr(node, attr, "")
            if attr in ("x", "y"):
                return float(value) if value else 0
            return str(value).lower() if value else ""

        # Sort all nodes
        gui.nodes = sorted(gui.nodes, key=get_sort_key, reverse=gui.sort_reverse)
        rebuild_editor_content()

    # Add button to create new node
    # Initial build of the editor content
    rebuild_editor_content()
    # Focus the first "add new node" entry after a short delay, if present
    if getattr(gui, "new_node_entries", None) and gui.new_node_entries:
        win.after(100, lambda: gui.new_node_entries[0].focus_set())

    gui.fix_window_geometry(gui.node_list_editor, 1600, 900)