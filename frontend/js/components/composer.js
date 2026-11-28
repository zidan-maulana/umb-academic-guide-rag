import { MAX_QUESTION } from "../config.js";
import { COPY } from "../content/copy.js";
import { el, icon, on } from "../utils/dom.js";

export function createComposer({ onSubmit }) {
  let isLocked = false;

  const input = el("textarea", {
    id: "question-input",
    name: "question",
    className: "composer__input",
    rows: "1",
    maxlength: String(MAX_QUESTION),
    placeholder: COPY.composerPlaceholder,
    autocomplete: "off",
  });

  const sendBtn = el(
    "button",
    {
      type: "submit",
      className: "composer__send",
      id: "send-btn",
      "aria-label": COPY.sendLabel,
      disabled: true,
    },
    [icon("arrow-right", 18)]
  );

  const form = el("form", { className: "composer", id: "composer" }, [
    el("label", { className: "sr-only", for: "question-input", text: COPY.composerLabel }),
    input,
    sendBtn,
  ]);

  const dock = el("footer", { className: "composer-dock" }, [
    el("div", { className: "chat-container" }, [
      form,
      el("div", { className: "composer-meta" }, [
        el("p", { className: "composer-hint", text: COPY.composerHint }),
        el("p", { className: "composer-disclaimer", text: COPY.disclaimer }),
      ]),
    ]),
  ]);

  const resize = () => {
    input.style.height = "auto";
    const nextHeight = Math.min(input.scrollHeight, 132);
    input.style.height = `${nextHeight}px`;
    input.style.overflowY = input.scrollHeight > 132 ? "auto" : "hidden";
  };

  const syncSendState = () => {
    sendBtn.disabled = isLocked || input.value.trim().length === 0;
  };

  const submitCurrent = () => {
    const val = input.value.trim();
    if (!val || isLocked) return;
    if (onSubmit) onSubmit(val);
  };

  on(form, "submit", (event) => {
    event.preventDefault();
    submitCurrent();
  });

  on(input, "input", () => {
    resize();
    syncSendState();
  });

  on(input, "keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      submitCurrent();
    }
  });

  on(input, "focus", () => {
    window.setTimeout(() => {
      input.scrollIntoView({ block: "nearest", behavior: "smooth" });
    }, 150);
  });

  return {
    element: dock,
    input,
    clear() {
      input.value = "";
      resize();
      syncSendState();
    },
    setLocked(locked) {
      isLocked = locked;
      input.disabled = locked;
      syncSendState();
      if (!locked) input.focus();
    },
    focus() {
      input.focus();
    },
  };
}
