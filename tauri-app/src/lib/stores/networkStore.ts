import { writable, get } from "svelte/store";
import type {
  NetworkNode,
  NetworkConnection,
  StickyNote,
  GroupRect,
  GroupColorPreset,
  CustomCommand,
  DisplayOptions,
} from "../types/network";
import { unsavedChanges } from "./uiStore";

export const nodes = writable<NetworkNode[]>([]);
export const connections = writable<NetworkConnection[]>([]);
export const stickyNotes = writable<StickyNote[]>([]);
export const groups = writable<GroupRect[]>([]);
export const displayOptions = writable<DisplayOptions>({});
export const pingResults = writable<Record<number, boolean[]>>({});
export const hostNodeIndices = writable<Set<number>>(new Set());
export const vlanLabels = writable<Record<string, string>>({});
export const vlanLabelOrder = writable<string[]>([]);
export const customCommands = writable<Record<string, string | CustomCommand>>(
  {}
);
export const groupColorPresets = writable<GroupColorPreset[]>([
  {
    id: "preset1",
    name: "Classic Blue",
    light_bg: "#e3f0ff",
    light_border: "#3a7bd5",
    dark_bg: "#22304a",
    dark_border: "#3a7bd5",
  },
  {
    id: "preset2",
    name: "Sunset",
    light_bg: "#ffe5d0",
    light_border: "#ff7f50",
    dark_bg: "#4a2c23",
    dark_border: "#ff7f50",
  },
  {
    id: "preset3",
    name: "Mint",
    light_bg: "#e0fff4",
    light_border: "#2ecc71",
    dark_bg: "#204034",
    dark_border: "#2ecc71",
  },
  {
    id: "preset4",
    name: "Lavender",
    light_bg: "#f3e8ff",
    light_border: "#a259e6",
    dark_bg: "#2d234a",
    dark_border: "#a259e6",
  },
  {
    id: "preset5",
    name: "Slate",
    light_bg: "#f0f4f8",
    light_border: "#607d8b",
    dark_bg: "#232b32",
    dark_border: "#607d8b",
  },
  {
    id: "preset6",
    name: "Contrast",
    light_bg: "#ffffff",
    light_border: "#000000",
    dark_bg: "#000000",
    dark_border: "#ffffff",
  },
]);

export function addNode(node: NetworkNode): void {
  nodes.update((n) => [...n, node]);
  unsavedChanges.set(true);
}

export function updateNode(
  index: number,
  partial: Partial<NetworkNode>
): void {
  nodes.update((n) => {
    const copy = [...n];
    if (copy[index]) {
      copy[index] = { ...copy[index], ...partial };
    }
    return copy;
  });
  unsavedChanges.set(true);
}

export function removeNode(index: number): void {
  nodes.update((n) => n.filter((_, i) => i !== index));
  // Also remove connections referencing this node and adjust indices
  connections.update((conns) =>
    conns
      .filter((c) => c.from !== index && c.to !== index)
      .map((c) => ({
        ...c,
        from: c.from > index ? c.from - 1 : c.from,
        to: c.to > index ? c.to - 1 : c.to,
      }))
  );
  unsavedChanges.set(true);
}

export function moveNode(index: number, x: number, y: number): void {
  nodes.update((n) => {
    const copy = [...n];
    if (copy[index]) {
      copy[index] = { ...copy[index], x, y };
    }
    return copy;
  });
  unsavedChanges.set(true);
}

export function addConnection(conn: NetworkConnection): void {
  connections.update((c) => [...c, conn]);
  unsavedChanges.set(true);
}

export function updateConnection(
  index: number,
  partial: Partial<NetworkConnection>
): void {
  connections.update((c) => {
    const copy = [...c];
    if (copy[index]) {
      copy[index] = { ...copy[index], ...partial };
    }
    return copy;
  });
  unsavedChanges.set(true);
}

export function removeConnection(index: number): void {
  connections.update((c) => c.filter((_, i) => i !== index));
  unsavedChanges.set(true);
}

export function addStickyNote(note: StickyNote): void {
  stickyNotes.update((n) => [...n, note]);
  unsavedChanges.set(true);
}

export function removeStickyNote(index: number): void {
  stickyNotes.update((n) => n.filter((_, i) => i !== index));
  unsavedChanges.set(true);
}

export function addGroup(group: GroupRect): void {
  groups.update((g) => [...g, group]);
  unsavedChanges.set(true);
}

export function updateGroup(
  index: number,
  partial: Partial<GroupRect>
): void {
  groups.update((g) => {
    const copy = [...g];
    if (copy[index]) {
      copy[index] = { ...copy[index], ...partial };
    }
    return copy;
  });
  unsavedChanges.set(true);
}

export function removeGroup(index: number): void {
  groups.update((g) => g.filter((_, i) => i !== index));
  unsavedChanges.set(true);
}
