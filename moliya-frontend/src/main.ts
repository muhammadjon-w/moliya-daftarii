import { createApp } from "vue"
import { useUi } from "@/composables/useUi"
import { translate } from "@/plugins/i18n"
import { router } from "@/plugins/router"
import { telegram } from "@/plugins/telegram"
import { installVueQuery } from "@/plugins/vueQuery"
import App from "./App.vue"
import "@/styles/tokens.css"
import "@/styles/base.css"

const app = createApp(App)
const { ui, notify, openPaywall } = useUi()
document.documentElement.lang = ui.lang

installVueQuery(app, {
  onSubscriptionRequired() {
    openPaywall()
    telegram.haptic("error")
  },
  onError(message) {
    notify(translate(ui.lang, "err_prefix") + " " + message, true)
    telegram.haptic("error")
  },
})
app.use(router)
telegram.ready()
// Birinchi sahifa aniqlanmaguncha mount qilinmaydi: /obuna da mini app qobig'i bir lahza ham yuklanmasin
router.isReady().then(() => app.mount("#app"))
