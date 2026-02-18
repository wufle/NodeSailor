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

export interface RangeResult {
  label: string;
  devices: DiscoveredDevice[];
}

export interface MergedDevice {
  hostname: string;
  mac_address: string;
  vendor: string;
  open_ports: number[];
  ips: Record<string, string>; // vlanKey -> IP address
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

function deriveFriendlyNameFromMerged(device: MergedDevice): string {
  if (device.hostname) return device.hostname;

  if (device.vendor && device.mac_address) {
    const hexOnly = device.mac_address.replace(/[^0-9A-Fa-f]/g, "");
    const suffix = hexOnly.slice(-6).toUpperCase();
    return `${device.vendor}-${suffix}`;
  }

  const firstIp = Object.values(device.ips)[0] || "";
  const ipSuffix = firstIp.split(".").slice(-2).join(".");
  if (device.open_ports.includes(631) || device.open_ports.includes(9100)) {
    return `Printer-${ipSuffix}`;
  }
  if (device.open_ports.includes(80) || device.open_ports.includes(443) || device.open_ports.includes(8080)) {
    return `Web Device-${ipSuffix}`;
  }

  return firstIp;
}

function deriveWebUrl(device: DiscoveredDevice): string {
  if (device.open_ports.includes(443)) return `https://${device.ip}`;
  if (device.open_ports.includes(80)) return `http://${device.ip}`;
  return "";
}

function deriveWebUrlFromIp(ports: number[], ip: string): string {
  if (ports.includes(443)) return `https://${ip}`;
  if (ports.includes(80)) return `http://${ip}`;
  return "";
}

function sanitizeVlanKey(label: string): string {
  return label.toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "") || "range";
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

export function mergeDevicesByMac(
  rangeResults: RangeResult[]
): {
  devices: MergedDevice[];
  vlanLabels: Record<string, string>;
  vlanLabelOrder: string[];
} {
  const macMap = new Map<string, MergedDevice>();
  const labels: Record<string, string> = {};
  const order: string[] = [];
  const usedKeys = new Set<string>();

  for (const range of rangeResults) {
    let vlanKey = sanitizeVlanKey(range.label);
    // Handle duplicate keys by adding numeric suffix
    if (usedKeys.has(vlanKey)) {
      let counter = 2;
      while (usedKeys.has(`${vlanKey}_${counter}`)) counter++;
      vlanKey = `${vlanKey}_${counter}`;
    }
    usedKeys.add(vlanKey);
    labels[vlanKey] = range.label;
    order.push(vlanKey);

    for (const device of range.devices) {
      const key = device.mac_address || `no-mac-${device.ip}`;

      if (macMap.has(key)) {
        const existing = macMap.get(key)!;
        existing.ips[vlanKey] = device.ip;
        // Merge open ports
        for (const port of device.open_ports) {
          if (!existing.open_ports.includes(port)) {
            existing.open_ports.push(port);
          }
        }
        // Prefer non-empty hostname/vendor
        if (!existing.hostname && device.hostname) {
          existing.hostname = device.hostname;
        }
        if (!existing.vendor && device.vendor) {
          existing.vendor = device.vendor;
        }
      } else {
        macMap.set(key, {
          hostname: device.hostname,
          mac_address: device.mac_address,
          vendor: device.vendor,
          open_ports: [...device.open_ports],
          ips: { [vlanKey]: device.ip },
        });
      }
    }
  }

  return {
    devices: Array.from(macMap.values()),
    vlanLabels: labels,
    vlanLabelOrder: order,
  };
}

export function createNodesFromMergedDiscovery(
  mergedDevices: MergedDevice[],
  vlanConfig: { labels: Record<string, string>; order: string[] },
  layout: "grid" | "circle",
  clearExisting: boolean
): void {
  if (clearExisting) {
    newNetwork();
  }

  vlanLabels.set({ ...vlanConfig.labels });
  vlanLabelOrder.set([...vlanConfig.order]);

  const positions =
    layout === "grid"
      ? computeGridLayout(mergedDevices.length)
      : computeCircleLayout(mergedDevices.length);

  for (let i = 0; i < mergedDevices.length; i++) {
    const d = mergedDevices[i];
    const pos = positions[i];
    const firstIp = Object.values(d.ips)[0] || "";

    const node: NetworkNode = {
      name: deriveFriendlyNameFromMerged(d),
      x: pos.x,
      y: pos.y,
      vlans: { ...d.ips },
      remote_desktop_address: d.open_ports.includes(3389) ? firstIp : "",
      file_path: "",
      web_config_url: deriveWebUrlFromIp(d.open_ports, firstIp),
    };

    addNode(node);
  }

  unsavedChanges.set(true);
  activeDialog.set(null);
  showStartMenu.set(false);
}
