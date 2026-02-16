// Matrix Mode easter egg — toggled with Ctrl+Shift+M
import { writable } from "svelte/store";
import type { ThemeName } from "./uiStore";

export const matrixMode = writable<boolean>(false);
export const previousTheme = writable<ThemeName>("dark");
