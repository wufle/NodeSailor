import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog, messagebox, font, filedialog, colorchooser, ttk
import subprocess
from threading import Thread
import json
import platform
from PIL import Image, ImageTk
import socket
import os
import webbrowser
import ctypes
import math

# Classes
from colors import ColorConfig
from notes import StickyNote
from connections import ConnectionLine
from tooltip import ToolTip
from nodes import NetworkNode
from gui import NetworkMapGUI
from utils import get_ip_addresses
from groups import GroupManager, RectangleGroup
 
if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(True, True)
    root.title("NodeSailor")
    gui = NetworkMapGUI(root)
    root.mainloop()