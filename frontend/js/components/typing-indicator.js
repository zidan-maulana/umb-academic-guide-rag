import { TYPING_NOTE_DELAY_MS } from "../config.js";
import { COPY } from "../content/copy.js";
import { el, icon } from "../utils/dom.js";

export function createTypingIndicator() {
  const note = el("span", {
    className: "typing__note",
    text: COPY.typingNote,
    hidden: true,
  });

  const dots = el("div", { className: "typing__dots", "aria-hidden": "true" }, [
    el("span"),
    el("span"),
    el("span"),
  ]);

  const row = el(
    "div",
    { className: "msg-row msg-row--bot", id: "typing-indicator", role: "status" },
    [
      el("div", { className: "msg-avatar", "aria-hidden": "true" }, [icon("book", 16)]),
      el("div", { className: "msg-col" }, [
        el("div", { className: "bubble bubble--bot" }, [
          el("div", { className: "typing" }, [
            el("span", { className: "sr-only", text: COPY.typingNote }),
            dots,
            note,
          ]),
        ]),
      ]),
    ]
  );

  const timer = window.setTimeout(() => {
    note.hidden = false;
  }, TYPING_NOTE_DELAY_MS);

  return {
    element: row,
    destroy() {
      window.clearTimeout(timer);
      row.remove();
    },
  };
}
