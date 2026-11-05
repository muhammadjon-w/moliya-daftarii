<script setup lang="ts">
// To'lov sayti (/obuna): Telegram orqali kirish → muddat tanlash → Payme / Click / Click hisobi.
// Bu sahifa mini app ichida emas, oddiy brauzerda ochiladi.
import { computed, ref, watch } from "vue"
import { useRoute } from "vue-router"
import { useCreateOrder, useOrderStatus, useSendInvoice, useSiteMe } from "@/application/billing/queries"
import { ApiError } from "@/application/errors"
import type { TelegramLogin } from "@/application/ports"
import { useUiStore, type Lang } from "@/application/session/ui"
import { fmtDate, num } from "@/domain/money"
import { useI18n } from "@/presentation/i18n"
import TelegramLoginButton from "../components/layout/TelegramLoginButton.vue"

const STORE_KEY = "moliya_tg_login"
const route = useRoute()
const ui = useUiStore()
const { t, lang } = useI18n()
const bot = import.meta.env.VITE_BOT_USERNAME || ""
const LANGS: Lang[] = ["uz", "ru", "en"]

function readLogin(): TelegramLogin | null {
  try {
    const v = sessionStorage.getItem(STORE_KEY)
    return v ? (JSON.parse(v) as TelegramLogin) : null
  } catch {
    return null
  }
}
const login = ref<TelegramLogin | null>(readLogin())
function setLogin(v: TelegramLogin | null) {
  login.value = v
  try {
    if (v) sessionStorage.setItem(STORE_KEY, JSON.stringify(v))
    else sessionStorage.removeItem(STORE_KEY)
  } catch {
    /* xotira yopiq bo'lsa ham sahifa ishlaydi */
  }
}

const me = useSiteMe(login)
watch(me.error, (e) => e instanceof ApiError && e.unauthorized && setLogin(null))

const prices = computed(() => Object.entries(me.data.value?.prices ?? {}).map(([m, v]) => ({ months: Number(m), amount: v })).sort((a, b) => a.months - b.months))
const selected = ref<number | null>(null)
watch(prices, (p) => {
  if (p.length && !p.some((x) => x.months === selected.value)) selected.value = p[0].months
}, { immediate: true })
const bestValue = computed(() => {
  const p = prices.value
  if (p.length < 2) return null
  return p.reduce((best, x) => (x.amount / x.months < best.amount / best.months ? x : best)).months
})

const access = computed(() => me.data.value?.access ?? null)
const stateText = computed(() => {
  const a = access.value
  if (!a) return ""
  return a.state === "expired" ? t("sub_state_expired") : t(a.state === "trial" ? "sub_state_trial" : "sub_state_active", { d: a.daysLeft })
})

const createOrder = useCreateOrder(login)
const sendInvoice = useSendInvoice(login)
const phone = ref("+998 ")
const showInvoice = ref(false)
const orderId = ref<string | null>(typeof route.query.paid === "string" ? route.query.paid : null)
const status = useOrderStatus(login, orderId)
const paid = computed(() => status.data.value?.order.status === "paid")
const paidUntil = computed(() => status.data.value?.access.paidUntil ?? null)

function pay(provider: "payme" | "click") {
  if (!selected.value) return
  createOrder.mutate(
    { months: selected.value, provider },
    { onSuccess: ({ payUrl }) => window.location.assign(payUrl) },
  )
}
function invoice() {
  if (!selected.value) return
  sendInvoice.mutate(
    { months: selected.value, phone: phone.value },
    {
      onSuccess: ({ order }) => {
        orderId.value = order.id
        ui.notify(t("sub_invoice_sent"))
      },
    },
  )
}
const busy = computed(() => createOrder.isPending.value || sendInvoice.isPending.value)
const botLink = bot ? `https://t.me/${bot}` : ""
</script>

<template>
  <main class="sub-page">
    <div class="sub-top">
      <div class="eyebrow">{{ t("app_title") }}</div>
      <div class="lang-switch">
        <button v-for="l in LANGS" :key="l" class="lang-btn" :class="{ active: lang === l }" type="button" @click="ui.setLang(l)">{{ l.toUpperCase() }}</button>
      </div>
    </div>

    <section class="sub-card">
      <h1>{{ t("sub_title") }}</h1>

      <template v-if="!login">
        <p class="sub-lead">{{ t("sub_lead") }}</p>
        <TelegramLoginButton v-if="bot" :bot="bot" @auth="setLogin" />
        <p v-else class="muted-note">{{ t("sub_login_hint") }}</p>
      </template>

      <div v-else-if="me.isPending.value" class="state-box"><span class="spinner" aria-hidden="true"></span>{{ t("loading") }}</div>

      <template v-else-if="me.data.value">
        <div class="sub-user">
          <div>
            <b>{{ t("sub_hello", { n: me.data.value.account.firstName || me.data.value.account.username }) }}</b>
            <div class="sub-state" :class="access?.state">{{ stateText }}</div>
          </div>
          <button class="btn-link" type="button" @click="setLogin(null)">{{ t("sub_logout") }}</button>
        </div>

        <div v-if="paid" class="sub-done">
          <p><b>{{ t("sub_paid") }}</b></p>
          <p v-if="paidUntil">{{ t("sub_until", { d: fmtDate(paidUntil.slice(0, 10)) }) }}</p>
          <a v-if="botLink" class="btn-primary" :href="botLink">{{ t("sub_back") }}</a>
        </div>

        <template v-else>
          <div class="plans" role="radiogroup">
            <button
              v-for="p in prices"
              :key="p.months"
              type="button"
              role="radio"
              class="plan-opt"
              :class="{ on: selected === p.months }"
              :aria-checked="selected === p.months"
              @click="selected = p.months"
            >
              <span v-if="bestValue === p.months" class="plan-tag">{{ t("sub_best") }}</span>
              <span class="plan-m">{{ t("sub_months", { n: p.months }) }}</span>
              <span class="plan-v">{{ num(p.amount) }} {{ t("sum") }}</span>
              <span class="plan-pm">{{ t("sub_per_month", { v: num(p.amount / p.months) }) }}</span>
            </button>
          </div>

          <p class="sub-label">{{ t("sub_pay_with") }}</p>
          <div class="pay-buttons">
            <button class="pay-btn payme" type="button" :disabled="busy" @click="pay('payme')">{{ t("sub_payme") }}</button>
            <button class="pay-btn click" type="button" :disabled="busy" @click="pay('click')">{{ t("sub_click") }}</button>
          </div>
          <button class="btn-link" type="button" @click="showInvoice = !showInvoice">{{ t("sub_invoice") }}</button>
          <form v-if="showInvoice" class="invoice-row" @submit.prevent="invoice">
            <label><span>{{ t("sub_phone") }}</span><input v-model="phone" type="tel" inputmode="tel" autocomplete="tel" /></label>
            <button class="btn-primary" type="submit" :disabled="busy">{{ t("sub_send") }}</button>
          </form>
          <p v-if="orderId && !paid" class="sub-waiting"><span class="spinner" aria-hidden="true"></span>{{ t("sub_waiting") }}</p>
          <p class="muted-note">{{ t("sub_note") }}</p>
        </template>
      </template>

      <div v-else class="state-box error">
        <p>{{ t("load_error") }}</p>
        <button class="btn-primary" type="button" @click="me.refetch()">{{ t("retry") }}</button>
      </div>
    </section>
  </main>
</template>
