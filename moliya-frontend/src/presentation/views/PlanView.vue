<script setup lang="ts">
import { computed } from "vue"
import { planSections } from "@/domain/ledger"
import { useCopyPreviousPlan, useSavePlan, useUpdateSettings } from "@/application/ledger/mutations"
import { useMonth } from "@/application/ledger/useMonth"
import { useUiStore } from "@/application/session/ui"
import { useI18n } from "@/presentation/i18n"
import { monthKey, shiftMonth } from "@/domain/money"
import MoneyInput from "../components/common/MoneyInput.vue"

const ui = useUiStore()
const { state, usdRate, period, key, list, sums, plan, startBalance, opening } = useMonth()
const savePlan = useSavePlan()
const copyPlan = useCopyPreviousPlan()
const updateSettings = useUpdateSettings()
const { t, monthName, catLabel, groupLabel, sum, signedSum } = useI18n()

const sections = computed(() => planSections(list.value, plan.value, usdRate.value))
const planned = computed(() => Object.fromEntries(sections.value.map((s) => [s.group, s.plan])) as Record<string, number>)
const planNet = computed(() => planned.value.inc - planned.value.pay - planned.value.exp - planned.value.debt)

const overview = computed(() => [
  { label: t("g_inc"), plan: planned.value.inc, fact: sums.value.inc },
  { label: t("g_pay"), plan: planned.value.pay, fact: sums.value.pay },
  { label: t("g_exp"), plan: planned.value.exp, fact: sums.value.exp },
  { label: t("g_debt"), plan: planned.value.debt, fact: sums.value.debt },
  { label: t("ov_net"), plan: planNet.value, fact: sums.value.net, strong: true },
  { label: t("ov_capital"), plan: startBalance.value + planNet.value, fact: startBalance.value + sums.value.net, strong: true },
])

function setPlan(planKey: string, v: number) {
  const values = { ...plan.value }
  if (v > 0) values[planKey] = v
  else delete values[planKey]
  if ((plan.value[planKey] ?? 0) === (values[planKey] ?? 0)) return
  savePlan.mutate({ month: key.value, values })
}
function copyPrevious() {
  const p = shiftMonth(period.value.y, period.value.m, -1)
  if (!Object.keys(state.value.plans[monthKey(p.y, p.m)] ?? {}).length) {
    ui.notify(t("plan_none"))
    return
  }
  copyPlan.mutate(key.value, { onSuccess: () => ui.notify(t("plan_copied")) })
}
function setOpening(v: number) {
  const n = Number.isFinite(v) ? v : 0
  if (n !== opening.value) updateSettings.mutate({ openingBalance: n })
}
const diffText = (d: number) => (d < 0 ? "−" : "+") + " " + sum(Math.abs(d))
const progress = (isInc: boolean, p: number, f: number) => {
  const pct = p ? f / p : 0
  return { width: Math.min(pct * 100, 100).toFixed(1) + "%", cls: isInc ? (pct >= 1 ? "" : "short") : pct > 1 ? "over" : "" }
}
</script>

<template>
  <section>
    <div class="plan-overview">
      <div class="panel">
        <h2><span>{{ t("ov_title") }}</span><small>{{ monthName(period.m) }} {{ period.y }}</small></h2>
        <table class="ov-table">
          <thead><tr><th>{{ t("th_name") }}</th><th>{{ t("th_plan") }}</th><th>{{ t("th_fact") }}</th></tr></thead>
          <tbody>
            <tr v-for="r in overview" :key="r.label" :class="{ strong: r.strong }">
              <td>{{ r.label }}</td><td class="v">{{ signedSum(r.plan) }}</td><td class="v">{{ signedSum(r.fact) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="panel">
        <h2><span>{{ t("sav_title") }}</span></h2>
        <table class="ov-table">
          <tbody>
            <tr><td>{{ t("sav_prev") }}</td><td class="v" :style="{ color: startBalance < 0 ? 'var(--brick)' : 'inherit' }">{{ signedSum(startBalance) }}</td></tr>
            <tr><td>{{ t("sav_net") }}</td><td class="v" :style="{ color: sums.net < 0 ? 'var(--brick)' : 'inherit' }">{{ signedSum(sums.net) }}</td></tr>
            <tr class="strong">
              <td>{{ t("sav_end") }}</td>
              <td class="v" :style="{ color: startBalance + sums.net < 0 ? 'var(--brick)' : 'inherit' }">{{ signedSum(startBalance + sums.net) }}</td>
            </tr>
          </tbody>
        </table>
        <div class="open-row">
          <label for="openInput">{{ t("opening") }}</label>
          <MoneyInput id="openInput" class="num-input" :model-value="opening" allow-negative zero-as-text @commit="setOpening" />
        </div>
        <p class="muted-note">{{ t("opening_note") }}</p>
      </div>
    </div>

    <div class="toolbar">
      <h2>{{ t("plan_title") }}</h2>
      <div class="tool-actions">
        <button class="btn-ghost" type="button" :disabled="copyPlan.isPending.value" @click="copyPrevious">{{ t("copy_plan") }}</button>
      </div>
    </div>

    <div class="plan-sections">
      <div v-for="s in sections" :key="s.group">
        <div class="sec-head">
          <h3>{{ groupLabel(s.group) }}</h3>
          <small>{{ t("th_plan") }} {{ sum(s.plan) }} · {{ t("th_fact") }} {{ sum(s.fact) }}</small>
        </div>
        <div class="table-scroll">
          <table class="plan-table">
            <thead>
              <tr>
                <th>{{ t("th_cat") }}</th><th class="num">{{ t("th_plan") }}</th><th class="num">{{ t("th_fact") }}</th>
                <th class="num">{{ t("th_diff") }}</th><th>{{ t("th_progress") }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in s.rows" :key="r.key">
                <td class="cat">{{ catLabel(r.category) }}</td>
                <td class="num">
                  <MoneyInput :model-value="r.plan" placeholder="0" :aria-label="t('th_plan') + ' ' + catLabel(r.category)" @commit="(v) => setPlan(r.key, v)" />
                </td>
                <td class="num"><template v-if="r.fact">{{ sum(r.fact) }}</template><span v-else style="color: var(--muted); font-weight: 500">0</span></td>
                <td class="num diff" :class="!r.plan ? '' : r.diff >= 0 ? 'good' : 'bad'">{{ r.plan ? diffText(r.diff) : "—" }}</td>
                <td>
                  <div v-if="r.plan" class="prog">
                    <i :class="progress(s.group === 'inc', r.plan, r.fact).cls" :style="{ width: progress(s.group === 'inc', r.plan, r.fact).width }"></i>
                  </div>
                </td>
              </tr>
            </tbody>
            <tfoot>
              <tr>
                <td>{{ t("total") }}</td><td class="num">{{ sum(s.plan) }}</td><td class="num">{{ sum(s.fact) }}</td>
                <td class="num diff" :class="s.plan ? (s.diff >= 0 ? 'good' : 'bad') : ''">{{ s.plan ? diffText(s.diff) : "—" }}</td><td></td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    </div>
  </section>
</template>
