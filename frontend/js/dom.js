/**
 * Referensi elemen DOM dan fungsi bantu viewport/aksesibilitas.
 */
export const els = {
  messages: document.getElementById("messages"),
  welcome: document.getElementById("welcome"),
  chips: document.getElementById("chips"),
  input: document.getElementById("question-input"),
  send: document.getElementById("send-btn"),
  form: document.getElementById("composer"),
  theme: document.getElementById("theme-toggle"),
  clear: document.getElementById("clear-chat"),
  confirm: document.getElementById("clear-confirm"),
  confirmYes: document.getElementById("confirm-yes"),
  confirmNo: document.getElementById("confirm-no"),
  jump: document.getElementById("jump-latest"),
  toast: document.getElementById("toast"),
};

export function prefersReducedMotion() {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export function nearBottom() {
  const el = els.messages;
  return el.scrollHeight - el.scrollTop - el.clientHeight < 80;
}
