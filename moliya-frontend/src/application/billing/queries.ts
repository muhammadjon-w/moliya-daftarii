// To'lov sayti: tariflar, buyurtma yaratish, Click hisobi, buyurtma holatini kuzatish.
import { useMutation, useQuery } from "@tanstack/vue-query"
import { computed, type Ref } from "vue"
import { useGateways } from "../container"
import type { TelegramLogin } from "../ports"
import { queryKeys } from "../queryKeys"

export function usePrices() {
  const { billing } = useGateways()
  return useQuery({ queryKey: queryKeys.prices, queryFn: () => billing.prices(), staleTime: 10 * 60_000 })
}

export function useSiteMe(login: Ref<TelegramLogin | null>) {
  const { billing } = useGateways()
  return useQuery({
    queryKey: computed(() => queryKeys.siteMe(login.value?.id ?? "anon")),
    queryFn: () => billing.siteMe(login.value!),
    enabled: computed(() => !!login.value),
  })
}

export function useCreateOrder(login: Ref<TelegramLogin | null>) {
  const { billing } = useGateways()
  return useMutation({ mutationFn: (v: { months: number; provider: "payme" | "click" }) => billing.createOrder(login.value!, v.months, v.provider) })
}

export function useSendInvoice(login: Ref<TelegramLogin | null>) {
  const { billing } = useGateways()
  return useMutation({ mutationFn: (v: { months: number; phone: string }) => billing.sendInvoice(login.value!, v.months, v.phone) })
}

/** To'lov kutilayotganda har 4 soniyada holatni so'raydi, to'langach to'xtaydi. */
export function useOrderStatus(login: Ref<TelegramLogin | null>, orderId: Ref<string | null>) {
  const { billing } = useGateways()
  return useQuery({
    queryKey: computed(() => queryKeys.order(orderId.value ?? "-")),
    queryFn: () => billing.orderStatus(login.value!, orderId.value!),
    enabled: computed(() => !!login.value && !!orderId.value),
    refetchInterval: (q) => (q.state.data?.order.status === "paid" ? false : 4000),
  })
}
