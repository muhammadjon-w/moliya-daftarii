// TanStack Query sozlamasi. Barcha yozish xatolari shu yerda bir marta ushlanadi.
import { MutationCache, QueryClient, VueQueryPlugin, type VueQueryPluginOptions } from "@tanstack/vue-query"
import type { App } from "vue"
import { ApiError } from "@/rest/client"

export interface QueryErrorHandlers {
  /** 402: obuna tugagan */
  onSubscriptionRequired(): void
  onError(message: string): void
}

export function installVueQuery(app: App, h: QueryErrorHandlers) {
  const queryClient = new QueryClient({
    mutationCache: new MutationCache({
      onError(error) {
        if (error instanceof ApiError && error.subscriptionRequired) h.onSubscriptionRequired()
        else h.onError(error instanceof Error ? error.message : String(error))
      },
    }),
    defaultOptions: {
      queries: {
        refetchOnWindowFocus: true,
        // 4xx xatoda qayta urinishdan foyda yo'q; tarmoq/5xx — 2 marta
        retry: (count, err) => !(err instanceof ApiError && err.clientError) && count < 2,
      },
      mutations: { retry: 0 },
    },
  })
  app.use(VueQueryPlugin, { queryClient } satisfies VueQueryPluginOptions)
  return queryClient
}
