import { loadHistory, saveHistory } from "./storage.js";

const state = {
  scene: "landing",
  theme: "light",
  messages: loadHistory(),
  isLoading: false,
  isTransitioning: false,
  lastQuestion: "",
  toast: null,
};

const listeners = new Set();

export function getState() {
  return state;
}

export function subscribe(listener) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function setState(patch, reason = "update") {
  Object.assign(state, patch);
  for (const listener of listeners) {
    listener(state, reason);
  }
}

export function addMessage(entry) {
  const next = [...state.messages, entry];
  saveHistory(next);
  setState({ messages: next }, "messages");
  return entry;
}

export function clearMessages() {
  saveHistory([]);
  setState({ messages: [], lastQuestion: "" }, "messages:clear");
}
