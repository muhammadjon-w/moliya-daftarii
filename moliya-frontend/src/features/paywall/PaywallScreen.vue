<script setup lang="ts">
// "Moliya daftari Pro": obuna tugaganda (402) yoki obuna belgisini bosganda ochiladi.
// To'lov Telegram ichida emas — /obuna sahifasi oddiy brauzerda ochiladi (Telegram Login bilan).
import { computed, onBeforeUnmount, onMounted, ref } from "vue"
import { useI18n } from "@/composables/useI18n"
import { useTelegram } from "@/composables/useTelegram"
import AppIcon from "@/components/AppIcon.vue"
import IconTile from "@/components/IconTile.vue"
import PlanOptions from "@/components/PlanOptions.vue"
import { ENV } from "@/constants/app"
import { usePricesQuery } from "@/rest/queries/billing.queries"
import type { Access, PayProvider } from "@/types/account"

const props = defineProps<{ access: Access }>()
const emit = defineEmits<{ close: [] }>()
const { t } = useI18n()
const tg = useTelegram()
const prices = usePricesQuery()
const months = ref<number | null>(null)

const expired = computed(() => props.access.state === "expired")

function pay(provider: PayProvider) {
  const q = new URLSearchParams({ months: String(months.value ?? ""), provider })
  tg.openLink(`${ENV.siteUrl}/obuna?${q}`)
}

function onKey(e: KeyboardEvent) {
  if (e.key === "Escape") emit("close")
}
onMounted(() => document.addEventListener("keydown", onKey))
onBeforeUnmount(() => document.removeEventListener("keydown", onKey))
</script>

<template>
  <Teleport to="body">
    <div class="pw" role="dialog" aria-modal="true" :aria-label="t('pro_title')">
      <button class="pw__close" type="button" :aria-label="t('close')" @click="emit('close')"><AppIcon name="x" /></button>
      <div class="pw__body">
        <IconTile icon="chart" tone="teal" :size="110" :icon-size="44" outlined class="pw__logo" />
        <h2>{{ t("pro_title") }}</h2>
        <p class="pw__lead">{{ expired ? t("pro_expired") : t("pro_lead") }}</p>
        <ul class="pw__features">
          <li><AppIcon name="check" class="positive" />{{ t("pro_f1") }}</li>
          <li><AppIcon name="check" class="positive" />{{ t("pro_f2") }}</li>
          <li><AppIcon name="check" class="positive" />{{ t("pro_f3") }}</li>
        </ul>
        <PlanOptions v-if="prices.data.value" v-model="months" :prices="prices.data.value" />
        <p v-else-if="prices.isError.value" class="muted">{{ t("load_error") }}</p>
      </div>
      <footer class="pw__foot">
        <div class="pw__pay">
          <button class="btn btn--primary" type="button" :disabled="!months" @click="pay('payme')">{{ t("payme") }}</button>
          <button class="btn pw__click" type="button" :disabled="!months" @click="pay('click')">{{ t("click") }}</button>
        </div>
        <p class="pw__note">{{ t("pro_note") }}</p>
      </footer>
    </div>
  </Teleport>
</template>

<style scoped>
.pw {
  position: fixed;
  inset: 0;
  z-index: 60;
  display: flex;
  flex-direction: column;
  max-width: 560px;
  margin: 0 auto;
  background:
    radial-gradient(90% 40% at 50% 0%, rgba(52, 198, 180, 0.12), transparent 70%),
    var(--bg);
  animation: fade 0.2s ease-out;
}

.pw__close {
  position: absolute;
  top: calc(16px + env(safe-area-inset-top, 0px));
  right: 16px;
  display: grid;
  place-items: center;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--surface-2);
}

.pw__body {
  flex: 1;
  overflow-y: auto;
  padding: 60px 20px 20px;
  text-align: center;
}

.pw__logo {
  margin-bottom: 26px;
}

.pw__body h2 {
  font-size: clamp(28px, 8vw, 36px);
  font-weight: 600;
}

.pw__lead {
  max-width: 420px;
  margin: 14px auto 22px;
  color: var(--text-2);
  font-size: 18px;
}

.pw__features {
  display: grid;
  gap: 14px;
  margin: 0 0 28px;
  padding: 0;
  list-style: none;
  text-align: left;
  font-size: 18px;
}

.pw__features li {
  display: flex;
  align-items: center;
  gap: 14px;
}

.pw__foot {
  padding: 12px 20px calc(18px + var(--safe-bottom));
}

.pw__pay {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.pw__pay .btn {
  min-height: 64px;
  border-radius: var(--r-lg);
  font-size: 22px;
}

.pw__click {
  background: var(--click-blue);
  color: var(--text);
}

.pw__note {
  margin-top: 12px;
  color: var(--muted);
  text-align: center;
  font-size: 15px;
}

@keyframes fade {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
}
</style>
