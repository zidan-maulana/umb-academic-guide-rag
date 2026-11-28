import { el, icon, on } from "../utils/dom.js";

export function createChip({ question, label, iconName, variant = "grid", onSelect }) {
  const className = variant === "inline" ? "chip chip--inline" : "chip";
  const btn = el("button", { type: "button", className }, [
    el("span", { className: "chip__icon", "aria-hidden": "true" }, [icon(iconName, 18)]),
    el("span", { className: "chip__label", text: label || question }),
  ]);

  on(btn, "click", (event) => {
    if (onSelect) onSelect(question, event.currentTarget);
  });

  return btn;
}
