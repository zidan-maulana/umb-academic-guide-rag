import { PDF_URL } from "../config.js";
import { COPY } from "../content/copy.js";
import { copyText } from "../utils/clipboard.js";
import { el, icon, on } from "../utils/dom.js";

export function createSourceBadges(sources, { onToast } = {}) {
  if (!Array.isArray(sources) || !sources.length) return null;

  let activePage = null;
  const buttons = new Map();
  const quoteBox = el("div", { className: "source-quote", hidden: true });
  const row = el("div", { className: "sources__row" });

  const renderQuote = (src) => {
    const metaParts = [src.bagian, src.programStudi || src.fakultas].filter(Boolean);
    const title = metaParts.length
      ? `Halaman ${src.halaman} (${metaParts.join(" · ")})`
      : `Halaman ${src.halaman}`;

    const copyRefBtn = el("button", {
      type: "button",
      className: "source-quote__action",
      text: `Salin Hal. ${src.halaman}`,
    });
    on(copyRefBtn, "click", async () => {
      try {
        await copyText(`Hal. ${src.halaman}: ${src.kutipan}`);
        if (onToast) onToast(`Kutipan Hal. ${src.halaman} disalin`);
      } catch {
        if (onToast) onToast(COPY.copyErrorToast);
      }
    });

    const actions = [copyRefBtn];
    if (PDF_URL) {
      const openLink = el(
        "a",
        {
          className: "source-quote__action",
          href: `${PDF_URL}#page=${src.halaman}`,
          target: "_blank",
          rel: "noopener noreferrer",
        },
        [icon("external", 14), "Buka PDF"]
      );
      actions.push(openLink);
    }

    const closeBtn = el("button", {
      type: "button",
      className: "text-btn",
      text: "Tutup",
      "aria-label": "Tutup kutipan sumber",
    });
    on(closeBtn, "click", () => {
      activePage = null;
      quoteBox.hidden = true;
      buttons.forEach((b) => b.setAttribute("aria-expanded", "false"));
    });

    quoteBox.replaceChildren(
      el("div", { className: "source-quote__head" }, [el("span", { text: title }), closeBtn]),
      el("p", { className: "source-quote__text", text: src.kutipan }),
      el("div", { className: "source-quote__actions" }, actions)
    );
    quoteBox.hidden = false;
  };

  sources.forEach((src, index) => {
    const badgeChildren = [icon("doc", 14), el("span", { text: `Hal. ${src.halaman}` })];
    if (PDF_URL && !src.kutipan) {
      badgeChildren.push(icon("external", 13, "source-badge__ext"));
    }

    const badge = el(
      "button",
      {
        type: "button",
        className: "source-badge",
        "aria-label": `Sumber halaman ${src.halaman}`,
        "aria-expanded": src.kutipan ? "false" : null,
      },
      badgeChildren
    );
    badge.style.animationDelay = `${index * 60}ms`;
    buttons.set(src.halaman, badge);

    on(badge, "click", async () => {
      if (src.kutipan) {
        if (activePage === src.halaman) {
          activePage = null;
          quoteBox.hidden = true;
          badge.setAttribute("aria-expanded", "false");
          return;
        }
        activePage = src.halaman;
        buttons.forEach((b, p) => b.setAttribute("aria-expanded", String(p === src.halaman)));
        renderQuote(src);
        return;
      }

      if (PDF_URL) {
        window.open(`${PDF_URL}#page=${src.halaman}`, "_blank", "noopener,noreferrer");
        return;
      }

      try {
        await copyText(`Hal. ${src.halaman}`);
        if (onToast) onToast(`Hal. ${src.halaman} disalin`);
      } catch {
        if (onToast) onToast(COPY.copyErrorToast);
      }
    });

    row.appendChild(badge);
  });

  return el("div", { className: "sources" }, [
    el("span", { className: "sources__label", text: COPY.sourcesLabel }),
    row,
    quoteBox,
  ]);
}
