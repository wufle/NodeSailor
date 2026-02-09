import { invoke } from "@tauri-apps/api/core";
import { get } from "svelte/store";
import { nodes, pingResults } from "../stores/networkStore";

export async function pingNode(nodeIndex: number): Promise<void> {
  const allNodes = get(nodes);
  const node = allNodes[nodeIndex];
  if (!node) return;

  const ips = Object.values(node.vlans).filter((v) => v && v.trim() !== "");
  if (ips.length === 0) return;

  const results: boolean[] = await invoke("ping_ips", { ips });
  pingResults.update((pr) => ({ ...pr, [nodeIndex]: results }));
}

export async function pingAllNodes(): Promise<void> {
  const allNodes = get(nodes);
  for (let i = 0; i < allNodes.length; i++) {
    await pingNode(i);
  }
}

export function clearPingResults(): void {
  pingResults.set({});
}
