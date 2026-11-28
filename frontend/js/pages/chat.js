import { GREETING_REGEX, MAX_QUESTION } from "../config.js";
import { COPY } from "../content/copy.js";
import { toggleTheme } from "../core/theme.js";
import { askBackend } from "../services/api.js";
import { addMessage, clearMessages, getState, setState } from "../state/store.js";
import { createBotBubble, createUserBubble } from "../components/bubble.js";
import { createChatHeader } from "../components/chat-header.js";
import { createComposer } from "../components/composer.js";
import { createJumpLatest } from "../components/floating.js";
import { showToast } from "../components/toast.js";
import { createTypingIndicator } from "../components/typing-indicator.js";
import { createWelcome } from "../components/welcome.js";
import { el, on, qs } from "../utils/dom.js";
import { isNearBottom, scrollToBottom } from "../utils/scroll.js";
import { runTypewriter } from "../utils/typewriter.js";

export function initChat({ onBackToLanding }) {
  const root = qs("#chat");
  if (!root) return null;

  let composer = null;
  let welcome = null;
  let header = null;
  let messagesScroll = null;
  let messagesInner = null;
  let jumpLatest = null;

  const syncScrollBtn = () => {
    if (!jumpLatest || !messagesScroll) return;
    jumpLatest.setVisible(!isNearBottom(messagesScroll));
  };

  const appendRow = (row, forceScroll = true) => {
    messagesInner.appendChild(row);
    const scrolled = scrollToBottom(messagesScroll, forceScroll);
    if (!scrolled && jumpLatest) jumpLatest.setVisible(true);
  };

  const renderEntry = (entry, { animateText = false } = {}) => {
    if (entry.role === "user") {
      const row = createUserBubble(entry);
      appendRow(row, true);
      return null;
    }

    const view = createBotBubble(entry, {
      animateText,
      onRetry: (q) => sendQuestion(q, { fromRetry: true }),
      onClarify: (q, field, value) => sendQuestion(q, { filters: { [field]: value } }),
      onToast: showToast,
    });
    appendRow(view.element, true);
    return view;
  };

  const finishBotReply = (entry) => {
    addMessage(entry);
    const view = renderEntry(entry, { animateText: true });
    if (!view) {
      setState({ isLoading: false }, "loading");
      composer.setLocked(false);
      return;
    }

    const cancel = runTypewriter(view.content, entry.text, {
      onTick: () => scrollToBottom(messagesScroll, false),
      onDone: () => {
        view.bubble.removeEventListener("click", cancel);
        if (entry.sources && entry.sources.length) {
          view.showBadges(entry.sources);
        }
        setState({ isLoading: false }, "loading");
        composer.setLocked(false);
        scrollToBottom(messagesScroll, false);
      },
    });
    on(view.bubble, "click", cancel);
  };

  const sendQuestion = async (raw, { fromRetry = false, filters = null } = {}) => {
    const question = String(raw || "").trim().slice(0, MAX_QUESTION);
    if (!question || getState().isLoading) return;

    welcome.hide();
    header.setClearVisible(true);
    setState({ lastQuestion: question, isLoading: true }, "loading");

    if (!fromRetry) {
      const userEntry = { role: "user", text: question, ts: Date.now() };
      addMessage(userEntry);
      renderEntry(userEntry);
    }

    composer.clear();
    composer.setLocked(true);

    const typing = createTypingIndicator();
    appendRow(typing.element, true);

    if (GREETING_REGEX.test(question) && !filters) {
      window.setTimeout(() => {
        typing.destroy();
        finishBotReply({
          role: "bot",
          kind: "normal",
          text: COPY.greetingReply,
          ts: Date.now(),
          sources: [],
        });
      }, 380);
      return;
    }

    try {
      const result = await askBackend(question, filters);
      typing.destroy();
      finishBotReply({
        role: "bot",
        kind: result.isFallback ? "fallback" : "normal",
        text: result.answer,
        ts: Date.now(),
        sources: result.sources,
        modeLabel: result.modeLabel,
        clarification: result.clarification,
        originalQuestion: question,
      });
    } catch (err) {
      typing.destroy();
      const errEntry = {
        role: "bot",
        kind: "error",
        text: err.message || COPY.errGeneric,
        ts: Date.now(),
        retryQuestion: question,
      };
      addMessage(errEntry);
      renderEntry(errEntry, { animateText: false });
      setState({ isLoading: false }, "loading");
      composer.setLocked(false);
    }
  };

  const handleClear = () => {
    if (getState().isLoading) return;
    clearMessages();
    messagesInner.querySelectorAll(".msg-row").forEach((node) => node.remove());
    welcome.show();
    header.setClearVisible(false);
    jumpLatest.setVisible(false);
    showToast(COPY.clearDoneToast);
    composer.focus();
  };

  header = createChatHeader({
    onBack: (originEl) => onBackToLanding && onBackToLanding(originEl),
    onToggleTheme: () => toggleTheme(),
    onClear: handleClear,
  });

  welcome = createWelcome({ onSelectSuggestion: (q) => sendQuestion(q) });
  composer = createComposer({ onSubmit: (q) => sendQuestion(q) });
  jumpLatest = createJumpLatest({
    onClick: () => {
      scrollToBottom(messagesScroll, true);
      jumpLatest.setVisible(false);
    },
  });

  messagesInner = el("div", { className: "chat-container messages__inner" }, [welcome.element]);
  messagesScroll = el(
    "div",
    {
      className: "messages",
      id: "messages",
      role: "log",
      "aria-live": "polite",
      "aria-relevant": "additions",
    },
    [messagesInner]
  );

  on(messagesScroll, "scroll", syncScrollBtn);

  const stage = el("div", { className: "chat-stage" }, [messagesScroll, jumpLatest.element]);
  root.replaceChildren(header.element, stage, composer.element);

  const existing = getState().messages;
  if (existing.length > 0) {
    welcome.hide();
    header.setClearVisible(true);
    existing.forEach((entry) => renderEntry(entry, { animateText: false }));
  } else {
    header.setClearVisible(false);
  }

  return {
    sendQuestion,
    focusInput: () => composer.focus(),
  };
}
