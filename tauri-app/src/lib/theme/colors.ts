import type { ThemeName } from "../stores/uiStore";

export interface ThemeColors {
  FRAME_BG: string;
  BUTTON_BG: string;
  BUTTON_TEXT: string;
  BUTTON_ACTIVE_BG: string;
  BUTTON_ACTIVE_TEXT: string;
  BUTTON_CONFIGURATION_MODE: string;
  CELL_BORDER: string;
  BORDER_COLOR: string;
  ENTRY_FOCUS_BG: string;
  ENTRY_TEXT: string;
  INFO_NOTE_BG: string;
  INFO_TEXT: string;
  HEADER_BG: string;
  HEADER_TEXT: string;
  ROW_BG_EVEN: string;
  ROW_BG_ODD: string;
  NODE_DEFAULT: string;
  NODE_HIGHLIGHT: string;
  NODE_OUTLINE_DEFAULT: string;
  NODE_PING_SUCCESS: string;
  NODE_PING_FAILURE: string;
  NODE_PING_PARTIAL_SUCCESS: string;
  Connections: string;
  GROUP_TEXT: string;
  GROUP_OUTLINE: string;
}

export const lightTheme: ThemeColors = {
  FRAME_BG: "#f0f0f0",
  BUTTON_BG: "#e0e0e0",
  BUTTON_TEXT: "#333333",
  BUTTON_ACTIVE_BG: "#3a7bd5",
  BUTTON_ACTIVE_TEXT: "#ffffff",
  BUTTON_CONFIGURATION_MODE: "#ff9800",
  CELL_BORDER: "#cccccc",
  BORDER_COLOR: "#bbbbbb",
  ENTRY_FOCUS_BG: "#ffffff",
  ENTRY_TEXT: "#333333",
  INFO_NOTE_BG: "#ffffffdd",
  INFO_TEXT: "#555555",
  HEADER_BG: "#d0d0d0",
  HEADER_TEXT: "#333333",
  ROW_BG_EVEN: "#ffffff",
  ROW_BG_ODD: "#f5f5f5",
  NODE_DEFAULT: "#5b9bd5",
  NODE_HIGHLIGHT: "#ff6600",
  NODE_OUTLINE_DEFAULT: "#333333",
  NODE_PING_SUCCESS: "#27ae60",
  NODE_PING_FAILURE: "#e74c3c",
  NODE_PING_PARTIAL_SUCCESS: "#f39c12",
  Connections: "#888888",
  GROUP_TEXT: "#333333",
  GROUP_OUTLINE: "#3a7bd5",
};

export const darkTheme: ThemeColors = {
  FRAME_BG: "#1e1e2e",
  BUTTON_BG: "#2a2a3a",
  BUTTON_TEXT: "#d0d0d0",
  BUTTON_ACTIVE_BG: "#3a7bd5",
  BUTTON_ACTIVE_TEXT: "#ffffff",
  BUTTON_CONFIGURATION_MODE: "#ff9800",
  CELL_BORDER: "#444466",
  BORDER_COLOR: "#444466",
  ENTRY_FOCUS_BG: "#2a2a3a",
  ENTRY_TEXT: "#d0d0d0",
  INFO_NOTE_BG: "#1e1e2edd",
  INFO_TEXT: "#aaaacc",
  HEADER_BG: "#2a2a3a",
  HEADER_TEXT: "#d0d0d0",
  ROW_BG_EVEN: "#1e1e2e",
  ROW_BG_ODD: "#24243a",
  NODE_DEFAULT: "#5b9bd5",
  NODE_HIGHLIGHT: "#ff6600",
  NODE_OUTLINE_DEFAULT: "#cccccc",
  NODE_PING_SUCCESS: "#27ae60",
  NODE_PING_FAILURE: "#e74c3c",
  NODE_PING_PARTIAL_SUCCESS: "#f39c12",
  Connections: "#666688",
  GROUP_TEXT: "#ccccdd",
  GROUP_OUTLINE: "#3a7bd5",
};

const ironcladTheme: ThemeColors = {
  FRAME_BG: "#2b2d31",
  BUTTON_BG: "#3a3c42",
  BUTTON_TEXT: "#c8c8c8",
  BUTTON_ACTIVE_BG: "#e09240",
  BUTTON_ACTIVE_TEXT: "#1a1a1a",
  BUTTON_CONFIGURATION_MODE: "#e09240",
  CELL_BORDER: "#555a62",
  BORDER_COLOR: "#555a62",
  ENTRY_FOCUS_BG: "#3a3c42",
  ENTRY_TEXT: "#c8c8c8",
  INFO_NOTE_BG: "#2b2d31dd",
  INFO_TEXT: "#999999",
  HEADER_BG: "#3a3c42",
  HEADER_TEXT: "#c8c8c8",
  ROW_BG_EVEN: "#2b2d31",
  ROW_BG_ODD: "#32343a",
  NODE_DEFAULT: "#5b9bd5",
  NODE_HIGHLIGHT: "#e09240",
  NODE_OUTLINE_DEFAULT: "#c8c8c8",
  NODE_PING_SUCCESS: "#27ae60",
  NODE_PING_FAILURE: "#e74c3c",
  NODE_PING_PARTIAL_SUCCESS: "#f39c12",
  Connections: "#777788",
  GROUP_TEXT: "#c8c8c8",
  GROUP_OUTLINE: "#e09240",
};

const themes: Record<ThemeName, ThemeColors> = {
  light: lightTheme,
  dark: darkTheme,
  ironclad: ironcladTheme,
};

export function getThemeColors(theme: ThemeName): ThemeColors {
  return themes[theme] ?? darkTheme;
}
