import { writable } from "svelte/store";

export interface AppSettings {
  hide_start_menu?: boolean;
  last_file_path?: string;
  window_geometry?: string;
  auto_load_last_file?: boolean;
  tutorial_completed?: boolean;
  show_canvas_status_bar?: boolean; // Default true for new users
  auto_show_tutorial?: boolean; // Default true for first launch
  disable_strobe_effects?: boolean;
  custom_theme_colors?: Record<string, Record<string, string>>;
  custom_themes?: Record<string, Record<string, string>>;
  last_custom_theme?: string;
}

export const settings = writable<AppSettings>({});
