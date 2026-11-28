import { FALLBACK_TEXT } from "../config.js";

export function formatTime(ts) {
  const d = new Date(ts);
  const hh = String(d.getHours()).padStart(2, "0");
  const mm = String(d.getMinutes()).padStart(2, "0");
  return `${hh}.${mm}`;
}

export function formatModeLabel(mode) {
  if (!mode || typeof mode !== "object") return "";
  const parts = [mode.bagian, mode.fakultas, mode.program_studi, mode.jenjang]
    .map((v) => (typeof v === "string" ? v.trim() : ""))
    .filter(Boolean);
  return parts.join(" · ");
}

export function normalizeSources(rawSources, legacyPages) {
  const byPage = new Map();

  if (Array.isArray(rawSources)) {
    for (const item of rawSources) {
      if (!item || typeof item !== "object") continue;
      const page = Number(item.halaman);
      if (!Number.isInteger(page) || page <= 0) continue;
      if (!byPage.has(page)) {
        byPage.set(page, {
          halaman: page,
          bagian: item.bagian || null,
          kutipan: item.kutipan || "",
          programStudi: item.program_studi || null,
          fakultas: item.fakultas || null,
        });
      }
    }
  }

  if (byPage.size === 0 && Array.isArray(legacyPages)) {
    for (const value of legacyPages) {
      const page = Number(value);
      if (Number.isInteger(page) && page > 0 && !byPage.has(page)) {
        byPage.set(page, {
          halaman: page,
          bagian: null,
          kutipan: "",
          programStudi: null,
          fakultas: null,
        });
      }
    }
  }

  return Array.from(byPage.values()).sort((a, b) => a.halaman - b.halaman);
}

export function parseChatResponse(data) {
  let payload = data && typeof data === "object" ? data : {};
  if (payload.answer && typeof payload.answer === "object") {
    payload = payload.answer;
  }

  const status = String(data?.status || "");
  const answer = String(payload.answer || "").trim();
  const isFallback =
    payload.is_fallback === true ||
    status === "not_found" ||
    answer === FALLBACK_TEXT;

  const isClarification =
    status === "needs_clarification" &&
    data?.clarification &&
    Array.isArray(data.clarification.options) &&
    data.clarification.options.length > 0;

  const sources =
    isFallback || isClarification
      ? []
      : normalizeSources(data?.sources, payload.pages);

  return {
    status: status || (isFallback ? "not_found" : "answered"),
    answer: answer || FALLBACK_TEXT,
    sources,
    modeLabel: formatModeLabel(data?.mode),
    clarification: isClarification ? data.clarification : null,
    isFallback,
  };
}

function appendInline(parent, text) {
  const lines = String(text).split("\n");
  lines.forEach((line, index) => {
    if (index > 0) parent.appendChild(document.createElement("br"));
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
    const bulletMatch = line.match(/^\s*[-*]\s+(.*)$/);
    const numberedMatch = line.match(/^\s*\d+[.)]\s+(.*)$/);

    if (bulletMatch || numberedMatch) {
      const isBullet = Boolean(bulletMatch);
      const list = document.createElement(isBullet ? "ul" : "ol");
      while (i < lines.length) {
        const match = isBullet
          ? lines[i].match(/^\s*[-*]\s+(.*)$/)
          : lines[i].match(/^\s*\d+[.)]\s+(.*)$/);
        if (!match) break;
        const li = document.createElement("li");
        appendInline(li, match[1]);
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

    const paragraphLines = [line];
    i += 1;
    while (
      i < lines.length &&
      lines[i].trim() !== "" &&
      !/^\s*[-*]\s+/.test(lines[i]) &&
      !/^\s*\d+[.)]\s+/.test(lines[i])
    ) {
      paragraphLines.push(lines[i]);
      i += 1;
    }

    const p = document.createElement("p");
    appendInline(p, paragraphLines.join("\n"));
    container.appendChild(p);
  }
}
