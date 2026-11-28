import { COPY } from "../content/copy.js";
import { SUGGESTIONS } from "../content/suggestions.js";
import { initScrollReveal } from "../core/reveal.js";
import { toggleTheme } from "../core/theme.js";
import { getState, subscribe } from "../state/store.js";
import { bindFloatingChat } from "../components/floating.js";
import { createChip } from "../components/chip.js";
import { on, qs } from "../utils/dom.js";

export function initLanding({ onOpenChat }) {
  const heroCta = qs("#hero-cta");
  const closingCta = qs("#closing-cta");
  const floatingBtn = qs("#floating-chat");
  const themeBtn = qs("#landing-theme-toggle");
  const chipsContainer = qs("#landing-chips");

  const syncCtaLabels = (messages) => {
    const labelText = messages.length > 0 ? COPY.ctaContinue : COPY.ctaStart;
    const heroLabel = qs(".btn__label", heroCta);
    const closingLabel = qs(".btn__label", closingCta);
    if (heroLabel) heroLabel.textContent = labelText;
    if (closingLabel) closingLabel.textContent = labelText;
  };

  syncCtaLabels(getState().messages);
  subscribe((state, reason) => {
    if (reason.startsWith("messages")) {
      syncCtaLabels(state.messages);
    }
  });

  if (themeBtn) {
    on(themeBtn, "click", () => toggleTheme());
  }

  if (heroCta) {
    on(heroCta, "click", () => onOpenChat({ originEl: heroCta }));
  }

  if (closingCta) {
    on(closingCta, "click", () => onOpenChat({ originEl: closingCta }));
  }

  if (floatingBtn && heroCta) {
    bindFloatingChat(floatingBtn, heroCta, (originEl) => onOpenChat({ originEl }));
  }

  if (chipsContainer) {
    chipsContainer.replaceChildren(
      ...SUGGESTIONS.map((item) =>
        createChip({
          question: item.q,
          label: item.short,
          iconName: item.icon,
          variant: "inline",
          onSelect: (question, chipEl) => onOpenChat({ originEl: chipEl, question }),
        })
      )
    );
  }

  initScrollReveal();
}
