<script setup lang="ts">
// To'lov sayti (/obuna): Telegram orqali kirish → muddat tanlash → Payme / Click / Click hisobi.
// Mini app ichida emas, oddiy brauzerda ochiladi. ?months=12&provider=payme — mini app'dan kelganda oldindan tanlanadi.
import { computed, ref, watch } from "vue"
import { useRoute } from "vue-router"
import { useI18n } from "@/composables/useI18n"
import { useUi } from "@/composables/useUi"
import IconTile from "@/components/IconTile.vue"
import PlanOptions from "@/components/PlanOptions.vue"
import SegmentedControl from "@/components/SegmentedControl.vue"
import { ENV, STORAGE_KEYS } from "@/constants/app"
import TelegramLoginButton from "@/features/subscribe/TelegramLoginButton.vue"
import { LANGS } from "@/plugins/i18n"
import { ApiError } from "@/rest/client"
import { useCreateOrder, useOrderStatusQuery, useSendInvoice, useSiteMeQuery } from "@/rest/queries/billing.queries"
import type { PayProvider, TelegramLogin } from "@/types/account"
import type { Lang } from "@/types/ui"
import { fmtDate } from "@/utils/money"

const route = useRoute()
const { ui, setLang, notify } = useUi()
const { t } = useI18n()

function readLogin(): TelegramLogin | null {
  try {
    const v = sessionStorage.getItem(STORAGE_KEYS.telegramLogin)
    return v ? (JSON.parse(v) as TelegramLogin) : null
  } catch {
    return null
  }
}
const login = ref<TelegramLogin | null>(readLogin())
function setLogin(v: TelegramLogin | null) {
  login.value = v
  try {
    if (v) sessionStorage.setItem(STORAGE_KEYS.telegramLogin, JSON.stringify(v))
    else sessionStorage.removeItem(STORAGE_KEYS.telegramLogin)
  } catch {
    /* xotira yopiq bo'lsa ham sahifa ishlaydi */
  }
}

const me = useSiteMeQuery(login)
watch(me.error, (e) => e instanceof ApiError && e.unauthorized && setLogin(null))

const months = ref<number | null>(Number(route.query.months) || null)
const preferred = route.query.provider === "click" ? "click" : route.query.provider === "payme" ? "payme" : null

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
const status = useOrderStatusQuery(login, orderId)
const paid = computed(() => status.data.value?.order.status === "paid")
const paidUntil = computed(() => status.data.value?.access.paidUntil ?? null)
const busy = computed(() => createOrder.isPending.value || sendInvoice.isPending.value)
const botLink = ENV.botUsername ? `https://t.me/${ENV.botUsername}` : ""

function pay(provider: PayProvider) {
  if (!months.value) return
  createOrder.mutate({ months: months.value, provider }, { onSuccess: ({ payUrl }) => window.location.assign(payUrl) })
}
function invoice() {
  if (!months.value) return
  sendInvoice.mutate(
    { months: months.value, phone: phone.value },
    {
      onSuccess: ({ order }) => {
        orderId.value = order.id
        notify(t("sub_invoice_sent"))
      },
    },
  )
}

const langOptions = LANGS.map((l) => ({ value: l, label: l.toUpperCase() }))
const lang = computed<Lang>({ get: () => ui.lang, set: setLang })
</script>

<template>
  <main class="page page--standalone sp">
    <div class="sp__top">
      <SegmentedControl v-model="lang" :options="langOptions" :label="t('language')" class="sp__lang" />
    </div>

    <IconTile icon="chart" tone="teal" :size="96" :icon-size="40" outlined class="sp__logo" />
    <h1>{{ t("pro_title") }}</h1>

    <template v-if="!login">
      <p class="sp__lead">{{ t("sub_login") }}</p>
      <TelegramLoginButton v-if="ENV.botUsername" :bot="ENV.botUsername" @auth="setLogin" />
      <p v-else class="muted">{{ t("sub_login_hint") }}</p>
    </template>

    <p v-else-if="me.isPending.value" class="sp__lead">{{ t("loading") }}</p>

    <template v-else-if="me.data.value">
      <div class="card sp__user">
        <div>
          <b>{{ t("sub_hello", { n: me.data.value.account.firstName || me.data.value.account.username || "" }) }}</b>
          <div class="sp__state" :class="access?.state">{{ stateText }}</div>
        </div>
        <button class="link" type="button" @click="setLogin(null)">{{ t("sub_logout") }}</button>
      </div>

      <div v-if="paid" class="card sp__done">
        <p><b>{{ t("sub_paid") }}</b></p>
        <p v-if="paidUntil">{{ t("sub_until", { d: fmtDate(paidUntil.slice(0, 10)) }) }}</p>
        <a v-if="botLink" class="btn btn--primary" :href="botLink">{{ t("sub_back") }}</a>
      </div>

      <template v-else>
        <PlanOptions v-model="months" :prices="me.data.value.prices" class="sp__plans" />
        <div class="sp__pay">
          <button class="btn btn--primary" :class="{ 'sp__pref': preferred === 'payme' }" type="button" :disabled="busy || !months" @click="pay('payme')">{{ t("payme") }}</button>
          <button class="btn sp__click" :class="{ 'sp__pref': preferred === 'click' }" type="button" :disabled="busy || !months" @click="pay('click')">{{ t("click") }}</button>
        </div>
        <button class="link sp__inv-toggle" type="button" @click="showInvoice = !showInvoice">{{ t("sub_invoice") }}</button>
        <form v-if="showInvoice" class="sp__invoice" @submit.prevent="invoice">
          <label class="field">
            <span class="field__label">{{ t("sub_phone") }}</span>
            <input v-model="phone" class="input" type="tel" inputmode="tel" autocomplete="tel" />
          </label>
          <button class="btn btn--ghost btn--block" type="submit" :disabled="busy">{{ t("sub_send") }}</button>
        </form>
        <p v-if="orderId && !paid" class="sp__lead">{{ t("sub_waiting") }}</p>
        <p class="muted sp__note">{{ t("pro_note") }}</p>
      </template>
    </template>

    <div v-else class="sp__error">
      <p>{{ t("load_error") }}</p>
      <button class="btn btn--primary" type="button" @click="me.refetch()">{{ t("retry") }}</button>
    </div>
  </main>
</template>

<style scoped>
.sp {
  text-align: center;
}

.sp__top {
  display: flex;
  justify-content: flex-end;
}

.sp__lang {
  width: 200px;
}

.sp__logo {
  margin: 20px 0 22px;
}

.sp h1 {
  font-size: 32px;
  font-weight: 600;
}

.sp__lead {
  margin: 14px 0;
  color: var(--text-2);
  font-size: 18px;
}

.sp__user {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin: 22px 0;
  padding: 18px 20px;
  border-radius: var(--r-lg);
  text-align: left;
}

.sp__state {
  margin-top: 4px;
  color: var(--yellow);
  font-size: 15px;
}

.sp__state.active {
  color: var(--teal);
}

.sp__state.expired {
  color: var(--red);
}

.sp__plans {
  text-align: left;
}

.sp__pay {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  margin-top: 22px;
}

.sp__pay .btn {
  min-height: 62px;
  border-radius: var(--r-lg);
  font-size: 21px;
}

.sp__click {
  background: var(--click-blue);
  color: var(--text);
}

.sp__pref {
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.25);
}

.sp__inv-toggle {
  margin-top: 18px;
  font-size: 16px;
}

.sp__invoice {
  display: grid;
  gap: 12px;
  text-align: left;
}

.sp__note {
  margin-top: 16px;
  font-size: 15px;
}

.sp__done {
  display: grid;
  gap: 10px;
  justify-items: center;
  padding: 24px;
}

.sp__error {
  display: grid;
  justify-items: center;
  gap: 14px;
  margin-top: 28px;
}
</style>
