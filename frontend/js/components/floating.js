import { COPY } from "../content/copy.js";
import { el, icon, on } from "../utils/dom.js";

export function bindFloatingChat(buttonEl, targetObservedEl, onOpen) {
  if (!buttonEl || !targetObservedEl) return () => {};

  const unbindClick = on(buttonEl, "click", (event) => {
    if (onOpen) onOpen(event.currentTarget);
  });

  if (typeof IntersectionObserver !== "function") {
    buttonEl.classList.add("is-visible");
    return unbindClick;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      const entry = entries[0];
      if (!entry) return;
      buttonEl.classList.toggle("is-visible", !entry.isIntersecting);
    },
    { threshold: 0.1 }
  );

  observer.observe(targetObservedEl);

  return () => {
    unbindClick();
    observer.disconnect();
  };
}

export function createJumpLatest({ onClick }) {
  const btn = el(
    "button",
    { type: "button", className: "jump-latest", id: "jump-latest", hidden: true },
    [icon("arrow-down", 15), el("span", { text: COPY.jumpLatest })]
  );

  on(btn, "click", () => {
    if (onClick) onClick();
  });

  return {
    element: btn,
    setVisible(visible) {
      btn.hidden = !visible;
    },
  };
}
