<script setup lang="ts">
// Rasmiy Telegram Login Widget. Imzoni server bot tokeni bilan tekshiradi.
import { onBeforeUnmount, onMounted, ref } from "vue"
import type { TelegramLogin } from "@/types/account"

const props = defineProps<{ bot: string }>()
const emit = defineEmits<{ auth: [TelegramLogin] }>()
const host = ref<HTMLElement | null>(null)
const CALLBACK = "__moliyaTelegramAuth"

onMounted(() => {
  ;(window as unknown as Record<string, unknown>)[CALLBACK] = (user: TelegramLogin) => emit("auth", user)
  const s = document.createElement("script")
  s.async = true
  s.src = "https://telegram.org/js/telegram-widget.js?22"
  s.setAttribute("data-telegram-login", props.bot)
  s.setAttribute("data-size", "large")
  s.setAttribute("data-radius", "12")
  s.setAttribute("data-request-access", "write")
  s.setAttribute("data-onauth", CALLBACK + "(user)")
  host.value?.appendChild(s)
})
onBeforeUnmount(() => delete (window as unknown as Record<string, unknown>)[CALLBACK])
</script>

<template>
  <div ref="host" class="tg-login"></div>
</template>

<style scoped>
.tg-login {
  display: flex;
  justify-content: center;
  min-height: 48px;
  margin-top: 18px;
}
</style>
