from colors import ColorConfig
import tkinter as tk
from tkinter import simpledialog

class StickyNote:
    def __init__(self, canvas, text, x, y, gui=None,
                 font=('Helvetica', '12'), bg=ColorConfig.current.INFO_NOTE_BG):
        self.canvas = canvas
        self.gui = gui  # May be None if older code doesn't pass the GUI
        self.text = text
        self.x = x
        self.y = y
        self.bg = bg
        self.font = font

        # Background rectangle
        self.bg_shape = canvas.create_rectangle(
            x, y, x + 100, y + 50,
            fill=ColorConfig.current.FRAME_BG, outline='',
            tags=("sticky_bg", f"bg_{id(self)}")  # consistent with "sticky_bg"
        )
        # Text
        self.note = canvas.create_text(
            x, y,
            text=text,
            font=self.font,
            fill=ColorConfig.current.INFO_TEXT,
            tags=("sticky_note",),
            anchor="nw"
        )

        # Left-click drag
        self.canvas.tag_bind(self.note, '<Button-1>', self.on_click)
        self.canvas.tag_bind(self.note, '<Shift-B1-Motion>', self.on_drag_notes)
        self.canvas.tag_bind(self.note, '<ButtonRelease-1>', self.on_release)

        # Right-click context menu
        self.canvas.tag_bind(self.note, '<Button-3>', self.show_context_menu)
        self.canvas.tag_bind(self.bg_shape, '<Button-3>', self.show_context_menu)

        self.adjust_note_size()
        self.type = 'sticky'

    def adjust_note_size(self):
        bbox = self.canvas.bbox(self.note)
        if bbox:
            padding = 2
            self.canvas.coords(self.bg_shape,
                bbox[0] - padding, bbox[1] - padding,
                bbox[2] + padding, bbox[3] + padding)
            self.canvas.itemconfig(self.bg_shape,
                fill=ColorConfig.current.INFO_NOTE_BG)

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
                self.canvas.move(self.bg_shape, dx, dy)
                self.last_drag_x = event.x
                self.last_drag_y = event.y
                self.adjust_note_size()

    def on_release(self, event):
        self.canvas.selected_object_type = None
        self.canvas.selected_object = None

    # Right-click menu
    def show_context_menu(self, event):
        context_menu = tk.Toplevel(self.canvas)
        context_menu.wm_overrideredirect(True)
        context_menu.wm_geometry(f"+{event.x_root}+{event.y_root}")

        menu_frame = tk.Frame(context_menu, bg=ColorConfig.current.BUTTON_BG)
        menu_frame.pack()

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

        options = [
            ("Edit Note Text", self.edit_sticky_text),
            ("Delete Note", self.delete_sticky)
        ]

        for txt, cmd in options:
            btn = tk.Button(
                menu_frame, text=txt,
                command=lambda c=cmd: [destroy_menu(), self.canvas.after(10, c)],
                bg=ColorConfig.current.BUTTON_BG,
                fg=ColorConfig.current.BUTTON_TEXT,
                activebackground=ColorConfig.current.BUTTON_ACTIVE_BG,
                activeforeground=ColorConfig.current.BUTTON_ACTIVE_TEXT,
                relief='flat', borderwidth=0, padx=10, pady=4, anchor='w',
                font=('Helvetica', 10)
            )
            btn.pack(fill='x')

        # Clicking elsewhere or pressing Escape closes the menu
        self.canvas.bind("<Button-1>", lambda e: destroy_menu(), add="+")
        context_menu.bind("<Escape>", lambda e: destroy_menu())

    def edit_sticky_text(self):
        if self.gui and hasattr(self.gui, "show_sticky_note_popup"):
            def on_ok(new_text):
                self.text = new_text
                self.canvas.itemconfig(self.note, text=self.text)
                self.adjust_note_size()
                if hasattr(self.gui, "regain_focus"):
                    self.gui.regain_focus()
            self.gui.show_sticky_note_popup(self.text, on_ok)
        else:
            # fallback to simpledialog if gui method is not available
            new_text = simpledialog.askstring(
                "Edit Note",
                "Enter new note text:",
                initialvalue=self.text
            )
            if new_text is not None:
                self.text = new_text
                self.canvas.itemconfig(self.note, text=self.text)
                self.adjust_note_size()

    def delete_sticky(self):
        # If the GUI is available, call its remove_sticky. Otherwise, just delete ourselves.
        if self.gui and hasattr(self.gui, 'remove_sticky'):
            self.gui.remove_sticky(self)
        else:
            self.canvas.delete(self.note)
            self.canvas.delete(self.bg_shape)