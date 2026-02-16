import { writable, derived } from "svelte/store";
import { currentTheme } from "../stores/uiStore";
import type { BuiltInTheme, ThemeName } from "../stores/uiStore";

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

// Matrix Mode easter egg theme
export const matrixTheme: ThemeColors = {
  FRAME_BG: "#000000",
  BUTTON_BG: "#001a00",
  BUTTON_TEXT: "#00ff00",
  BUTTON_ACTIVE_BG: "#00ff00",
  BUTTON_ACTIVE_TEXT: "#000000",
  BUTTON_CONFIGURATION_MODE: "#00cc00",
  CELL_BORDER: "#003300",
  BORDER_COLOR: "#003300",
  ENTRY_FOCUS_BG: "#001a00",
  ENTRY_TEXT: "#00ff00",
  INFO_NOTE_BG: "#000000dd",
  INFO_TEXT: "#00cc00",
  HEADER_BG: "#001a00",
  HEADER_TEXT: "#00ff00",
  ROW_BG_EVEN: "#000000",
  ROW_BG_ODD: "#001100",
  NODE_DEFAULT: "#00ff00",
  NODE_HIGHLIGHT: "#88ff88",
  NODE_OUTLINE_DEFAULT: "#00ff00",
  NODE_PING_SUCCESS: "#00ff00",
  NODE_PING_FAILURE: "#ff0000",
  NODE_PING_PARTIAL_SUCCESS: "#00cc00",
  Connections: "#00aa00",
  GROUP_TEXT: "#00ff00",
  GROUP_OUTLINE: "#00cc00",
};

const builtInThemes: Record<BuiltInTheme, ThemeColors> = {
  light: lightTheme,
  dark: darkTheme,
  ironclad: ironcladTheme,
};

let customThemes: Record<string, ThemeColors> = {};
let colorOverrides: Record<string, Partial<ThemeColors>> = {};

// Version counter — bump this to make effectiveColors re-derive
const colorVersion = writable(0);

function bumpVersion() {
  colorVersion.update((v) => v + 1);
}

export function getThemeColors(theme: ThemeName): ThemeColors {
  const base = customThemes[theme] ?? builtInThemes[theme as BuiltInTheme] ?? darkTheme;
  const custom = colorOverrides[theme];
  return custom ? { ...base, ...custom } : base;
}

/** Reactive store: re-derives whenever theme or color overrides change */
export const effectiveColors = derived(
  [currentTheme, colorVersion],
  ([theme, _v]) => getThemeColors(theme),
);

export function isBuiltInTheme(name: string): boolean {
  return name in builtInThemes;
}

// --- Color overrides (live editing on top of any theme) ---

export function setColorOverride(theme: ThemeName, key: keyof ThemeColors, value: string) {
  if (!colorOverrides[theme]) colorOverrides[theme] = {};
  colorOverrides[theme]![key] = value;
  bumpVersion();
}

export function resetColorOverrides(theme?: ThemeName) {
  if (theme) {
    delete colorOverrides[theme];
  } else {
    colorOverrides = {};
  }
  bumpVersion();
}

export function loadColorOverrides(overrides: Record<string, Partial<ThemeColors>>) {
  colorOverrides = overrides;
  bumpVersion();
}

export function getColorOverrides(): Record<string, Partial<ThemeColors>> {
  return colorOverrides;
}

// --- Custom themes (saved as full theme presets) ---

export function registerCustomTheme(name: string, colors: ThemeColors) {
  customThemes[name] = { ...colors };
  bumpVersion();
}

export function removeCustomTheme(name: string) {
  delete customThemes[name];
  delete colorOverrides[name];
  bumpVersion();
}

export function loadCustomThemes(themes: Record<string, ThemeColors>) {
  customThemes = themes;
  bumpVersion();
}

export function getCustomThemeNames(): string[] {
  return Object.keys(customThemes);
}

export function getCustomThemes(): Record<string, ThemeColors> {
  return customThemes;
}
