
import { ICONS, SUGGESTIONS, PDF_URL } from "./config.js";
import { els, prefersReducedMotion, nearBottom } from "./dom.js";
import { formatTime, renderFormatted } from "./format.js";

let toastTimer = 0;
let skipTypewriter = false;

export function svgNode(html) {
  const wrap = document.createElement("span");
  wrap.innerHTML = html;
  return wrap.firstElementChild;
}

export function showToast(text) {
  els.toast.hidden = false;
  els.toast.textContent = text;
  requestAnimationFrame(() => els.toast.classList.add("show"));
  clearTimeout(toastTimer);
  toastTimer = window.setTimeout(() => {
    els.toast.classList.remove("show");
  }, 2000);
}

export function scrollToLatest(force = false) {
  if (force || nearBottom()) {
    els.messages.scrollTo({
      top: els.messages.scrollHeight,
      behavior: prefersReducedMotion() ? "auto" : "smooth",
    });
    els.jump.hidden = true;
  } else {
    els.jump.hidden = false;
  }
}

export function hideWelcome() {
  if (!els.welcome || els.welcome.hidden) return;
  if (prefersReducedMotion()) {
    els.welcome.hidden = true;
    return;
  }
  els.welcome.classList.add("leaving");
  window.setTimeout(() => {
    els.welcome.hidden = true;
    els.welcome.classList.remove("leaving");
  }, 220);
}

export function renderChips(onSelect) {
  els.chips.textContent = "";
  for (const item of SUGGESTIONS) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "chip";
    btn.appendChild(svgNode(ICONS[item.icon]));
    const label = document.createElement("span");
    label.textContent = item.q;
    btn.appendChild(label);
    btn.addEventListener("click", () => onSelect(item.q));
    els.chips.appendChild(btn);
  }
}

export function renderBadges(parent, pages) {
  if (!pages || !pages.length) return;
  const box = document.createElement("div");
  box.className = "sources";
  const label = document.createElement("div");
  label.className = "sources-label";
  label.textContent = "Sumber";
  box.appendChild(label);
  const row = document.createElement("div");
  row.className = "badge-row";
  pages.forEach((page, index) => {
    const badge = document.createElement("button");
    badge.type = "button";
    badge.className = "badge";
    badge.style.animationDelay = `${index * 60}ms`;
    badge.appendChild(svgNode(ICONS.doc));
    const text = document.createElement("span");
    text.textContent = `Hal. ${page}`;
    badge.appendChild(text);
    badge.setAttribute("aria-label", `Sumber halaman ${page}`);
    badge.addEventListener("click", async () => {
      if (PDF_URL) {
        window.open(`${PDF_URL}#page=${page}`, "_blank", "noopener,noreferrer");
        return;
      }
      try {
        await navigator.clipboard.writeText(`Hal. ${page}`);
        showToast(`Hal. ${page} disalin`);
      } catch {
        showToast("Tidak bisa menyalin");
      }
    });
    row.appendChild(badge);
  });
  box.appendChild(row);
  parent.appendChild(box);
}

export function renderMessage(entry, options = {}) {
  const { animateText = false, onRetry } = options;
  const row = document.createElement("article");
  row.className = `row ${entry.role === "user" ? "row-user" : "row-bot"}`;

  const avatar = document.createElement("div");
  avatar.className = `avatar${entry.role === "user" ? " user" : ""}`;
  avatar.setAttribute("aria-hidden", "true");
  avatar.appendChild(svgNode(entry.role === "user" ? ICONS.user : ICONS.book));

  const col = document.createElement("div");
  col.className = "bubble-col";

  const bubble = document.createElement("div");
  bubble.className = `bubble ${entry.role === "user" ? "bubble-user" : "bubble-bot"}`;
  if (entry.kind === "fallback") bubble.classList.add("fallback");
  if (entry.kind === "error") bubble.classList.add("error");

  const body = document.createElement("div");
  body.className = "bot-body";
  if (entry.role === "bot" && (entry.kind === "fallback" || entry.kind === "error")) {
    const iconWrap = document.createElement("span");
    iconWrap.className = "lead-icon";
    iconWrap.appendChild(svgNode(entry.kind === "error" ? ICONS.warn : ICONS.info));
    body.appendChild(iconWrap);
  }
  const content = document.createElement("div");
  content.className = "content";
  if (entry.role === "user") {
    content.textContent = entry.text;
  } else {
    renderFormatted(content, animateText ? "" : entry.text);
  }
  body.appendChild(content);
  bubble.appendChild(body);

  if (entry.kind === "error" && onRetry) {
    const retry = document.createElement("button");
    retry.type = "button";
    retry.className = "retry-btn";
    retry.textContent = "Coba lagi";
    retry.addEventListener("click", () => onRetry(entry.retryQuestion));
    bubble.appendChild(retry);
  }

  col.appendChild(bubble);

  const meta = document.createElement("div");
  meta.className = "meta";
  const time = document.createElement("time");
  time.className = "time";
  time.dateTime = new Date(entry.ts).toISOString();
  time.textContent = formatTime(entry.ts);
  meta.appendChild(time);

  if (entry.role === "bot" && entry.kind !== "error") {
    const copyBtn = document.createElement("button");
    copyBtn.type = "button";
    copyBtn.className = "copy-btn";
    copyBtn.setAttribute("aria-label", "Salin jawaban");
    copyBtn.appendChild(svgNode(ICONS.copy));
    const copyLabel = document.createElement("span");
    copyLabel.textContent = "Salin";
    copyBtn.appendChild(copyLabel);
    copyBtn.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(entry.text);
        copyBtn.classList.add("copied");
        const done = document.createElement("span");
        done.textContent = "Tersalin";
        copyBtn.replaceChildren(svgNode(ICONS.check), done);
        window.setTimeout(() => {
          copyBtn.classList.remove("copied");
          const label = document.createElement("span");
          label.textContent = "Salin";
          copyBtn.replaceChildren(svgNode(ICONS.copy), label);
        }, 1500);
      } catch {
        showToast("Tidak bisa menyalin");
      }
    });
    meta.appendChild(copyBtn);
  }
  col.appendChild(meta);

  if (entry.role === "bot" && entry.kind === "normal" && entry.pages && entry.pages.length) {
    const badgeHost = document.createElement("div");
    badgeHost.className = "badge-host";
    if (!animateText) renderBadges(badgeHost, entry.pages);
    col.appendChild(badgeHost);
    row._badgeHost = badgeHost;
  }

  if (entry.role === "user") {
    row.appendChild(col);
    row.appendChild(avatar);
  } else {
    row.appendChild(avatar);
    row.appendChild(col);
  }

  els.messages.appendChild(row);
  scrollToLatest(true);
  return { row, content, bubble };
}

export function showTyping() {
  const row = document.createElement("div");
  row.className = "row row-bot";
  row.id = "typing-row";
  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.setAttribute("aria-hidden", "true");
  avatar.appendChild(svgNode(ICONS.book));
  const col = document.createElement("div");
  col.className = "bubble-col";
  const bubble = document.createElement("div");
  bubble.className = "bubble bubble-bot";
  const typing = document.createElement("div");
  typing.className = "typing";
  const dots = document.createElement("div");
  dots.className = "dots";
  dots.innerHTML = "<span></span><span></span><span></span>";
  typing.appendChild(dots);
  const note = document.createElement("span");
  note.className = "typing-note";
  note.hidden = true;
  note.textContent = "Sedang mencari di panduan…";
  typing.appendChild(note);
  bubble.appendChild(typing);
  col.appendChild(bubble);
  row.appendChild(avatar);
  row.appendChild(col);
  els.messages.appendChild(row);
  scrollToLatest(true);
  const timer = window.setTimeout(() => {
    note.hidden = false;
  }, 6000);
  return () => {
    window.clearTimeout(timer);
    row.remove();
  };
}

export function typewriter(contentEl, fullText, onDone) {
  if (prefersReducedMotion()) {
    renderFormatted(contentEl, fullText);
    onDone();
    return () => {};
  }
  skipTypewriter = false;
  const total = fullText.length;
  const maxMs = 2500;
  const interval = Math.max(4, Math.min(12, maxMs / Math.max(total, 1)));
  let i = 0;
  const tick = () => {
    if (skipTypewriter) {
      renderFormatted(contentEl, fullText);
      onDone();
      return;
    }
    i += 1;
    renderFormatted(contentEl, fullText.slice(0, i));
    scrollToLatest(false);
    if (i >= total) {
      onDone();
      return;
    }
    window.setTimeout(tick, interval);
  };
  tick();
  return () => {
    skipTypewriter = true;
  };
}

export function setComposerEnabled(on, loading = false) {
  els.input.disabled = !on;
  updateSendState(loading);
  if (on) els.input.focus();
}

export function updateSendState(loading = false) {
  const empty = els.input.value.trim().length === 0;
  els.send.disabled = loading || empty;
}

export function resizeInput() {
  const el = els.input;
  el.style.height = "auto";
  const max = 16 * 8.25;
  el.style.height = `${Math.min(el.scrollHeight, max)}px`;
}
