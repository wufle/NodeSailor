import { writable } from "svelte/store";

export type TerminalEntryType =
  | "ping"
  | "ping-result"
  | "system"
  | "custom"
  | "info"
  | "error";

export interface TerminalEntry {
  id: number;
  timestamp: Date;
  type: TerminalEntryType;
  command: string;
  description: string;
  result?: string;
}

let nextId = 1;
const MAX_ENTRIES = 1000;

export const terminalEntries = writable<TerminalEntry[]>([]);
export const terminalVisible = writable(false);
export const terminalHeight = writable(200);

export function addTerminalEntry(
  type: TerminalEntryType,
  command: string,
  description: string,
  result?: string
): void {
  terminalEntries.update((entries) => {
    const newEntry: TerminalEntry = {
      id: nextId++,
      timestamp: new Date(),
      type,
      command,
      description,
      result,
    };
    const updated = [...entries, newEntry];
    if (updated.length > MAX_ENTRIES) {
      return updated.slice(updated.length - MAX_ENTRIES);
    }
    return updated;
  });
}

export function clearTerminal(): void {
  terminalEntries.set([]);
}
