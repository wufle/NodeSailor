export interface NetworkNode {
  name: string;
  x: number;
  y: number;
  vlans: Record<string, string>;
  remote_desktop_address: string;
  file_path: string;
  web_config_url: string;
}

export interface NetworkConnection {
  from: number;
  to: number;
  label: string;
  connectioninfo?: string;
  label_pos?: number;
  waypoints?: [number, number][];
}

export interface GroupRect {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  name: string;
  color: string;
  light_bg: string;
  light_border: string;
  dark_bg: string;
  dark_border: string;
  color_preset_id: string;
}

export interface StickyNote {
  text: string;
  x: number;
  y: number;
}

export interface CustomCommand {
  template: string;
  applicable_nodes: string[] | null;
}

export interface GroupColorPreset {
  id: string;
  name: string;
  light_bg: string;
  light_border: string;
  dark_bg: string;
  dark_border: string;
}

export interface DisplayOptions {
  show_connections?: boolean;
  show_connection_labels?: boolean;
  show_notes?: boolean;
  show_groups?: boolean;
  node_size?: number;
  visible_vlans?: string[] | null; // null = show all, empty array = show none, array with keys = show those
}
