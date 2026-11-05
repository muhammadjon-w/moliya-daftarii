import { MutationCache, QueryCache, QueryClient, VueQueryPlugin } from "@tanstack/vue-query"
import { createPinia } from "pinia"
import { createApp } from "vue"
import { GATEWAYS } from "@/application/container"
import { ApiError } from "@/application/errors"
import { useUiStore } from "@/application/session/ui"
import { translate } from "@/presentation/i18n"
import App from "./app/App.vue"
import { createGateways } from "./app/container"
import { router } from "./app/router"
import "@/presentation/styles/app.css"
import "@/presentation/styles/extra.css"

const gateways = createGateways()
const pinia = createPinia()
const app = createApp(App)
app.use(pinia)

const ui = useUiStore(pinia)
ui.initLang(gateways.platform.languageCode)

/** Barcha yozish xatolari bir joyda: obuna tugagan bo'lsa to'lov oynasi, aks holda bildirishnoma. */
function onMutationError(error: unknown) {
  if (error instanceof ApiError && error.subscriptionRequired) {
    ui.paywallOpen = true
    gateways.platform.haptic("error")
    return
  }
  const msg = error instanceof ApiError ? error.message : String(error)
  ui.notify(translate(ui.lang, "err_prefix") + " " + msg, true)
  gateways.platform.haptic("error")
}

const queryClient = new QueryClient({
  queryCache: new QueryCache(),
  mutationCache: new MutationCache({ onError: onMutationError }),
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: true,
      retry: (count, err) => !(err instanceof ApiError && err.status >= 400 && err.status < 500) && count < 2,
    },
    mutations: { retry: 0 },
  },
})

app.provide(GATEWAYS, gateways)
app.use(VueQueryPlugin, { queryClient })
app.use(router)
gateways.platform.ready()
app.mount("#app")
