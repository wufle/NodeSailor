import { writable } from "svelte/store";

export interface AppSettings {
  hide_start_menu?: boolean;
  last_file_path?: string;
  window_geometry?: string;
}

export const settings = writable<AppSettings>({});
