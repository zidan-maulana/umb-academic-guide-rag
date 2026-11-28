import { COPY } from "../content/copy.js";
import { SUGGESTIONS } from "../content/suggestions.js";
import { el, icon, prefersReducedMotion } from "../utils/dom.js";
import { createChip } from "./chip.js";

export function createWelcome({ onSelectSuggestion }) {
  const chipsGrid = el(
    "div",
    { className: "chip-grid welcome__chips" },
    SUGGESTIONS.map((item) =>
      createChip({
        question: item.q,
        label: item.q,
        iconName: item.icon,
        variant: "grid",
        onSelect: (q) => onSelectSuggestion && onSelectSuggestion(q),
      })
    )
  );

  const section = el("section", { className: "welcome", id: "chat-welcome" }, [
    el("div", { className: "welcome__orb", "aria-hidden": "true" }, [icon("brand", 28)]),
    el("h2", { className: "welcome__title" }, [
      COPY.welcomeTitlePrefix,
      el("span", { className: "accent-serif", text: COPY.welcomeTitleAccent }),
      COPY.welcomeTitleSuffix,
    ]),
    el("p", { className: "welcome__sub", text: COPY.welcomeSub }),
    chipsGrid,
  ]);

  return {
    element: section,
    show() {
      section.classList.remove("is-leaving");
      section.hidden = false;
    },
    hide() {
      if (section.hidden) return;
      if (prefersReducedMotion()) {
        section.hidden = true;
        return;
      }
      section.classList.add("is-leaving");
      window.setTimeout(() => {
        section.hidden = true;
        section.classList.remove("is-leaving");
      }, 200);
    },
  };
}
