<script setup lang="ts">
import { storeToRefs } from "pinia"
import { computed } from "vue"
import { useRoute } from "vue-router"
import { useGateways } from "@/application/container"
import { useLedgerState } from "@/application/ledger/queries"
import { useUpdateSettings } from "@/application/ledger/mutations"
import { useUiStore, type Lang } from "@/application/session/ui"
import { useI18n } from "@/presentation/i18n"
import MoneyInput from "../common/MoneyInput.vue"
import TabNav from "./TabNav.vue"

const route = useRoute()
const ui = useUiStore()
const { period } = storeToRefs(ui)
const { platform } = useGateways()
const { state, usdRate, query } = useLedgerState()
const updateSettings = useUpdateSettings()
const { t, lang, monthName, greeting, todayText } = useI18n()

const isYear = computed(() => route.meta.tab === "year")
const showMonthNav = computed(() => route.meta.tab !== "debts" && route.meta.tab !== "report")
const label = computed(() => (isYear.value ? String(period.value.y) : monthName(period.value.m) + " " + period.value.y))
const access = computed(() => (query.data.value ? state.value.access : null))
const accessText = computed(() => {
  const a = access.value
  if (!a) return ""
  if (a.state === "expired") return t("expired_badge")
  return t(a.state === "trial" ? "trial_left" : "active_left", { d: a.daysLeft })
})
const LANGS: Lang[] = ["uz", "ru", "en"]

function shift(d: number) {
  ui.shift(d, isYear.value ? "year" : "month")
  platform.haptic("light")
}
function saveRate(v: number) {
  if (v > 0 && v !== usdRate.value) updateSettings.mutate({ usdRate: v })
}
</script>

<template>
  <header class="masthead">
    <div class="masthead-top">
      <div class="greet-wrap">
        <div class="eyebrow">{{ t("app_title") }}</div>
        <h1>{{ greeting(platform.userFirstName) }}</h1>
        <div class="greet-date">{{ todayText() }}</div>
      </div>
      <RouterLink class="btn-teal" to="/report">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M3 3v18h18" /><path d="M7 15l4-4 3 3 5-6" />
        </svg>
        <span>{{ t("annual_btn") }}</span>
      </RouterLink>
    </div>
    <TabNav />
    <div class="sub-row">
      <div class="sub-left">
        <div v-if="showMonthNav" class="month-nav">
          <button class="nav-btn" type="button" aria-label="‹" @click="shift(-1)">‹</button>
          <strong>{{ label }}</strong>
          <button class="nav-btn" type="button" aria-label="›" @click="shift(1)">›</button>
        </div>
        <div class="rate-inline">
          <label for="rateInput">1 $ =</label>
          <MoneyInput id="rateInput" :model-value="usdRate" @commit="saveRate" />
          <span>{{ t("sum") }}</span>
        </div>
        <button v-if="access" type="button" class="access-pill" :class="access.state" @click="access.state === 'expired' && (ui.paywallOpen = true)">
          {{ accessText }}
        </button>
      </div>
      <div class="lang-switch">
        <button v-for="l in LANGS" :key="l" class="lang-btn" :class="{ active: lang === l }" type="button" @click="ui.setLang(l)">{{ l.toUpperCase() }}</button>
      </div>
    </div>
  </header>
</template>
