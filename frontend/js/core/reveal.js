import { prefersReducedMotion, qsa } from "../utils/dom.js";

export function initScrollReveal() {
  const nodes = qsa(".reveal");
  if (!nodes.length) return;

  if (prefersReducedMotion() || typeof IntersectionObserver !== "function") {
    nodes.forEach((node) => node.classList.add("is-revealed"));
    return;
  }

  let staggerBatch = 0;
  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        const delay = Math.min(staggerBatch, 4) * 80;
        staggerBatch += 1;
        entry.target.style.transitionDelay = `${delay}ms`;
        entry.target.classList.add("is-revealed");
        observer.unobserve(entry.target);
      }
      window.setTimeout(() => {
        staggerBatch = 0;
      }, 200);
    },
    { threshold: 0.14, rootMargin: "0px 0px -32px 0px" }
  );

  nodes.forEach((node) => observer.observe(node));
}
