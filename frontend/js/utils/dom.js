const SVG_NS = "http://www.w3.org/2000/svg";

export function qs(selector, root = document) {
  return root.querySelector(selector);
}

export function qsa(selector, root = document) {
  return Array.from(root.querySelectorAll(selector));
}

export function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  for (const [key, val] of Object.entries(attrs)) {
    if (val === undefined || val === null || val === false) continue;
    if (key === "className") {
      node.className = val;
    } else if (key === "text") {
      node.textContent = val;
    } else if (key === "dataset") {
      Object.assign(node.dataset, val);
    } else if (key === "hidden") {
      node.hidden = Boolean(val);
    } else if (key === "disabled") {
      node.disabled = Boolean(val);
    } else {
      node.setAttribute(key, String(val));
    }
  }
  for (const child of children) {
    if (child === null || child === undefined) continue;
    node.appendChild(typeof child === "string" ? document.createTextNode(child) : child);
  }
  return node;
}

export function on(target, eventName, handler, options) {
  target.addEventListener(eventName, handler, options);
  return () => target.removeEventListener(eventName, handler, options);
}

export function icon(name, size = 18, className = "") {
  const svg = document.createElementNS(SVG_NS, "svg");
  svg.setAttribute("width", String(size));
  svg.setAttribute("height", String(size));
  svg.setAttribute("aria-hidden", "true");
  if (className) svg.setAttribute("class", className);

  const use = document.createElementNS(SVG_NS, "use");
  use.setAttribute("href", `assets/icons/sprite.svg#icon-${name}`);
  svg.appendChild(use);
  return svg;
}

export function prefersReducedMotion() {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}
