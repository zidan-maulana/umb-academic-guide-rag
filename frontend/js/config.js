function readMeta(name) {
  if (typeof document === "undefined") return "";
  const el = document.querySelector(`meta[name="${name}"]`);
  return el ? el.getAttribute("content").trim() : "";
}

function resolveApiBaseUrl() {
  const win = typeof window !== "undefined" ? window : null;
  const fromGlobal = win && win.__UMB_CONFIG__ && win.__UMB_CONFIG__.API_BASE_URL;
  if (fromGlobal) return String(fromGlobal).replace(/\/+$/, "");

  const fromMeta = readMeta("api-base-url");
  if (fromMeta) return fromMeta.replace(/\/+$/, "");

  if (!win) return "http://localhost:8000";
  const host = win.location.hostname;
  if (host === "localhost" || host === "127.0.0.1" || win.location.protocol === "file:") {
    return "http://localhost:8000";
  }
  return "";
}

export const API_BASE_URL = resolveApiBaseUrl();
export const CHAT_ENDPOINT = `${API_BASE_URL}/api/v1/chat`;
export const HEALTH_ENDPOINT = `${API_BASE_URL}/api/v1/health`;
export const PDF_URL =
  (typeof window !== "undefined" && window.__UMB_CONFIG__ && window.__UMB_CONFIG__.PDF_URL) ||
  readMeta("pdf-url") ||
  "";

export const REQUEST_TIMEOUT_MS = 60000;
export const TYPING_NOTE_DELAY_MS = 6000;
export const TYPEWRITER_CHAR_MS = 12;
export const TYPEWRITER_MAX_MS = 2500;
export const TRANSITION_ENTER_MS = 900;
export const TRANSITION_BACK_MS = 600;
export const CLEAR_CONFIRM_MS = 4000;
export const TOAST_DURATION_MS = 2000;
export const MAX_QUESTION = 500;

export const FALLBACK_TEXT = "Informasi tidak ditemukan di panduan.";
export const HISTORY_KEY = "umb-guide-history";
export const THEME_KEY = "umb-guide-theme";

export const GREETING_REGEX =
  /^(halo|hallo|hai|hi|hey|hei|p|assalamu\s*['’]?alaikum|assalamualaikum|selamat\s+(pagi|siang|sore|malam))\b[!?.]*$/i;
