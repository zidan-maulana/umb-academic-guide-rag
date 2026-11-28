import { loadSavedTheme, saveTheme } from "../state/storage.js";
import { setState } from "../state/store.js";

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  const metaTheme = document.querySelector('meta[name="theme-color"]');
  if (metaTheme) {
    metaTheme.setAttribute("content", theme === "dark" ? "#0B1322" : "#3D6BC9");
  }
  setState({ theme }, "theme");
}

export function initTheme() {
  const saved = loadSavedTheme();
  const preferred = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  applyTheme(saved || preferred);
}

export function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme") === "dark" ? "dark" : "light";
  const next = current === "dark" ? "light" : "dark";
  saveTheme(next);
  applyTheme(next);
}
