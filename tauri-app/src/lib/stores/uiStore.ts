import { writable, derived } from "svelte/store";

export type BuiltInTheme = "light" | "dark" | "ironclad";
export type ThemeName = BuiltInTheme | (string & {});

function createRefreshableStore<T>(initial: T) {
  let value = initial;
  const subscribers = new Set<(v: T) => void>();

  function notify() {
    for (const fn of subscribers) fn(value);
  }

  return {
    subscribe(fn: (v: T) => void) {
      subscribers.add(fn);
      fn(value);
      return () => { subscribers.delete(fn); };
    },
    set(v: T) {
      value = v;
      notify();
    },
    update(fn: (v: T) => T) {
      value = fn(value);
      notify();
    },
    /** Force all subscribers to re-evaluate, even if value unchanged */
    refresh() {
      notify();
    },
  };
}

export const currentTheme = createRefreshableStore<ThemeName>("dark");
export const isDark = derived(currentTheme, (t) => t !== "light");
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
