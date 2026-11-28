import { TRANSITION_BACK_MS, TRANSITION_ENTER_MS } from "../config.js";
import { prefersReducedMotion } from "../utils/dom.js";

function getOriginPoint(originEl) {
  if (!originEl || typeof originEl.getBoundingClientRect !== "function") {
    return { x: window.innerWidth / 2, y: window.innerHeight / 2 };
  }
  const rect = originEl.getBoundingClientRect();
  return {
    x: rect.left + rect.width / 2,
    y: rect.top + rect.height / 2,
  };
}

function getMaxRadius(x, y) {
  const maxX = Math.max(x, window.innerWidth - x);
  const maxY = Math.max(y, window.innerHeight - y);
  return Math.ceil(Math.hypot(maxX, maxY));
}

export async function runCircleTransition({ originEl, reverse = false, swapDom }) {
  if (prefersReducedMotion()) {
    swapDom();
    return;
  }

  const { x, y } = getOriginPoint(originEl);
  const radius = getMaxRadius(x, y);
  const duration = reverse ? TRANSITION_BACK_MS : TRANSITION_ENTER_MS;
  const clipStart = reverse ? `circle(${radius}px at ${x}px ${y}px)` : `circle(0px at ${x}px ${y}px)`;
  const clipEnd = reverse ? `circle(0px at ${x}px ${y}px)` : `circle(${radius}px at ${x}px ${y}px)`;

  if (typeof document.startViewTransition === "function") {
    document.documentElement.dataset.transitionDir = reverse ? "back" : "enter";
    const vt = document.startViewTransition(() => swapDom());
    await vt.ready;
    await document.documentElement.animate(
      { clipPath: [clipStart, clipEnd] },
      {
        duration: reverse ? duration : 500,
        easing: "cubic-bezier(0.65, 0, 0.35, 1)",
        pseudoElement: reverse ? "::view-transition-old(root)" : "::view-transition-new(root)",
      }
    ).finished.catch(() => {});
    await vt.finished.catch(() => {});
    delete document.documentElement.dataset.transitionDir;
    return;
  }

  swapDom();
  const target = document.getElementById(reverse ? "landing" : "chat");
  if (!target || typeof target.animate !== "function") return;
  const anim = target.animate(
    { clipPath: [`circle(0px at ${x}px ${y}px)`, `circle(${radius}px at ${x}px ${y}px)`] },
    { duration: reverse ? duration : 500, easing: "cubic-bezier(0.65, 0, 0.35, 1)" }
  );
  await anim.finished.catch(() => {});
}
