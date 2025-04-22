class ColorConfig:
    class Light:
        NODE_DEFAULT = 'light steel blue'
        NODE_GREYED_OUT = 'gainsboro'
        NODE_HIGHLIGHT = 'gold'
        NODE_HOST = 'turquoise'
        NODE_OUTLINE_DEFAULT = 'black'
        NODE_PING_SUCCESS = 'green'
        NODE_PING_PARTIAL_SUCCESS = 'yellow'
        NODE_PING_FAILURE = 'red'
        FRAME_BG = 'white'
        INFO_NOTE_BG = 'white'
        INFO_TEXT = 'black'
        BUTTON_BG = 'white'
        BUTTON_TEXT = 'black'
        BUTTON_ACTIVE_BG = '#e0e0e0'
        BUTTON_ACTIVE_TEXT = '#000000'
        BUTTON_CONFIGURATION_MODE = 'light coral'
        Connections = 'dim gray'
        BORDER_COLOR = '#f7f7f7'
        # New for list editor readability
        ROW_BG_EVEN = '#f9f9f9'
        ROW_BG_ODD = '#e6f0fa'
        HEADER_BG = '#dbeafe'
        HEADER_TEXT = '#1e293b'
        ENTRY_FOCUS_BG = '#f9f9f9'
        CELL_BORDER = '#b6b6b6'
        ENTRY_TEXT = '#222222'

    class Dark:
        NODE_DEFAULT = '#28376c'
        NODE_GREYED_OUT = '#4B5563'
        NODE_HIGHLIGHT = '#D97706'
        NODE_HOST = '#72741f'
        NODE_OUTLINE_DEFAULT = '#374151'
        NODE_PING_SUCCESS = '#047857'
        NODE_PING_PARTIAL_SUCCESS = '#B45309'
        NODE_PING_FAILURE = '#991B1B'
        FRAME_BG = "#0c0f14" #MAIN BACKBROUND
        INFO_NOTE_BG = '#111827'
        INFO_TEXT = '#8f8f8f'
        BUTTON_BG = '#1e2540'
        BUTTON_TEXT = '#c7c7c7'
        BUTTON_ACTIVE_BG = '#111827' #button when pressed
        BUTTON_ACTIVE_TEXT = 'black'  #button text when pressed
        BUTTON_CONFIGURATION_MODE = '#F87171'
        Connections = '#6a7586'
        BORDER_COLOR = '#374151' #f1 and legend window border colour
        # New for list editor readability
        ROW_BG_EVEN = '#181e29'
        ROW_BG_ODD = '#232b3a'
        HEADER_BG = '#22304a'
        HEADER_TEXT = '#e0e7ef'
        ENTRY_FOCUS_BG = '#2d3748'
        CELL_BORDER = '#3b4252'
        ENTRY_TEXT = '#e0e7ef'

    # Default to Dark mode
    current = Dark