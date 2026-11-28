import { getState, setState } from "../state/store.js";
import { qs, prefersReducedMotion } from "../utils/dom.js";
import { runCircleTransition } from "./transition.js";

function setButtonLoading(button, busy) {
  if (!button || !button.classList.contains("btn--cta")) return () => {};
  const arrow = qs(".btn__arrow", button);
  button.classList.add("is-pressing");
  let spinner = null;
  if (arrow) {
    arrow.hidden = true;
    spinner = document.createElement("span");
    spinner.className = "btn__spinner";
    spinner.setAttribute("aria-hidden", "true");
    button.appendChild(spinner);
  }
  return () => {
    button.classList.remove("is-pressing");
    if (spinner) spinner.remove();
    if (arrow && busy) arrow.hidden = false;
  };
}

function activateScene(targetName) {
  const landing = qs("#landing");
  const chat = qs("#chat");
  const isChat = targetName === "chat";

  landing.hidden = isChat;
  landing.inert = isChat;
  landing.setAttribute("aria-hidden", String(isChat));

  chat.hidden = !isChat;
  chat.inert = !isChat;
  chat.setAttribute("aria-hidden", String(!isChat));

  document.body.setAttribute("data-active-scene", targetName);
  setState({ scene: targetName }, "scene");
}

export async function goToChat(originEl) {
  const state = getState();
  if (state.isTransitioning || state.scene === "chat") return;
  setState({ isTransitioning: true }, "transition");

  const landing = qs("#landing");
  const chat = qs("#chat");
  const cleanupBtn = setButtonLoading(originEl, true);

  if (!prefersReducedMotion()) {
    landing.classList.add("is-leaving");
    await new Promise((r) => window.setTimeout(r, 120));
  }

  chat.classList.add("is-entering");
  await runCircleTransition({
    originEl,
    reverse: false,
    swapDom: () => activateScene("chat"),
  });

  cleanupBtn();
  landing.classList.remove("is-leaving");
  window.setTimeout(() => chat.classList.remove("is-entering"), 900);
  setState({ isTransitioning: false }, "transition");

  const input = qs("#question-input");
  if (input && !input.disabled) input.focus();
}

export async function goToLanding(originEl) {
  const state = getState();
  if (state.isTransitioning || state.scene === "landing") return;
  setState({ isTransitioning: true }, "transition");

  await runCircleTransition({
    originEl,
    reverse: true,
    swapDom: () => activateScene("landing"),
  });

  setState({ isTransitioning: false }, "transition");
  const cta = qs("#hero-cta");
  if (cta) cta.focus();
}
