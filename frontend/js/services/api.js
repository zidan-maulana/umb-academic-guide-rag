import { CHAT_ENDPOINT, HEALTH_ENDPOINT, REQUEST_TIMEOUT_MS } from "../config.js";
import { COPY } from "../content/copy.js";
import { parseChatResponse } from "../utils/format.js";

export async function wakeHealth() {
  try {
    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), 5000);
    await fetch(HEALTH_ENDPOINT, { method: "GET", signal: controller.signal });
    window.clearTimeout(timer);
  } catch {
    /* diamkan saat cold start atau offline; error ditangani saat chat dikirim */
  }
}

function mapHttpError(status, body) {
  if (body && body.error && body.error.message) {
    return String(body.error.message);
  }
  if (status === 422) return COPY.errValidation;
  if (status === 429) return COPY.errRateLimit;
  if (status === 504) return COPY.errTimeout;
  if (status >= 500) return COPY.errServer;
  return COPY.errBusy;
}

export async function askBackend(question, filters = null) {
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  const payload = { question };
  if (filters && Object.values(filters).some(Boolean)) {
    payload.filters = filters;
  }

  try {
    const res = await fetch(CHAT_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });

    if (!res.ok) {
      let body = null;
      try {
        body = await res.json();
      } catch {
        body = null;
      }
      throw new Error(mapHttpError(res.status, body));
    }

    const data = await res.json();
    return parseChatResponse(data);
  } catch (err) {
    if (err.name === "AbortError") {
      throw new Error(COPY.errTimeout);
    }
    if (err instanceof TypeError) {
      throw new Error(COPY.errNetwork);
    }
    throw err;
  } finally {
    window.clearTimeout(timer);
  }
}
