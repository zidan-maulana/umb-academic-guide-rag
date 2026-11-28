import { prefersReducedMotion } from "./dom.js";

export function isNearBottom(container, threshold = 80) {
  if (!container) return true;
  return container.scrollHeight - container.scrollTop - container.clientHeight < threshold;
}

export function scrollToBottom(container, force = false) {
  if (!container) return true;
  if (force || isNearBottom(container)) {
    container.scrollTo({
      top: container.scrollHeight,
      behavior: prefersReducedMotion() ? "auto" : "smooth",
    });
    return true;
  }
  return false;
}
