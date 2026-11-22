/**
 * Format teks, parsing Markdown sederhana, waktu, dan respons API.
 */
import { FALLBACK_TEXT } from "./config.js";

export function formatTime(ts) {
  const d = new Date(ts);
  const hh = String(d.getHours()).padStart(2, "0");
  const mm = String(d.getMinutes()).padStart(2, "0");
  return `${hh}.${mm}`;
}

export function uniquePages(values) {
  const pages = [];
  for (const value of values) {
    const n = Number(value);
    if (Number.isInteger(n) && n > 0 && !pages.includes(n)) pages.push(n);
  }
  pages.sort((a, b) => a - b);
  return pages;
}

export function parseChatResponse(data) {
  let payload = data;
  if (payload && typeof payload.answer === "object" && payload.answer) {
    payload = payload.answer;
  }
  const answer = String(payload.answer || "").trim();
  let pages = [];
  if (Array.isArray(payload.pages)) {
    pages = uniquePages(payload.pages);
  } else if (Array.isArray(data.sources)) {
    pages = uniquePages(data.sources.map((s) => s && s.halaman));
  }
  const isFallback =
    payload.is_fallback === true ||
    data.status === "not_found" ||
    answer === FALLBACK_TEXT;
  return {
    answer: answer || FALLBACK_TEXT,
    pages: isFallback ? [] : pages,
    isFallback,
  };
}

export function appendInlineFormat(parent, text) {
  const lines = String(text).split("\n");
  lines.forEach((line, lineIndex) => {
    if (lineIndex > 0) parent.appendChild(document.createElement("br"));
    const parts = line.split(/(\*\*[^*]+\*\*)/g);
    for (const part of parts) {
      if (part.startsWith("**") && part.endsWith("**") && part.length > 4) {
        const strong = document.createElement("strong");
        strong.textContent = part.slice(2, -2);
        parent.appendChild(strong);
      } else if (part) {
        parent.appendChild(document.createTextNode(part));
      }
    }
  });
}

export function renderFormatted(container, text) {
  container.textContent = "";
  const lines = String(text).replace(/\r\n/g, "\n").split("\n");
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    const bullet = line.match(/^\s*[-*]\s+(.*)$/);
    const numbered = line.match(/^\s*\d+[.)]\s+(.*)$/);
    if (bullet || numbered) {
      const list = document.createElement(bullet ? "ul" : "ol");
      while (i < lines.length) {
        const b = lines[i].match(/^\s*[-*]\s+(.*)$/);
        const n = lines[i].match(/^\s*\d+[.)]\s+(.*)$/);
        const itemText = bullet ? b && b[1] : n && n[1];
        if (!itemText && itemText !== "") break;
        if (bullet && !b) break;
        if (!bullet && !n) break;
        const li = document.createElement("li");
        appendInlineFormat(li, (b || n)[1]);
        list.appendChild(li);
        i += 1;
      }
      container.appendChild(list);
      continue;
    }
    if (line.trim() === "") {
      i += 1;
      continue;
    }
    const para = document.createElement("p");
    const chunk = [line];
    i += 1;
    while (
      i < lines.length &&
      lines[i].trim() !== "" &&
      !/^\s*[-*]\s+/.test(lines[i]) &&
      !/^\s*\d+[.)]\s+/.test(lines[i])
    ) {
      chunk.push(lines[i]);
      i += 1;
    }
    appendInlineFormat(para, chunk.join("\n"));
    container.appendChild(para);
  }
}
