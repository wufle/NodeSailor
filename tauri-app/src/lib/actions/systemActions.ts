import { invoke } from "@tauri-apps/api/core";
import { get } from "svelte/store";
import type { NetworkNode } from "../types/network";
import { addTerminalEntry } from "../stores/terminalStore";
import { nodes, pingResults } from "../stores/networkStore";

export async function getLocalIps(): Promise<string[]> {
  addTerminalEntry(
    "system",
    "get_local_ips",
    "Detecting local IP addresses"
  );
  const ips: string[] = await invoke("get_local_ips");
  addTerminalEntry(
    "info",
    `Found ${ips.length} local IP(s)`,
    `Local IPs: ${ips.join(", ") || "none found"}`,
    ips.join(", ")
  );
  return ips;
}

export async function openRemoteDesktop(address: string): Promise<void> {
  addTerminalEntry(
    "system",
    `mstsc /v:${address}`,
    `Opening Remote Desktop connection to ${address}`
  );
  await invoke("open_rdp", { address });
}

export async function openFileExplorer(path: string): Promise<void> {
  addTerminalEntry(
    "system",
    `explorer ${path}`,
    `Opening File Explorer at ${path}`
  );
  await invoke("open_file_explorer", { path });
}

export async function openWebBrowser(url: string): Promise<void> {
  addTerminalEntry(
    "system",
    `cmd /c start ${url}`,
    `Opening web browser to ${url}`
  );
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

  addTerminalEntry(
    "custom",
    `cmd /c start cmd /k ${command}`,
    `Running custom command on node "${node.name}": ${command}`
  );

  await invoke("execute_command", { command });
}

export async function highlightMatchingNodes(): Promise<void> {
  try {
    const localIps = await getLocalIps();
    const allNodes = get(nodes);
    const matchingIndices: number[] = [];

    for (let i = 0; i < allNodes.length; i++) {
      const node = allNodes[i];
      const vlanValues = Object.values(node.vlans);
      if (vlanValues.some((ip) => localIps.includes(ip))) {
        matchingIndices.push(i);
      }
    }

    if (matchingIndices.length > 0) {
      const matchedNames = matchingIndices.map((idx) => allNodes[idx].name);
      addTerminalEntry(
        "info",
        "who-am-i",
        `This machine is ${matchedNames.join(", ")}`,
        matchedNames.join(", ")
      );

      // Flash matching nodes 3 times quickly
      for (let flash = 0; flash < 3; flash++) {
        const highlightState: Record<number, boolean[]> = {};
        for (const idx of matchingIndices) {
          highlightState[idx] = [true];
        }
        pingResults.set(highlightState);

        await new Promise((resolve) => setTimeout(resolve, 200));

        pingResults.set({});

        await new Promise((resolve) => setTimeout(resolve, 150));
      }

      // Leave highlighted after flashing
      const finalHighlight: Record<number, boolean[]> = {};
      for (const idx of matchingIndices) {
        finalHighlight[idx] = [true];
      }
      pingResults.set(finalHighlight);
    } else {
      addTerminalEntry(
        "info",
        "who-am-i",
        "No matching node found for this machine's IP addresses"
      );
      pingResults.set({});
    }
  } catch (error) {
    console.error("Who am I failed:", error);
    addTerminalEntry(
      "error",
      "who-am-i",
      `Failed to identify local node: ${error}`
    );
    pingResults.set({});
  }
}
