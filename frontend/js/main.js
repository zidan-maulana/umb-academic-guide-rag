import { initToast } from "./components/toast.js";
import { goToChat, goToLanding } from "./core/scene.js";
import { initTheme } from "./core/theme.js";
import { initChat } from "./pages/chat.js";
import { initLanding } from "./pages/landing.js";
import { wakeHealth } from "./services/api.js";

function bootstrap() {
  initTheme();
  initToast();
  wakeHealth();

  const chatController = initChat({
    onBackToLanding: (originEl) => goToLanding(originEl),
  });

  initLanding({
    onOpenChat: async ({ originEl, question } = {}) => {
      await goToChat(originEl);
      if (question && chatController) {
        chatController.sendQuestion(question);
      }
    },
  });
}

bootstrap();
