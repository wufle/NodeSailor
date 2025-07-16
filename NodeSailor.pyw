import customtkinter as ctk
import hPyT
from gui import NetworkMapGUI

if __name__ == "__main__":
    root = ctk.CTk()
    hPyT.title_bar.hide(root)
    root.resizable(True, True)
    root.title("NodeSailor v0.9.34")
    gui = NetworkMapGUI(root)
    root.mainloop()