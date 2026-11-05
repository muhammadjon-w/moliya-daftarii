<script setup lang="ts">
import { computed } from "vue"
import { dailyCumulative, debtSummary, monthTransactions, totals, balanceBefore } from "@/domain/ledger"
import { num, shiftMonth, usd } from "@/domain/money"
import { useMonth } from "@/application/ledger/useMonth"
import { useI18n } from "@/presentation/i18n"
import SparkLine from "../common/SparkLine.vue"

const { state, usdRate, period, list, sums, startBalance, plan, opening, today } = useMonth()
const { t, kcompact } = useI18n()

const planIncome = computed(() => Object.entries(plan.value).reduce((s, [k, v]) => (k.startsWith("inc:") ? s + (Number(v) || 0) : s), 0))
const incomeCount = computed(() => list.value.filter((x) => x.type === "income").length)
const debts = computed(() => debtSummary(state.value.debts, today))
const end = computed(() => startBalance.value + sums.value.net)

/** Oxirgi 6 oy: qarz to'lovlari va oy oxiridagi qoldiq */
const history = computed(() => {
  const debt: number[] = []
  const balance: number[] = []
  for (let i = 5; i >= 0; i--) {
    const p = shiftMonth(period.value.y, period.value.m, -i)
    const a = totals(monthTransactions(state.value.transactions, p.y, p.m), usdRate.value)
    debt.push(a.debt)
    balance.push(balanceBefore(state.value.transactions, p.y, p.m, usdRate.value, opening.value) + a.net)
  }
  return { debt, balance }
})
const incSpark = computed(() => dailyCumulative(list.value, period.value.y, period.value.m, usdRate.value, (x) => x.type === "income"))
const outSpark = computed(() => dailyCumulative(list.value, period.value.y, period.value.m, usdRate.value, (x) => x.type !== "income"))
const outRatio = computed(() => (sums.value.inc > 0 ? sums.value.out / sums.value.inc : sums.value.out > 0 ? 1 : 0))
const outCls = computed(() => (sums.value.inc <= 0 ? "bad" : outRatio.value > 1 ? "bad" : outRatio.value > 0.8 ? "warn" : "ok"))
const pct = (r: number) => (Math.max(0, Math.min(r, 1)) * 100).toFixed(1) + "%"
</script>

<template>
  <div class="band kpi-band">
    <RouterLink class="kpi" to="/income">
      <span class="kpi-top"><span>{{ t("k_inc") }}</span><span class="chev" aria-hidden="true">›</span></span>
      <span class="kpi-row"><span class="kpi-val yellow">{{ kcompact(sums.inc) }}</span><SparkLine :values="incSpark" color="var(--amber)" /></span>
      <span class="kpi-sub">
        <template v-if="planIncome > 0">/ {{ kcompact(planIncome) }} {{ t("k_plan") }}, {{ Math.round((sums.inc / planIncome) * 100) }}%</template>
        <template v-else>{{ incomeCount }} {{ t("records") }}</template>
      </span>
      <span class="kpi-sub">{{ sums.incUsd ? usd(sums.incUsd) : "" }}</span>
      <span v-if="planIncome > 0" class="kpi-bar"><i :style="{ width: pct(sums.inc / planIncome) }"></i></span>
    </RouterLink>

    <RouterLink class="kpi" to="/debts">
      <span class="kpi-top"><span>{{ t("k_debt") }}</span><span class="chev" aria-hidden="true">›</span></span>
      <span class="kpi-row"><span class="kpi-val coral">{{ num(debts.remaining) }}</span><SparkLine :values="history.debt" color="var(--coral-text)" /></span>
      <span class="kpi-sub">{{ debts.openCount }} {{ t("debts_n") }}<template v-if="debts.monthly"> · {{ t("per_month") }} {{ kcompact(debts.monthly) }}</template></span>
      <span class="kpi-sub"></span>
    </RouterLink>

    <RouterLink class="kpi" to="/year">
      <span class="kpi-top"><span>{{ t("k_end") }}</span><span class="chev" aria-hidden="true">›</span></span>
      <span class="kpi-row"><span class="kpi-val" :class="{ neg: end < 0 }">{{ (end < 0 ? "−" : "") + num(Math.abs(end)) }}</span><SparkLine :values="history.balance" color="#E8EEF9" /></span>
      <span class="kpi-sub">{{ t("this_month") }} <span class="pos">+{{ kcompact(sums.inc) }}</span> <span class="neg">−{{ kcompact(sums.out) }}</span></span>
      <span class="kpi-sub">{{ sums.incUsd || sums.outUsd ? t("and_usd") + " " + usd(sums.incUsd - sums.outUsd) : "" }}</span>
    </RouterLink>

    <RouterLink class="kpi" to="/expense">
      <span class="kpi-top"><span>{{ t("k_out") }}</span><span class="chev" aria-hidden="true">›</span></span>
      <span class="kpi-row"><span class="kpi-val">{{ kcompact(sums.out) }}</span><SparkLine :values="outSpark" color="var(--green-dark)" /></span>
      <span class="kpi-sub">{{ sums.inc > 0 ? t("of_income").replace("{p}", String(Math.round(outRatio * 100))) : t("no_income") }}</span>
      <span class="kpi-sub">{{ sums.outUsd ? usd(sums.outUsd) : "" }}</span>
      <span class="kpi-bar"><i :class="outCls" :style="{ width: pct(outRatio) }"></i></span>
    </RouterLink>
  </div>
</template>
