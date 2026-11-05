// Tariflar va to'lov sayti: buyurtma yaratish, Click hisobi, buyurtma holatini kuzatish.
import { useMutation, useQuery } from "@tanstack/vue-query"
import { computed, type Ref } from "vue"
import { queryKeys } from "@/constants/queryKeys"
import type { PayProvider, TelegramLogin } from "@/types/account"
import { billingService } from "../services/billing.service"

export function usePricesQuery() {
  return useQuery({ queryKey: queryKeys.prices, queryFn: billingService.prices, staleTime: 10 * 60_000 })
}

export function useSiteMeQuery(login: Ref<TelegramLogin | null>) {
  return useQuery({
    queryKey: computed(() => queryKeys.siteMe(login.value?.id ?? "anon")),
    queryFn: () => billingService.siteMe(login.value!),
    enabled: computed(() => !!login.value),
  })
}

export function useCreateOrder(login: Ref<TelegramLogin | null>) {
  return useMutation({ mutationFn: (v: { months: number; provider: PayProvider }) => billingService.createOrder(login.value!, v.months, v.provider) })
}

export function useSendInvoice(login: Ref<TelegramLogin | null>) {
  return useMutation({ mutationFn: (v: { months: number; phone: string }) => billingService.sendInvoice(login.value!, v.months, v.phone) })
}

/** To'lov kutilayotganda har 4 soniyada holatni so'raydi, to'langach to'xtaydi. */
export function useOrderStatusQuery(login: Ref<TelegramLogin | null>, orderId: Ref<string | null>) {
  return useQuery({
    queryKey: computed(() => queryKeys.order(orderId.value ?? "-")),
    queryFn: () => billingService.orderStatus(login.value!, orderId.value!),
    enabled: computed(() => !!login.value && !!orderId.value),
    refetchInterval: (q) => (q.state.data?.order.status === "paid" ? false : 4000),
  })
}
