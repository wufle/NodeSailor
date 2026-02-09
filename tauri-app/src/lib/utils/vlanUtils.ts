import type { NetworkNode } from "../types/network";

export function getPopulatedVlans(
  node: NetworkNode,
  vlanLabelOrder: string[]
): { key: string; value: string }[] {
  const result: { key: string; value: string }[] = [];
  for (const key of vlanLabelOrder) {
    const value = node.vlans[key];
    if (value && value.trim() !== "") {
      result.push({ key, value });
    }
  }
  return result;
}
