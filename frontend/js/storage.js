/**
 * Pengelolaan tema dan riwayat percakapan di LocalStorage.
 */
import { THEME_KEY, HISTORY_KEY } from "./config.js";

export function loadTheme() {
  let theme = "";
  try {
    theme = localStorage.getItem(THEME_KEY) || "";
  } catch {
    theme = "";
  }
  if (theme !== "light" && theme !== "dark") {
    theme = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  document.documentElement.setAttribute("data-theme", theme);
  return theme;
}

export function saveTheme(theme) {
  try {
    localStorage.setItem(THEME_KEY, theme);
  } catch {
    /* storage penuh atau diblokir */
  }
}

export function loadHistory() {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function saveHistory(history) {
  try {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
  } catch {
    /* abaikan kegagalan penyimpanan */
  }
}
