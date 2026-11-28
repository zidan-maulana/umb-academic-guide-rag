import { TOAST_DURATION_MS } from "../config.js";
import { el, qs } from "../utils/dom.js";

let toastEl = null;
let hideTimer = 0;

export function initToast() {
  const root = qs("#toast-root");
  if (!root) return;
  toastEl = el("div", { className: "toast", hidden: true });
  root.appendChild(toastEl);
}

export function showToast(message) {
  if (!toastEl) return;
  toastEl.textContent = message;
  toastEl.hidden = false;
  window.requestAnimationFrame(() => toastEl.classList.add("is-visible"));

  window.clearTimeout(hideTimer);
  hideTimer = window.setTimeout(() => {
    toastEl.classList.remove("is-visible");
    window.setTimeout(() => {
      if (!toastEl.classList.contains("is-visible")) {
        toastEl.hidden = true;
      }
    }, 240);
  }, TOAST_DURATION_MS);
}
