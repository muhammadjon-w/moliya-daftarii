// Yuklanish uzoq davom etsa true bo'ladi — "server uyg'onmoqda" xabarini ko'rsatish uchun.
import { onBeforeUnmount, ref, watch, type Ref } from "vue"
import { SLOW_LOADING_MS } from "@/constants/app"

export function useSlowLoading(loading: Ref<boolean>) {
  const slow = ref(false)
  let timer: ReturnType<typeof setTimeout> | undefined
  watch(
    loading,
    (on) => {
      clearTimeout(timer)
      slow.value = false
      if (on) timer = setTimeout(() => (slow.value = true), SLOW_LOADING_MS)
    },
    { immediate: true },
  )
  onBeforeUnmount(() => clearTimeout(timer))
  return slow
}
