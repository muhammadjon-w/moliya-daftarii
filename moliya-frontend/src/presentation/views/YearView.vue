<script setup lang="ts">
import { computed } from "vue"
import { yearRows, totals } from "@/domain/ledger"
import { monthKey } from "@/domain/money"
import { useMonth } from "@/application/ledger/useMonth"
import { useI18n } from "@/presentation/i18n"
import CategoryBars from "../components/dashboard/CategoryBars.vue"
import YearChart from "../components/dashboard/YearChart.vue"

const { state, usdRate, period, opening } = useMonth()
const { t, months, sum, signedSum } = useI18n()

const now = new Date()
const thisMonth = monthKey(now.getFullYear(), now.getMonth())
const rows = computed(() => yearRows(state.value.transactions, period.value.y, usdRate.value, opening.value))
const yearList = computed(() => state.value.transactions.filter((x) => x.date.startsWith(period.value.y + "-")))
const total = computed(() => totals(yearList.value, usdRate.value))
const chartData = computed(() => rows.value.map((r) => ({ m: r.m, inc: r.totals.inc, out: r.totals.out, hl: monthKey(period.value.y, r.m) === thisMonth })))
const endBalance = computed(() => rows.value[11]?.end ?? 0)
const expTotal = computed(() => total.value.out)
</script>

<template>
  <section>
    <div class="panel chart" style="margin-bottom: 18px">
      <h2>
        <span>{{ t("year_chart") }} {{ period.y }}</span>
        <span class="legend"><span style="--c: var(--green)">{{ t("g_inc") }}</span><span style="--c: var(--brick)">{{ t("l_out") }}</span></span>
      </h2>
      <YearChart :months="chartData" :label="t('year_chart')" />
    </div>

    <div class="toolbar"><h2>{{ t("year_title") }} · {{ period.y }}</h2></div>
    <div class="table-scroll" style="margin-bottom: 18px">
      <table class="year-table">
        <thead>
          <tr>
            <th>{{ t("th_month") }}</th><th class="num">{{ t("g_inc") }}</th><th class="num">{{ t("g_pay") }}</th><th class="num">{{ t("g_exp") }}</th>
            <th class="num">{{ t("g_debt") }}</th><th class="num">{{ t("th_net") }}</th><th class="num">{{ t("th_savings") }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in rows" :key="r.m" :class="{ cur: monthKey(period.y, r.m) === thisMonth }">
            <td class="cat">{{ months()[r.m] }}</td>
            <td v-for="k in (['inc', 'pay', 'exp', 'debt'] as const)" :key="k" class="num">
              <template v-if="r.totals[k]">{{ sum(r.totals[k]) }}</template><span v-else class="dash">—</span>
            </td>
            <td class="num" :class="r.totals.net < 0 ? 'neg' : r.totals.net > 0 ? 'pos' : ''">{{ r.totals.net ? signedSum(r.totals.net) : "—" }}</td>
            <td class="num" :class="{ neg: r.end < 0 }">{{ signedSum(r.end) }}</td>
          </tr>
        </tbody>
        <tfoot>
          <tr>
            <td>{{ t("total") }}</td><td class="num">{{ sum(total.inc) }}</td><td class="num">{{ sum(total.pay) }}</td><td class="num">{{ sum(total.exp) }}</td>
            <td class="num">{{ sum(total.debt) }}</td><td class="num">{{ signedSum(total.net) }}</td><td class="num">{{ signedSum(endBalance) }}</td>
          </tr>
        </tfoot>
      </table>
    </div>

    <div class="grid2">
      <div class="panel">
        <h2><span>{{ t("y_exp_cats") }}</span><small>{{ expTotal ? t("total") + ": " + sum(expTotal) : "" }}</small></h2>
        <CategoryBars :list="yearList" :usd-rate="usdRate" :income="false" :empty="t('no_out')" />
      </div>
      <div class="panel">
        <h2><span>{{ t("y_inc_cats") }}</span><small>{{ total.inc ? t("total") + ": " + sum(total.inc) : "" }}</small></h2>
        <CategoryBars :list="yearList" :usd-rate="usdRate" :income="true" :empty="t('no_inc')" />
      </div>
    </div>
  </section>
</template>
