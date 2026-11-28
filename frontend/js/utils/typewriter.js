import { TYPEWRITER_CHAR_MS, TYPEWRITER_MAX_MS } from "../config.js";
import { prefersReducedMotion } from "./dom.js";
import { renderFormatted } from "./format.js";

export function runTypewriter(contentEl, fullText, { onTick, onDone } = {}) {
  if (prefersReducedMotion()) {
    renderFormatted(contentEl, fullText);
    if (onDone) onDone();
    return () => {};
  }

  let skipped = false;
  let timerId = 0;
  const total = fullText.length;
  const stepMs = Math.max(
    4,
    Math.min(TYPEWRITER_CHAR_MS, TYPEWRITER_MAX_MS / Math.max(total, 1))
  );
  let index = 0;

  const finish = () => {
    window.clearTimeout(timerId);
    renderFormatted(contentEl, fullText);
    if (onDone) onDone();
  };

  const tick = () => {
    if (skipped) {
      finish();
      return;
    }
    index = Math.min(total, index + 2);
    renderFormatted(contentEl, fullText.slice(0, index));
    if (onTick) onTick();
    if (index >= total) {
      finish();
      return;
    }
    timerId = window.setTimeout(tick, stepMs);
  };

  tick();

  return () => {
    skipped = true;
    finish();
  };
}
