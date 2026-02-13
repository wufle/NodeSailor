import { invoke } from "@tauri-apps/api/core";
import { get } from "svelte/store";
import { nodes, pingResults, pingAnimationStates } from "../stores/networkStore";
import { addTerminalEntry } from "../stores/terminalStore";

export async function pingNode(nodeIndex: number): Promise<void> {
  const allNodes = get(nodes);
  const node = allNodes[nodeIndex];
  if (!node) return;

  const ips = Object.values(node.vlans).filter((v) => v && v.trim() !== "");
  if (ips.length === 0) return;

  for (const ip of ips) {
    addTerminalEntry(
      "ping",
      `ping -n 1 ${ip}`,
      `Pinging node "${node.name}" at ${ip}`
    );
  }

  const results: boolean[] = await invoke("ping_ips", { ips });
  pingResults.update((pr) => ({ ...pr, [nodeIndex]: results }));

  // Trigger strobe animation
  const allSuccess = results.every((r) => r);
  pingAnimationStates.update((s) => ({
    ...s,
    [nodeIndex]: allSuccess ? 'success' : 'failure',
  }));

  for (let i = 0; i < ips.length; i++) {
    const status = results[i] ? "Success" : "Failed";
    addTerminalEntry(
      "ping-result",
      `ping -n 1 ${ips[i]}`,
      `Ping ${status} for "${node.name}" at ${ips[i]}`,
      status
    );
  }
}

export async function pingAllNodes(): Promise<void> {
  const allNodes = get(nodes);
  addTerminalEntry(
    "info",
    `ping-all (${allNodes.length} nodes)`,
    `Starting parallel ping of all ${allNodes.length} nodes`
  );

  const pingPromises = [];
  for (let i = 0; i < allNodes.length; i++) {
    pingPromises.push(pingNode(i));
  }
  await Promise.all(pingPromises);

  addTerminalEntry(
    "info",
    `ping-all complete`,
    `Finished pinging all ${allNodes.length} nodes`
  );
}

export function clearPingResults(): void {
  pingResults.set({});
}
