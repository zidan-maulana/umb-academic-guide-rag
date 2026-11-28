import { CLEAR_CONFIRM_MS } from "../config.js";
import { COPY } from "../content/copy.js";
import { el, icon, on } from "../utils/dom.js";

export function createChatHeader({ onBack, onToggleTheme, onClear }) {
  let confirmTimer = 0;

  const backBtn = el(
    "button",
    {
      type: "button",
      className: "icon-btn",
      id: "chat-back-btn",
      "aria-label": COPY.backLabel,
      title: COPY.backLabel,
    },
    [icon("arrow-left", 20)]
  );

  const themeBtn = el(
    "button",
    {
      type: "button",
      className: "icon-btn",
      id: "chat-theme-toggle",
      "aria-label": COPY.themeLabel,
      title: COPY.themeLabel,
    },
    [icon("sun", 20, "icon-sun"), icon("moon", 20, "icon-moon")]
  );

  const clearBtn = el(
    "button",
    {
      type: "button",
      className: "icon-btn",
      id: "clear-chat-btn",
      "aria-label": COPY.clearLabel,
      title: COPY.clearLabel,
    },
    [icon("trash", 20)]
  );

  const yesBtn = el("button", {
    type: "button",
    className: "text-btn text-btn--danger",
    id: "clear-confirm-yes",
    text: COPY.clearYes,
  });

  const noBtn = el("button", {
    type: "button",
    className: "text-btn",
    id: "clear-confirm-no",
    text: COPY.clearNo,
  });

  const confirmWrap = el("div", { className: "clear-confirm", hidden: true }, [
    el("span", { className: "clear-confirm__label", text: COPY.clearConfirmPrompt }),
    yesBtn,
    noBtn,
  ]);

  const hideConfirm = () => {
    window.clearTimeout(confirmTimer);
    confirmWrap.hidden = true;
    clearBtn.hidden = false;
  };

  on(backBtn, "click", (event) => {
    hideConfirm();
    if (onBack) onBack(event.currentTarget);
  });

  on(themeBtn, "click", () => {
    if (onToggleTheme) onToggleTheme();
  });

  on(clearBtn, "click", () => {
    clearBtn.hidden = true;
    confirmWrap.hidden = false;
    yesBtn.focus();
    confirmTimer = window.setTimeout(hideConfirm, CLEAR_CONFIRM_MS);
  });

  on(yesBtn, "click", () => {
    hideConfirm();
    if (onClear) onClear();
  });

  on(noBtn, "click", () => {
    hideConfirm();
    clearBtn.focus();
  });

  const header = el("header", { className: "chat-header" }, [
    el("div", { className: "chat-container chat-header__inner" }, [
      el("div", { className: "chat-header__left" }, [
        backBtn,
        el("div", { className: "chat-header__brand" }, [
          el("span", { className: "brand__mark", "aria-hidden": "true" }, [icon("brand", 18)]),
          el("div", {}, [
            el("h1", { className: "chat-header__title", text: COPY.brandName }),
            el("p", { className: "chat-header__tagline", text: COPY.headerTagline }),
          ]),
        ]),
      ]),
      el("div", { className: "chat-header__actions" }, [themeBtn, clearBtn, confirmWrap]),
    ]),
  ]);

  return {
    element: header,
    setClearVisible(visible) {
      if (!visible) hideConfirm();
      clearBtn.disabled = !visible;
      clearBtn.style.opacity = visible ? "" : "0.45";
    },
  };
}
