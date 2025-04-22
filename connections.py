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
                label_entry.grid(row=0, column=1, padx=10, pady=5)

                tk.Label(dialog, text="Info (on hover):").grid(row=1, column=0, padx=10, pady=5)
                info_entry = tk.Entry(dialog, width=40)
                info_entry.grid(row=1, column=1, padx=10, pady=5)

                def submit():
                    self.label = label_entry.get()
                    self.connectioninfo = info_entry.get()
                    self.update_label()
                    dialog.destroy()

                tk.Button(dialog, text="Save", command=submit).grid(row=2, column=0, columnspan=2, pady=10)
                dialog.transient(self.root)
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
