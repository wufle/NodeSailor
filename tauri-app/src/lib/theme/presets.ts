import type { GroupColorPreset } from "../types/network";

export function getGroupColors(
  presetId: string,
  isDark: boolean,
  presets: GroupColorPreset[]
): { bg: string; border: string } {
  const preset = presets.find((p) => p.id === presetId);
  if (!preset) {
    return isDark
      ? { bg: "#22304a", border: "#3a7bd5" }
      : { bg: "#e3f0ff", border: "#3a7bd5" };
  }
  return isDark
    ? { bg: preset.dark_bg, border: preset.dark_border }
    : { bg: preset.light_bg, border: preset.light_border };
}
