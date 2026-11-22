/**
 * Komunikasi HTTP dengan backend FastAPI.
 */
import { API_URL, REQUEST_TIMEOUT_MS } from "./config.js";
import { parseChatResponse } from "./format.js";

export async function askBackend(question) {
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
      signal: controller.signal,
    });
    if (!res.ok) {
      let message = "Layanan sedang sibuk. Coba beberapa saat lagi.";
      try {
        const err = await res.json();
        if (err && err.error && err.error.message) message = String(err.error.message);
      } catch {
        if (res.status >= 500) message = "Server sedang bermasalah. Coba lagi.";
      }
      throw new Error(message);
    }
    const data = await res.json();
    return parseChatResponse(data);
  } catch (err) {
    if (err.name === "AbortError") {
      throw new Error("Pencarian terlalu lama. Coba kirim ulang.");
    }
    if (err instanceof TypeError) {
      throw new Error("Tidak bisa terhubung ke server. Pastikan backend berjalan, lalu coba lagi.");
    }
    throw err;
  } finally {
    window.clearTimeout(timer);
  }
}
