import { COPY } from "../content/copy.js";
import { copyText } from "../utils/clipboard.js";
import { el, icon, on } from "../utils/dom.js";
import { formatTime, renderFormatted } from "../utils/format.js";
import { createSourceBadges } from "./source-badges.js";

export function createUserBubble(entry) {
  const timeEl = el("time", {
    className: "bubble__meta",
    datetime: new Date(entry.ts).toISOString(),
    text: formatTime(entry.ts),
  });

  const bubble = el("div", { className: "bubble bubble--user" }, [
    el("div", { className: "bubble__content", text: entry.text }),
  ]);

  return el("article", { className: "msg-row msg-row--user" }, [
    el("div", { className: "msg-col" }, [bubble, timeEl]),
  ]);
}

function buildCopyButton(text, onToast) {
  const label = el("span", { text: COPY.copyLabel });
  const btn = el(
    "button",
    { type: "button", className: "copy-btn", "aria-label": "Salin jawaban" },
    [icon("copy", 14), label]
  );

  let resetTimer = 0;
  on(btn, "click", async () => {
    try {
      await copyText(text);
      btn.classList.add("is-copied");
      btn.replaceChildren(icon("check", 14), el("span", { text: COPY.copiedLabel }));
      window.clearTimeout(resetTimer);
      resetTimer = window.setTimeout(() => {
        btn.classList.remove("is-copied");
        btn.replaceChildren(icon("copy", 14), el("span", { text: COPY.copyLabel }));
      }, 1500);
    } catch {
      if (onToast) onToast(COPY.copyErrorToast);
    }
  });

  return btn;
}

export function createBotBubble(
  entry,
  { animateText = false, onRetry, onClarify, onToast } = {}
) {
  const isFallback = entry.kind === "fallback";
  const isError = entry.kind === "error";

  const bubbleClasses = ["bubble", "bubble--bot"];
  if (isFallback) bubbleClasses.push("bubble--fallback");
  if (isError) bubbleClasses.push("bubble--error");

  const content = el("div", { className: "bubble__content" });
  if (!animateText) {
    renderFormatted(content, entry.text);
  }

  const bodyChildren = [];
  if (isFallback || isError) {
    bodyChildren.push(
      el("span", { className: "bubble__lead-icon", "aria-hidden": "true" }, [
        icon(isError ? "warn" : "info", 18),
      ])
    );
  }
  bodyChildren.push(content);

  const bubbleChildren = [el("div", { className: "bubble__body" }, bodyChildren)];

  if (entry.clarification && Array.isArray(entry.clarification.options)) {
    const optionsWrap = el(
      "div",
      { className: "bubble__clarify" },
      entry.clarification.options.map((opt) => {
        const optBtn = el("button", {
          type: "button",
          className: "bubble__clarify-btn",
          text: opt,
        });
        on(optBtn, "click", () => {
          if (onClarify) {
            onClarify(entry.originalQuestion || "", entry.clarification.field, opt);
          }
        });
        return optBtn;
      })
    );
    bubbleChildren.push(optionsWrap);
  }

  if (isError && onRetry) {
    const retryBtn = el("button", {
      type: "button",
      className: "bubble__retry",
      text: COPY.retryLabel,
    });
    on(retryBtn, "click", () => onRetry(entry.retryQuestion));
    bubbleChildren.push(retryBtn);
  }

  const bubble = el("div", { className: bubbleClasses.join(" ") }, bubbleChildren);

  const metaChildren = [
    el("time", {
      datetime: new Date(entry.ts).toISOString(),
      text: formatTime(entry.ts),
    }),
  ];
  if (entry.modeLabel) {
    metaChildren.push(el("span", { className: "bubble__mode", text: entry.modeLabel }));
  }
  if (!isError) {
    metaChildren.push(buildCopyButton(entry.text, onToast));
  }

  const badgeHost = el("div");
  if (!animateText && !isFallback && !isError && Array.isArray(entry.sources) && entry.sources.length) {
    const badges = createSourceBadges(entry.sources, { onToast });
    if (badges) badgeHost.appendChild(badges);
  }

  const col = el("div", { className: "msg-col" }, [
    bubble,
    el("div", { className: "bubble__meta" }, metaChildren),
    badgeHost,
  ]);

  const row = el("article", { className: "msg-row msg-row--bot" }, [
    el("div", { className: "msg-avatar", "aria-hidden": "true" }, [icon("book", 16)]),
    col,
  ]);

  return {
    element: row,
    bubble,
    content,
    showBadges(sources) {
      if (isFallback || isError || !Array.isArray(sources) || !sources.length) return;
      const badges = createSourceBadges(sources, { onToast });
      if (badges) badgeHost.replaceChildren(badges);
    },
  };
}
