import { invoke } from "@tauri-apps/api/core";
import { open, save } from "@tauri-apps/plugin-dialog";
import { get } from "svelte/store";
import {
  nodes,
  connections,
  stickyNotes,
  groups,
  vlanLabels,
  vlanLabelOrder,
  customCommands,
  groupColorPresets,
  displayOptions,
} from "../stores/networkStore";
import { unsavedChanges, showStartMenu } from "../stores/uiStore";
import { settings } from "../stores/settingsStore";
import type { NetworkNode } from "../types/network";

let currentFilePath: string | null = null;

function parseNodes(rawNodes: any[]): NetworkNode[] {
  return rawNodes.map((raw) => {
    const vlans: Record<string, string> = {};
    const known = new Set([
      "name",
      "x",
      "y",
      "remote_desktop_address",
      "file_path",
      "web_config_url",
    ]);
    for (const key of Object.keys(raw)) {
      if (!known.has(key)) {
        vlans[key] = raw[key] ?? "";
      }
    }
    return {
      name: raw.name ?? "",
      x: raw.x ?? 0,
      y: raw.y ?? 0,
      remote_desktop_address: raw.remote_desktop_address ?? "",
      file_path: raw.file_path ?? "",
      web_config_url: raw.web_config_url ?? "",
      vlans,
    };
  });
}

function serializeNodes(nodeList: NetworkNode[]): any[] {
  return nodeList.map((node) => {
    const obj: any = {
      name: node.name,
      x: node.x,
      y: node.y,
      remote_desktop_address: node.remote_desktop_address,
      file_path: node.file_path,
      web_config_url: node.web_config_url,
    };
    for (const [key, value] of Object.entries(node.vlans)) {
      obj[key] = value;
    }
    return obj;
  });
}

export async function loadFile(filePath?: string): Promise<void> {
  let path = filePath;
  if (!path) {
    const selected = await open({
      filters: [{ name: "JSON", extensions: ["json"] }],
    });
    if (!selected) return;
    path = selected as string;
  }

  const content: string = await invoke("load_file", { path });
  // Replace NaN values with null to handle legacy/malformed JSON files
  const sanitizedContent = content.replace(/:\s*NaN\b/g, ': null');
  const data = JSON.parse(sanitizedContent);

  nodes.set(parseNodes(data.nodes ?? []));
  connections.set(data.connections ?? []);
  stickyNotes.set(data.stickynotes ?? []);
  groups.set(data.groups ?? []);
  vlanLabels.set(data.vlan_labels ?? {});
  vlanLabelOrder.set(data.vlan_label_order ?? []);
  customCommands.set(data.custom_commands ?? {});
  if (data.group_color_presets) {
    groupColorPresets.set(data.group_color_presets);
  }
  if (data.display_options) {
    displayOptions.set(data.display_options);
  }

  currentFilePath = path;
  unsavedChanges.set(false);
  showStartMenu.set(false);

  // Save last file path to settings
  const currentSettings = get(settings);
  await invoke("save_settings", {
    settings: { ...currentSettings, last_file_path: path },
  });
  settings.update((s) => ({ ...s, last_file_path: path }));
}

export async function saveFile(): Promise<void> {
  let path = currentFilePath;

  // If there's an existing file, ask user what they want to do
  if (path) {
    const choice = await invoke<string>("show_save_dialog", { currentPath: path });

    if (choice === "cancel") {
      return;
    } else if (choice === "new") {
      // Prompt for new file location
      const selected = await save({
        filters: [{ name: "JSON", extensions: ["json"] }],
      });
      if (!selected) return;
      path = selected;
    }
    // If "overwrite", keep the current path
  } else {
    // No existing file, prompt for new location
    const selected = await save({
      filters: [{ name: "JSON", extensions: ["json"] }],
    });
    if (!selected) return;
    path = selected;
  }

  const data = {
    nodes: serializeNodes(get(nodes)),
    connections: get(connections),
    vlan_labels: get(vlanLabels),
    vlan_label_order: get(vlanLabelOrder),
    stickynotes: get(stickyNotes),
    groups: get(groups),
    group_color_presets: get(groupColorPresets),
    custom_commands: get(customCommands),
  };

  const content = JSON.stringify(data, null, 4);
  await invoke("save_file", { path, content });
  currentFilePath = path;
  unsavedChanges.set(false);
}

export function newNetwork(): void {
  nodes.set([]);
  connections.set([]);
  stickyNotes.set([]);
  groups.set([]);
  vlanLabels.set({});
  vlanLabelOrder.set([]);
  customCommands.set({});
  displayOptions.set({});
  currentFilePath = null;
  unsavedChanges.set(false);
  showStartMenu.set(false);
}
