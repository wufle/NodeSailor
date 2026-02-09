import { writable, derived } from "svelte/store";

export type ThemeName = "light" | "dark" | "ironclad";

export const currentTheme = writable<ThemeName>("dark");
export const isDark = derived(currentTheme, (t) => t === "dark" || t === "ironclad");
export const mode = writable<"Operator" | "Configuration">("Operator");
export const showStartMenu = writable(false);
export const unsavedChanges = writable(false);
export const activeDialog = writable<string | null>(null);

export const zoom = writable(1);
export const panX = writable(0);
export const panY = writable(0);
export const zoomPercent = derived(zoom, (z) => Math.round(z * 100));

export const selectedNodeIndex = writable<number | null>(null);
export const hoveredNodeIndex = writable<number | null>(null);
export const previousSelectedNodeIndex = writable<number | null>(null);
export const groupsModeActive = writable(false);
export const connectionStartNodeIndex = writable<number | null>(null);

export const contextMenu = writable({
  visible: false,
  x: 0,
  y: 0,
  nodeIndex: null as number | null,
  connectionIndex: null as number | null,
});
