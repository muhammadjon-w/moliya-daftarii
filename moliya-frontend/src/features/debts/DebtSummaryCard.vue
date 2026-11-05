<script setup lang="ts">
// Qolgan qarz, to'langan/jami, oylik to'lov va faol qarzlar soni.
import { useI18n } from "@/composables/useI18n"
import ProgressBar from "@/components/ProgressBar.vue"
import type { DebtSummary } from "@/utils/ledger"
import { num } from "@/utils/money"

defineProps<{ summary: DebtSummary }>()
const { t } = useI18n()
</script>

<template>
  <section class="ds">
    <span class="ds__label">{{ t("debt_left") }}</span>
    <p class="ds__value num">{{ num(summary.remaining) }} <small>{{ t("sum") }}</small></p>
    <ProgressBar :value="summary.principal ? (summary.paid / summary.principal) * 100 : 0" tone="red" track="light" />
    <div class="ds__line num">
      <span>{{ t("debt_paid", { v: num(summary.paid) }) }}</span>
      <span>{{ t("debt_total", { v: num(summary.principal) }) }}</span>
    </div>
    <div class="ds__split">
      <div class="ds__cell">
        <span>{{ t("monthly_pay") }}</span>
        <b class="num ds__yellow">{{ num(summary.monthly) }}</b>
      </div>
      <div class="ds__cell">
        <span>{{ t("active_debts") }}</span>
        <b class="num">{{ t("count", { n: summary.openCount }) }}</b>
      </div>
    </div>
  </section>
</template>

<style scoped>
.ds {
  padding: 26px 24px 24px;
  background: var(--hero-debt);
  border: 1px solid rgba(var(--tone-red), 0.22);
  border-radius: var(--r-xl);
  box-shadow: var(--shadow);
}

.ds__label {
  color: var(--text-2);
  font-size: 18px;
}

.ds__value {
  margin: 16px 0 22px;
  font-size: clamp(38px, 12vw, 54px);
  font-weight: 600;
  line-height: 1;
}

.ds__value small {
  color: var(--text-2);
  font-size: 20px;
  font-weight: 400;
}

.ds__line {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  margin: 12px 0 22px;
  color: var(--text-2);
  font-size: 16px;
}

.ds__split {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.ds__cell {
  display: grid;
  gap: 6px;
  padding: 16px 18px;
  background: rgba(7, 13, 26, 0.35);
  border-radius: var(--r-lg);
}

.ds__cell span {
  color: var(--text-2);
  font-size: 16px;
}

.ds__cell b {
  font-size: 26px;
  font-weight: 600;
}

.ds__yellow {
  color: var(--yellow);
}
</style>
