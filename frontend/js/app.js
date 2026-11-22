
import { MAX_QUESTION } from "./config.js";
import { els, nearBottom } from "./dom.js";
import { loadTheme, saveTheme, loadHistory, saveHistory } from "./storage.js";
import { askBackend } from "./api.js";
import {
  hideWelcome,
  renderChips,
  renderBadges,
  renderMessage,
  showTyping,
  typewriter,
  setComposerEnabled,
  updateSendState,
  resizeInput,
  scrollToLatest,
  showToast,
} from "./ui.js";

let history = [];
let loading = false;
let lastQuestion = "";
let confirmTimer = 0;

export async function sendMessage(raw, { fromRetry = false } = {}) {
  const question = String(raw || "").trim().slice(0, MAX_QUESTION);
  if (!question || loading) return;

  lastQuestion = question;
  hideWelcome();

  if (!fromRetry) {
    const userEntry = { role: "user", text: question, ts: Date.now(), kind: "user" };
    renderMessage(userEntry, { onRetry: handleRetry });
    history.push(userEntry);
    saveHistory(history);
  }

  els.input.value = "";
  resizeInput();
  loading = true;
  setComposerEnabled(false, loading);
  const stopTyping = showTyping();

  try {
    const result = await askBackend(question);
    stopTyping();
    const kind = result.isFallback ? "fallback" : "normal";
    const entry = {
      role: "bot",
      text: result.answer,
      ts: Date.now(),
      kind,
      pages: result.pages,
    };

    history.push(entry);
    saveHistory(history);

    const view = renderMessage(entry, { animateText: true, onRetry: handleRetry });
    const cancel = typewriter(view.content, result.answer, () => {
      view.bubble.removeEventListener("click", cancel);
      if (view.row._badgeHost && result.pages.length) {
        renderBadges(view.row._badgeHost, result.pages);
      }
      loading = false;
      setComposerEnabled(true, loading);
    });
    view.bubble.addEventListener("click", cancel);
  } catch (err) {
    stopTyping();
    const errorEntry = {
      role: "bot",
      text: err.message || "Terjadi kendala. Coba lagi.",
      ts: Date.now(),
      kind: "error",
      retryQuestion: question,
    };
    history.push(errorEntry);
    saveHistory(history);

    renderMessage(errorEntry, { onRetry: handleRetry });
    loading = false;
    setComposerEnabled(true, loading);
  }
}

function handleRetry(questionToRetry) {
  sendMessage(questionToRetry || lastQuestion, { fromRetry: true });
}

export function restoreHistory() {
  history = loadHistory();
  if (!history.length) {
    els.welcome.hidden = false;
    return;
  }
  els.welcome.hidden = true;
  for (const entry of history) {
    renderMessage(entry, { animateText: false, onRetry: handleRetry });
  }
}

export function clearConversation() {
  history = [];
  saveHistory(history);
  els.messages.querySelectorAll(".row").forEach((n) => n.remove());
  els.welcome.hidden = false;
  els.jump.hidden = true;
  showToast("Percakapan dihapus");
  els.input.focus();
}

function hideConfirm() {
  els.confirm.hidden = true;
  els.clear.hidden = false;
  window.clearTimeout(confirmTimer);
}

// Event Listeners
els.form.addEventListener("submit", (event) => {
  event.preventDefault();
  sendMessage(els.input.value);
});

els.input.addEventListener("input", () => {
  resizeInput();
  updateSendState(loading);
});

els.input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendMessage(els.input.value);
  }
});

els.theme.addEventListener("click", () => {
  const current = document.documentElement.getAttribute("data-theme");
  const next = current === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  saveTheme(next);
});

els.clear.addEventListener("click", () => {
  els.clear.hidden = true;
  els.confirm.hidden = false;
  confirmTimer = window.setTimeout(hideConfirm, 4000);
});

els.confirmYes.addEventListener("click", () => {
  hideConfirm();
  clearConversation();
});

els.confirmNo.addEventListener("click", hideConfirm);

els.jump.addEventListener("click", () => scrollToLatest(true));

els.messages.addEventListener("scroll", () => {
  els.jump.hidden = nearBottom();
});

// Inisialisasi awal
loadTheme();
renderChips((q) => sendMessage(q));
restoreHistory();
updateSendState(loading);
resizeInput();
els.input.focus();
