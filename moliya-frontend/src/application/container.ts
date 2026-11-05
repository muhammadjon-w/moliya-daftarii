// Vue'ning provide/inject mexanizmi orqali portlarni komponentlarga yetkazish.
import { inject, type InjectionKey } from "vue"
import type { Gateways } from "./ports"

export const GATEWAYS: InjectionKey<Gateways> = Symbol("gateways")

export function useGateways(): Gateways {
  const g = inject(GATEWAYS)
  if (!g) throw new Error("Gateways provide qilinmagan (app/container.ts)")
  return g
}
