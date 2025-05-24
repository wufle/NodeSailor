class ColorConfig:
    class Light:
        NODE_DEFAULT = 'light steel blue'  # Default node color (light blue)
        NODE_GREYED_OUT = 'gainsboro'  # Node is disabled or inactive (light gray)
        NODE_HIGHLIGHT = 'gold'  # Highlighted node (yellow/gold)
        NODE_HOST = 'turquoise'  # Host node (turquoise)
        NODE_OUTLINE_DEFAULT = 'black'  # Default node outline (black)
        NODE_PING_SUCCESS = 'green'  # Node ping successful (green)
        NODE_PING_PARTIAL_SUCCESS = 'yellow'  # Node ping partially successful (yellow)
        NODE_PING_FAILURE = 'red'  # Node ping failed (red)
        FRAME_BG = 'white'  # Main background/frame (white)
        INFO_NOTE_BG = 'white'  # Info note background (white)
        INFO_TEXT = 'black'  # Info text color (black)
        BUTTON_BG = 'white'  # Button background (white)
        BUTTON_TEXT = 'black'  # Button text (black)
        BUTTON_ACTIVE_BG = '#e0e0e0'  # Button background when pressed (light gray)
        BUTTON_ACTIVE_TEXT = '#000000'  # Button text when pressed (black)
        BUTTON_CONFIGURATION_MODE = 'light coral'  # Button color in configuration mode (light coral)
        Connections = 'dim gray'  # Connection lines (dim gray)
        BORDER_COLOR = '#f7f7f7'  # Border color for frames/windows (very light gray)
        # Group rectangle colors
        GROUP_DEFAULT = '#e6f2ff'  # Default group rectangle background (very light blue)
        GROUP_OUTLINE = '#4d94ff'  # Group rectangle outline (medium blue)
        GROUP_SELECTED = '#0066cc'  # Selected group rectangle (blue)
        GROUP_TEXT = '#003366'  # Group text color (dark blue)
        # New for list editor readability
        ROW_BG_EVEN = '#f9f9f9'  # Even row background in lists (very light gray)
        ROW_BG_ODD = '#e6f0fa'  # Odd row background in lists (light blue-gray)
        HEADER_BG = '#dbeafe'  # Header background in lists (pale blue)
        HEADER_TEXT = '#1e293b'  # Header text color (dark slate blue)
        ENTRY_FOCUS_BG = '#f9f9f9'  # Entry background when focused (very light gray)
        CELL_BORDER = '#b6b6b6'  # Cell border color (gray)
        ENTRY_TEXT = '#222222'  # Entry text color (almost black)

    class Dark:
        NODE_DEFAULT = '#28376c'  # Default node color (dark blue)
        NODE_GREYED_OUT = '#4B5563'  # Node is disabled or inactive (gray)
        NODE_HIGHLIGHT = '#D97706'  # Highlighted node (orange)
        NODE_HOST = '#72741f'  # Host node (olive green)
        NODE_OUTLINE_DEFAULT = '#374151'  # Default node outline (dark gray-blue)
        NODE_PING_SUCCESS = '#047857'  # Node ping successful (teal green)
        NODE_PING_PARTIAL_SUCCESS = '#B45309'  # Node ping partially successful (amber)
        NODE_PING_FAILURE = '#991B1B'  # Node ping failed (dark red)
        FRAME_BG = "#0c0f14"  # Main background/frame (very dark blue)
        INFO_NOTE_BG = '#111827'  # Info note background (very dark gray-blue)
        INFO_TEXT = '#8f8f8f'  # Info text color (light gray)
        BUTTON_BG = '#1e2540'  # Button background (dark blue)
        BUTTON_TEXT = '#c7c7c7'  # Button text (light gray)
        BUTTON_ACTIVE_BG = '#111827'  # Button background when pressed (very dark gray-blue)
        BUTTON_ACTIVE_TEXT = 'black'  # Button text when pressed (black)
        BUTTON_CONFIGURATION_MODE = '#F87171'  # Button color in configuration mode (light red)
        Connections = '#6a7586'  # Connection lines (gray-blue)
        BORDER_COLOR = '#374151'  # Border color for frames/windows (dark gray-blue)
        # Group rectangle colors
        GROUP_DEFAULT = '#1a2942'  # Default group rectangle background (dark blue)
        GROUP_OUTLINE = '#3a5894'  # Group rectangle outline (blue-gray)
        GROUP_SELECTED = '#5d8cd9'  # Selected group rectangle (light blue)
        GROUP_TEXT = '#a3c2ff'  # Group text color (light blue)
        # New for list editor readability
        ROW_BG_EVEN = '#181e29'  # Even row background in lists (very dark blue)
        ROW_BG_ODD = '#232b3a'  # Odd row background in lists (dark blue-gray)
        HEADER_BG = '#22304a'  # Header background in lists (dark blue)
        HEADER_TEXT = '#e0e7ef'  # Header text color (very light blue)
        ENTRY_FOCUS_BG = '#2d3748'  # Entry background when focused (dark gray-blue)
        CELL_BORDER = '#3b4252'  # Cell border color (gray-blue)
        ENTRY_TEXT = '#e0e7ef'  # Entry text color (very light blue)

    # Default to Dark mode
    current = Dark

# Centralized group color presets
COLOR_PRESETS = [
    {
        "id": "preset1",
        "name": "Classic Blue",
        "light_bg": "#e3f0ff",
        "light_border": "#3a7bd5",
        "dark_bg": "#22304a",
        "dark_border": "#3a7bd5"
    },
    {
        "id": "preset2",
        "name": "Sunset",
        "light_bg": "#ffe5d0",
        "light_border": "#ff7f50",
        "dark_bg": "#4a2c23",
        "dark_border": "#ff7f50"
    },
    {
        "id": "preset3",
        "name": "Mint",
        "light_bg": "#e0fff4",
        "light_border": "#2ecc71",
        "dark_bg": "#204034",
        "dark_border": "#2ecc71"
    },
    {
        "id": "preset4",
        "name": "Lavender",
        "light_bg": "#f3e8ff",
        "light_border": "#a259e6",
        "dark_bg": "#2d234a",
        "dark_border": "#a259e6"
    },
    {
        "id": "preset5",
        "name": "Slate",
        "light_bg": "#f0f4f8",
        "light_border": "#607d8b",
        "dark_bg": "#232b32",
        "dark_border": "#607d8b"
    },
    {
        "id": "preset6",
        "name": "Contrast",
        "light_bg": "#ffffff",
        "light_border": "#000000",
        "dark_bg": "#000000",
        "dark_border": "#ffffff"
    }
]

def get_group_colors(color_preset_id, color_scheme):
    """
    Returns (bg, border) for the given preset and color scheme.
    color_scheme: "light" or "dark"
    """
    preset = next((p for p in COLOR_PRESETS if p["id"] == color_preset_id), COLOR_PRESETS[0])
    if color_scheme == "dark":
        return preset["dark_bg"], preset["dark_border"]
    else:
        return preset["light_bg"], preset["light_border"]