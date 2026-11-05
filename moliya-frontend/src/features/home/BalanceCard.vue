<script setup lang="ts">
// Oy oxiridagi qoldiq, tushum/chiqim va "tushumning N% sarflandi".
import { computed } from "vue"
import { useI18n } from "@/composables/useI18n"
import { useSheets } from "@/composables/useSheets"
import ProgressBar from "@/components/ProgressBar.vue"
import type { Access } from "@/types/account"
import { percent, type Totals } from "@/utils/ledger"
import { num } from "@/utils/money"

const props = defineProps<{ balance: number; sums: Totals; access: Access }>()
const sheets = useSheets()
const { t, compact } = useI18n()

const spent = computed(() => percent(props.sums.out, props.sums.inc))
const badge = computed(() => {
  const a = props.access
  if (a.state === "expired") return { text: t("badge_expired"), cls: "badge--red" }
  return { text: t(a.state === "trial" ? "badge_trial" : "badge_active", { d: a.daysLeft }), cls: a.state === "trial" ? "badge--yellow" : "badge--teal" }
})
</script>

<template>
  <section class="bc">
    <div class="bc__top">
      <span class="bc__label">{{ t("end_balance") }}</span>
      <button class="badge" :class="badge.cls" type="button" @click="sheets.paywall()">{{ badge.text }}</button>
    </div>
    <p class="bc__value num" :class="{ negative: balance < 0 }">
      {{ balance < 0 ? "−" : "" }}{{ num(Math.abs(balance)) }} <small>{{ t("sum") }}</small>
    </p>
    <div class="bc__split">
      <div class="bc__cell">
        <span>{{ t("income") }}</span>
        <b class="positive num">+{{ compact(sums.inc) }}</b>
      </div>
      <div class="bc__cell">
        <span>{{ t("expense") }}</span>
        <b class="negative num">−{{ compact(sums.out) }}</b>
      </div>
    </div>
    <ProgressBar :value="spent ?? 0" :tone="(spent ?? 0) > 100 ? 'red' : 'teal'" track="light" />
    <p class="bc__note">{{ spent === null ? t("no_income") : t("spent_pct", { p: spent }) }}</p>
  </section>
</template>

<style scoped>
.bc {
  padding: 26px 24px 24px;
  background: var(--hero);
  border: 1px solid rgba(122, 167, 255, 0.25);
  border-radius: var(--r-xl);
  box-shadow: var(--shadow);
}

.bc__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.bc__label {
  color: var(--text-2);
  font-size: 18px;
}

.badge {
  padding: 8px 16px;
  border-radius: var(--r-pill);
  font-size: 15px;
  font-weight: 600;
  white-space: nowrap;
}

.badge--yellow {
  background: rgba(var(--tone-yellow), 0.16);
  color: var(--yellow);
}

.badge--teal {
  background: rgba(var(--tone-teal), 0.16);
  color: var(--teal);
}

.badge--red {
  background: rgba(var(--tone-red), 0.18);
  color: var(--red);
}

.bc__value {
  margin: 18px 0 22px;
  font-size: clamp(38px, 12vw, 54px);
  font-weight: 600;
  line-height: 1;
  letter-spacing: -0.01em;
}

.bc__value small {
  color: var(--text-2);
  font-size: 20px;
  font-weight: 400;
}

.bc__split {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 22px;
}

.bc__cell {
  display: grid;
  gap: 6px;
  padding: 16px 18px;
  background: rgba(7, 13, 26, 0.35);
  border-radius: var(--r-lg);
}

.bc__cell span {
  color: var(--text-2);
  font-size: 16px;
}

.bc__cell b {
  font-size: clamp(20px, 6.4vw, 26px);
  font-weight: 600;
}

.bc__note {
  margin-top: 12px;
  color: var(--text-2);
  font-size: 15px;
}
</style>
