import {
  nodes,
  connections,
  vlanLabels,
  vlanLabelOrder,
  addNode,
} from "../stores/networkStore";
import { unsavedChanges, showStartMenu, activeDialog } from "../stores/uiStore";
import { newNetwork } from "./fileActions";
import type { NetworkNode } from "../types/network";

export interface DiscoveredDevice {
  ip: string;
  hostname: string;
  mac_address: string;
  vendor: string;
  open_ports: number[];
}

function computeGridLayout(count: number): { x: number; y: number }[] {
  const SPACING = 180;
  const START_X = 100;
  const START_Y = 100;
  const cols = Math.ceil(Math.sqrt(count));
  const positions: { x: number; y: number }[] = [];

  for (let i = 0; i < count; i++) {
    const col = i % cols;
    const row = Math.floor(i / cols);
    positions.push({
      x: START_X + col * SPACING,
      y: START_Y + row * SPACING,
    });
  }
  return positions;
}

function computeCircleLayout(count: number): { x: number; y: number }[] {
  const CENTER_X = 600;
  const CENTER_Y = 500;
  const MIN_RADIUS = 200;
  const RADIUS = Math.max(MIN_RADIUS, count * 25);
  const positions: { x: number; y: number }[] = [];

  for (let i = 0; i < count; i++) {
    const angle = (2 * Math.PI * i) / count - Math.PI / 2;
    positions.push({
      x: CENTER_X + RADIUS * Math.cos(angle),
      y: CENTER_Y + RADIUS * Math.sin(angle),
    });
  }
  return positions;
}

function deriveFriendlyName(device: DiscoveredDevice): string {
  // 1. Hostname if available
  if (device.hostname) return device.hostname;

  // 2. Vendor + last 3 MAC octets (e.g. "Samsung-D4E5F6")
  if (device.vendor && device.mac_address) {
    const hexOnly = device.mac_address.replace(/[^0-9A-Fa-f]/g, "");
    const suffix = hexOnly.slice(-6).toUpperCase();
    return `${device.vendor}-${suffix}`;
  }

  // 3. Device type from ports + IP last octet
  const ipSuffix = device.ip.split(".").slice(-2).join(".");
  if (device.open_ports.includes(631) || device.open_ports.includes(9100)) {
    return `Printer-${ipSuffix}`;
  }
  if (device.open_ports.includes(80) || device.open_ports.includes(443) || device.open_ports.includes(8080)) {
    return `Web Device-${ipSuffix}`;
  }

  // 4. Just the IP
  return device.ip;
}

function deriveWebUrl(device: DiscoveredDevice): string {
  if (device.open_ports.includes(443)) return `https://${device.ip}`;
  if (device.open_ports.includes(80)) return `http://${device.ip}`;
  return "";
}

export function createNodesFromDiscovery(
  devices: DiscoveredDevice[],
  layout: "grid" | "circle",
  clearExisting: boolean
): void {
  if (clearExisting) {
    newNetwork();
  }

  // Set up a VLAN for the discovered IP addresses
  vlanLabels.set({ ip: "IP Address" });
  vlanLabelOrder.set(["ip"]);

  const positions =
    layout === "grid"
      ? computeGridLayout(devices.length)
      : computeCircleLayout(devices.length);

  for (let i = 0; i < devices.length; i++) {
    const d = devices[i];
    const pos = positions[i];

    const node: NetworkNode = {
      name: deriveFriendlyName(d),
      x: pos.x,
      y: pos.y,
      vlans: { ip: d.ip },
      remote_desktop_address: d.open_ports.includes(3389) ? d.ip : "",
      file_path: "",
      web_config_url: deriveWebUrl(d),
    };

    addNode(node);
  }

  unsavedChanges.set(true);
  activeDialog.set(null);
  showStartMenu.set(false);
}
