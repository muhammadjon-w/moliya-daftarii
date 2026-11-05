<script setup lang="ts">
// Oylik hisobot: KPI, daromad/chiqim moddalari, qarzlar muddat bo'yicha, reja bajarilishi, kassa.
import { computed } from "vue"
import { byItem, cashReport, changePct, debtBuckets, debtCalc, monthTransactions, planOverview, previousMonth, totals } from "@/domain/ledger"
import { num, signed, usd } from "@/domain/money"
import { useGateways } from "@/application/container"
import { useExportExcel } from "@/application/ledger/mutations"
import { useMonth } from "@/application/ledger/useMonth"
import { useUiStore } from "@/application/session/ui"
import { useI18n } from "@/presentation/i18n"

const ui = useUiStore()
const { platform } = useGateways()
const exporter = useExportExcel()
const { state, usdRate, period, key, list, sums, plan, opening, today } = useMonth()
const { t, monthName, itemLabel, catLabel, methodLabel, sum } = useI18n()

const prev = computed(() => {
  const p = previousMonth(period.value.y, period.value.m)
  return totals(monthTransactions(state.value.transactions, p.y, p.m), usdRate.value)
})
const spend = computed(() => sums.value.pay + sums.value.exp)
const prevText = (v: number, pv: number) => {
  const d = changePct(v, pv)
  return d === null ? "" : t("rp_prev").replace("{p}", (d > 0 ? "+" : d < 0 ? "−" : "") + Math.abs(d) + "%")
}
const ofInc = (v: number) => t("rp_of_inc").replace("{p}", String(Math.round((v / sums.value.inc) * 100)))

const kpis = computed(() => {
  const a = sums.value
  return [
    { label: "rp_inc", cls: "inc", value: num(a.inc), sub: prevText(a.inc, prev.value.inc) },
    { label: "rp_exp", cls: "exp", value: num(spend.value), sub: a.inc > 0 ? ofInc(spend.value) : prevText(spend.value, prev.value.pay + prev.value.exp) },
    { label: "rp_debt", cls: "debt", value: num(a.debt), sub: a.inc > 0 && a.debt ? ofInc(a.debt) : "" },
    { label: "rp_net", cls: a.net < 0 ? "neg" : "pos", value: signed(a.net), sub: a.inc > 0 ? (a.net < 0 ? "−" : "+") + Math.abs(Math.round((a.net / a.inc) * 100)) + "%" : "" },
  ]
})
const incomeItems = computed(() => byItem(list.value, usdRate.value, true))
const outItems = computed(() => byItem(list.value, usdRate.value, false))
const buckets = computed(() => debtBuckets(state.value.debts, today))
const biggest = computed(() =>
  state.value.debts
    .map((d) => ({ d, c: debtCalc(d, today) }))
    .filter((o) => o.c.remaining > 0)
    .sort((a, b) => b.c.remaining - a.c.remaining)
    .slice(0, 5)
    .map((o) => `${o.d.lender || t("unnamed")} — ${num(o.c.remaining)}`)
    .join(" · "),
)
const planInfo = computed(() => planOverview(list.value, plan.value, usdRate.value))
const pctDone = (f: number, p: number) => (p ? Math.round((f / p) * 100) + "% " + t("rp_done") : "")
const cash = computed(() => cashReport(state.value.transactions, period.value.y, period.value.m))

function exportExcel() {
  exporter.mutate(key.value, { onSuccess: () => (ui.notify(t("export_sent")), platform.haptic("success")) })
}
</script>

<template>
  <section>
    <div class="rp-head">
      <div>
        <h2>{{ t("rp_title") }} {{ monthName(period.m) }} {{ period.y }}</h2>
        <div class="rp-sub">{{ (t("app_title") + (platform.userFirstName ? " · " + platform.userFirstName : "")).toUpperCase() }}</div>
      </div>
      <div class="rp-actions">
        <button class="rp-btn" type="button" aria-label="‹" @click="ui.shift(-1)">←</button>
        <button class="rp-btn" type="button" aria-label="›" @click="ui.shift(1)">→</button>
        <button class="btn-ghost" type="button" :disabled="exporter.isPending.value" @click="exportExcel">{{ t("export_bot") }}</button>
      </div>
    </div>

    <div class="rp-kpis">
      <div v-for="k in kpis" :key="k.label" class="rp-card">
        <span class="lbl">{{ t(k.label) }}</span>
        <span class="rp-val" :class="k.cls">{{ k.value }}</span>
        <div class="rp-pct">{{ k.sub }}</div>
      </div>
    </div>

    <div class="rp-grid">
      <div class="rp-panel">
        <h3>{{ t("rp_inc_list") }}</h3>
        <div class="rp-body">
          <p v-if="!incomeItems.length" class="rp-empty">{{ t("rp_empty_inc") }}</p>
          <template v-else>
            <div v-for="r in incomeItems" :key="r.key" class="rp-row"><span>{{ itemLabel(r.key) }}</span><b>{{ num(r.value) }}</b></div>
            <div class="rp-row total"><span>{{ t("total") }}</span><b>{{ num(sums.inc) }}</b></div>
          </template>
        </div>
      </div>

      <div class="rp-panel">
        <h3>{{ t("rp_out_list") }}</h3>
        <div class="rp-body">
          <p v-if="!outItems.length" class="rp-empty">{{ t("rp_empty_out") }}</p>
          <template v-else>
            <div v-for="r in outItems" :key="r.key" class="rp-row"><span>{{ itemLabel(r.key) }}<small>{{ t("b_" + r.group) }}</small></span><b>{{ num(r.value) }}</b></div>
            <div class="rp-row total"><span>{{ t("total") }}</span><b>{{ num(sums.out) }}</b></div>
            <div class="rp-row sub"><span>{{ t("g_pay") }}</span><b>{{ num(sums.pay) }}</b></div>
            <div class="rp-row sub"><span>{{ t("g_exp") }}</span><b>{{ num(sums.exp) }}</b></div>
            <div class="rp-row sub"><span>{{ t("g_debt") }}</span><b>{{ num(sums.debt) }}</b></div>
          </template>
        </div>
      </div>

      <div class="rp-panel">
        <h3>{{ t("rp_debts") }}</h3>
        <div class="rp-body">
          <p v-if="!buckets.total" class="rp-empty">{{ t("rp_no_debts") }}</p>
          <template v-else>
            <div class="rp-row"><span>{{ t("b_overdue") }}</span><b :class="{ coral: buckets.overdue }">{{ num(buckets.overdue) }}</b></div>
            <div class="rp-row"><span>{{ t("b_30") }}</span><b>{{ num(buckets.d30) }}</b></div>
            <div class="rp-row"><span>{{ t("b_60") }}</span><b>{{ num(buckets.d60) }}</b></div>
            <div class="rp-row"><span>{{ t("b_later") }}</span><b>{{ num(buckets.later) }}</b></div>
            <div class="rp-row total"><span>{{ t("total") }}</span><b>{{ num(buckets.total) }}</b></div>
            <p class="rp-note">{{ t("rp_biggest") }}: {{ biggest }}</p>
          </template>
        </div>
      </div>

      <div class="rp-panel">
        <h3>{{ t("rp_plan") }}</h3>
        <div class="rp-body">
          <template v-if="!planInfo.income && !planInfo.outflow">
            <p class="rp-empty">{{ t("rp_no_plan") }}</p>
            <RouterLink class="link-btn" to="/plan">{{ t("rp_set_plan") }}</RouterLink>
          </template>
          <template v-else>
            <div class="rp-row"><span>{{ t("rp_plan_inc") }}</span><b>{{ num(planInfo.income) }} / {{ num(sums.inc) }}</b></div>
            <div class="rp-row sub"><span></span><b>{{ pctDone(sums.inc, planInfo.income) }}</b></div>
            <div class="rp-row"><span>{{ t("rp_plan_out") }}</span><b>{{ num(planInfo.outflow) }} / {{ num(sums.out) }}</b></div>
            <div class="rp-row sub"><span></span><b>{{ pctDone(sums.out, planInfo.outflow) }}</b></div>
            <p class="rp-note">
              {{ t("rp_over") }}:
              {{ planInfo.overruns.length ? planInfo.overruns.slice(0, 4).map((o) => catLabel(o.category) + " +" + num(o.over)).join(" · ") : t("rp_no_over") }}
            </p>
          </template>
        </div>
      </div>
    </div>

    <div class="rp-panel" style="margin-bottom: 24px">
      <h3>{{ t("rp_cash") }}</h3>
      <div class="rp-table-wrap">
        <table class="rp-table">
          <thead>
            <tr><th>{{ t("c_kassa") }}</th><th>{{ t("c_start") }}</th><th>{{ t("c_in") }}</th><th>{{ t("c_out") }}</th><th>{{ t("c_end") }}</th></tr>
          </thead>
          <tbody>
            <tr v-for="r in cash.byMethod" :key="r.method">
              <td>{{ methodLabel(r.method) }}</td><td>{{ signed(r.row.start) }}</td><td class="in">{{ num(r.row.inflow) }}</td>
              <td class="out">{{ num(r.row.outflow) }}</td><td class="end">{{ signed(r.row.end) }}</td>
            </tr>
            <tr class="total">
              <td>{{ t("c_total") }}</td><td>{{ signed(cash.total.start) }}</td><td class="in">{{ num(cash.total.inflow) }}</td>
              <td class="out">{{ num(cash.total.outflow) }}</td><td class="end">{{ signed(cash.total.end) }}</td>
            </tr>
            <tr v-if="cash.usd">
              <td>{{ t("c_usd") }}</td><td>{{ usd(cash.usd.start) }}</td><td class="in">{{ usd(cash.usd.inflow) }}</td>
              <td class="out">{{ usd(cash.usd.outflow) }}</td><td class="end">{{ usd(cash.usd.end) }}</td>
            </tr>
          </tbody>
        </table>
        <p v-if="opening" class="rp-note rp-table-note">{{ t("rp_opening_note").replace("{v}", sum(opening)) }}</p>
      </div>
    </div>
  </section>
</template>
