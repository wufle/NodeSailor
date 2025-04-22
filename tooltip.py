from colors import ColorConfig
import tkinter as tk

class ToolTip:
    def __init__(self, widget, text, gui, bg=None, fg=None):
        self.widget = widget
        self.text = text
        self.gui = gui
        self.bg_func = bg if callable(bg) else (lambda: bg or "#ffffe0")
        self.fg_func = fg if callable(fg) else (lambda: fg or "black")
        self.tip_window = None
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)

    def on_enter(self, event=None):
        if self.gui.show_tooltips:
            self.show_tip()

    def on_leave(self, event=None):
        self.hide_tip()

    def show_tip(self):
        if self.tip_window or not self.text:
            return
        x = self.widget.winfo_rootx()
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 2
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                         background=self.bg_func(), foreground=self.fg_func(),
                         relief='solid', borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None