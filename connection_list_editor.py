import tkinter as tk
from tkinter import ttk

def open_connection_list_editor(gui_self):
    ColorConfig = gui_self.ColorConfig if hasattr(gui_self, "ColorConfig") else __import__("colors").ColorConfig

    if getattr(gui_self, 'legend_window', None) and gui_self.legend_window.winfo_exists():
        gui_self.legend_window.destroy()
        gui_self.legend_window = None

    if getattr(gui_self, 'connection_list_editor', None) and gui_self.connection_list_editor.winfo_exists():
        gui_self.connection_list_editor.lift()
        return

    def close_editor():
        try:
            gui_self.connection_list_editor.grab_release()
        except Exception:
            pass
        try:
            gui_self.connection_list_editor.destroy()
        except Exception:
            pass
        gui_self.connection_list_editor = None
        try:
            gui_self.root.focus_force()
        except Exception:
            pass
        try:
            gui_self.root.lift()
        except Exception:
            pass

    win, content = gui_self.create_popup(
        "Connection List Editor", 800, 700,
        on_close=gui_self.make_popup_closer("connection_list_editor"),
        grab=False
    )
    gui_self.connection_list_editor = win
    win.lift(gui_self.root)
    win.attributes("-topmost", True)

    button_frame = tk.Frame(content, bg=ColorConfig.current.FRAME_BG)
    button_frame.pack(fill=tk.X, padx=5, pady=5)

    def rebuild_editor_content():
        for widget in gui_self.connection_list_frame.winfo_children():
            widget.destroy()

        headers = ["From", "To", "Label", "Info", "Delete"]
        for i, h in enumerate(headers):
            header_label = tk.Label(
                gui_self.connection_list_frame,
                text=h,
                font=('Helvetica', 10, 'bold'),
                bg=ColorConfig.current.HEADER_BG,
                fg=ColorConfig.current.HEADER_TEXT,
                padx=8, pady=4, borderwidth=1, relief='solid',
            )
            header_label.grid(row=0, column=i, padx=1, pady=1, sticky="nsew")
            gui_self.connection_list_frame.grid_columnconfigure(i, weight=1, minsize=80)

        connections = set()
        for node in gui_self.nodes:
            for conn in node.connections:
                if conn not in connections:
                    connections.add(conn)

        for row_index, conn in enumerate(connections, start=1):
            row_bg = ColorConfig.current.ROW_BG_EVEN if row_index % 2 == 0 else ColorConfig.current.ROW_BG_ODD
            tk.Label(gui_self.connection_list_frame, text=conn.node1.name,
                    bg=row_bg, fg=ColorConfig.current.BUTTON_TEXT, padx=8, pady=4, borderwidth=1, relief='solid').grid(row=row_index, column=0, padx=1, pady=1, sticky="nsew")
            tk.Label(gui_self.connection_list_frame, text=conn.node2.name,
                    bg=row_bg, fg=ColorConfig.current.BUTTON_TEXT, padx=8, pady=4, borderwidth=1, relief='solid').grid(row=row_index, column=1, padx=1, pady=1, sticky="nsew")

            label_entry = tk.Entry(gui_self.connection_list_frame, width=30, bg=row_bg, fg=ColorConfig.current.ENTRY_TEXT,
                                  insertbackground=ColorConfig.current.ENTRY_TEXT, borderwidth=1, relief='solid')
            label_entry.insert(0, conn.label or "")
            label_entry.grid(row=row_index, column=2, padx=1, pady=1, sticky="nsew")

            info_entry = tk.Entry(gui_self.connection_list_frame, width=50, bg=row_bg, fg=ColorConfig.current.ENTRY_TEXT,
                                 insertbackground=ColorConfig.current.ENTRY_TEXT, borderwidth=1, relief='solid')
            info_entry.insert(0, conn.connectioninfo or "")
            info_entry.grid(row=row_index, column=3, padx=1, pady=1, sticky="nsew")

            def make_update_callback(c=conn, le=label_entry, ie=info_entry):
                def update_fields(event=None):
                    c.label = le.get()
                    c.connectioninfo = ie.get()
                    c.update_label()
                    gui_self.unsaved_changes = True
                return update_fields

            label_entry.bind("<FocusOut>", make_update_callback())
            info_entry.bind("<FocusOut>", make_update_callback())

            def delete_conn(c=conn):
                gui_self.canvas.delete(c.line)
                if c.label_id:
                    gui_self.canvas.delete(c.label_id)
                if hasattr(c, 'label_bg') and c.label_bg:
                    gui_self.canvas.delete(c.label_bg)
                c.node1.connections.remove(c)
                c.node2.connections.remove(c)
                gui_self.unsaved_changes = True
                rebuild_editor_content()

            tk.Button(gui_self.connection_list_frame, text="🗑", fg="red", bg=row_bg, borderwidth=1, relief='solid', command=lambda c=conn: delete_conn(c)).grid(row=row_index, column=4, padx=1, pady=1, sticky="nsew")

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
    canvas.pack(side="left", fill="both", expand=True)

    gui_self.connection_list_frame = tk.Frame(canvas, bg=ColorConfig.current.FRAME_BG)
    inner_window = canvas.create_window((0, 0), window=gui_self.connection_list_frame, anchor="nw")

    def resize_canvas(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfig(inner_window, width=canvas.winfo_width() - 24)

    gui_self.connection_list_frame.bind("<Configure>", resize_canvas)
    canvas.bind("<Configure>", resize_canvas)

    rebuild_editor_content()