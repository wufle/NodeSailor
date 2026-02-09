import { invoke } from "@tauri-apps/api/core";
import type { NetworkNode } from "../types/network";

export async function getLocalIps(): Promise<string[]> {
  return invoke("get_local_ips");
}

export async function openRemoteDesktop(address: string): Promise<void> {
  await invoke("open_rdp", { address });
}

export async function openFileExplorer(path: string): Promise<void> {
  await invoke("open_file_explorer", { path });
}

export async function openWebBrowser(url: string): Promise<void> {
  await invoke("open_browser", { url });
}

export async function executeCustomCommand(
  template: string,
  node: NetworkNode
): Promise<void> {
  let command = template
    .replace(/\{name\}/g, node.name)
    .replace(/\{rdp\}/g, node.remote_desktop_address)
    .replace(/\{file\}/g, node.file_path)
    .replace(/\{web\}/g, node.web_config_url);

  // Replace {ip} with first non-empty VLAN value
  const firstIp =
    Object.values(node.vlans).find((v) => v && v.trim() !== "") ?? "";
  command = command.replace(/\{ip\}/g, firstIp);

  // Replace VLAN-specific placeholders like {VLAN_100}
  for (const [key, value] of Object.entries(node.vlans)) {
    command = command.replace(new RegExp(`\\{${key}\\}`, "g"), value);
  }

  await invoke("execute_command", { command });
}
