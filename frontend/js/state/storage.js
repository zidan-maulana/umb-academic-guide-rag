import { HISTORY_KEY, THEME_KEY } from "../config.js";

export function loadSavedTheme() {
  try {
    const val = localStorage.getItem(THEME_KEY);
    return val === "light" || val === "dark" ? val : "";
  } catch {
    return "";
  }
}

export function saveTheme(theme) {
  try {
    localStorage.setItem(THEME_KEY, theme);
  } catch {
    /* abaikan saat storage penuh atau diblokir */
  }
}

export function loadHistory() {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function saveHistory(messages) {
  try {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(messages));
  } catch {
    /* abaikan kegagalan penyimpanan */
  }
}
