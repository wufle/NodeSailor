import { writable } from "svelte/store";

export interface AppSettings {
  hide_start_menu?: boolean;
  last_file_path?: string;
  window_geometry?: string;
  auto_load_last_file?: boolean;
}

export const settings = writable<AppSettings>({});
