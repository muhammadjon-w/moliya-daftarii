<script setup lang="ts">
import { computed } from "vue"
import { yearRows } from "@/domain/ledger"
import { useMonth } from "@/application/ledger/useMonth"
import { useUiStore } from "@/application/session/ui"
import { useI18n } from "@/presentation/i18n"

const ui = useUiStore()
const { state, usdRate, period, opening } = useMonth()
const { t, months, sum } = useI18n()

const rows = computed(() => yearRows(state.value.transactions, period.value.y, usdRate.value, opening.value))
const max = computed(() => Math.max(1, ...rows.value.map((r) => Math.max(r.totals.inc, r.totals.out))))
const bars = computed(() =>
  rows.value.map((r) => {
    const { inc, out } = r.totals
    const empty = !inc && !out
    return {
      m: r.m,
      hi: empty ? 7 : Math.max((inc / max.value) * 100, 4),
      ho: empty ? 0 : out ? Math.max((out / max.value) * 100, 3) : 0,
      over: out > inc && out > 0,
      tip: `${months()[r.m]} ${period.value.y}: ${t("g_inc")} ${sum(inc)}, ${t("l_out")} ${sum(out)}`,
    }
  }),
)
</script>

<template>
  <div class="dpanel">
    <div class="panel-head">
      <h2>{{ t("months_title") }} · {{ period.y }}</h2>
      <RouterLink class="link-btn" to="/year">{{ t("report_link") }}</RouterLink>
    </div>
    <div class="mbars">
      <button
        v-for="b in bars"
        :key="b.m"
        type="button"
        class="mcol"
        :class="{ cur: b.m === period.m, over: b.over }"
        :title="b.tip"
        :aria-label="b.tip"
        @click="ui.setPeriod({ y: period.y, m: b.m })"
      >
        <span class="mplot"><span class="mtrack" :style="{ height: b.hi.toFixed(1) + '%' }"></span><span class="mfill" :style="{ height: b.ho.toFixed(1) + '%' }"></span></span>
        <span class="mlbl">{{ months()[b.m].slice(0, 3) }}</span>
      </button>
    </div>
    <p class="legend-note">{{ t("mbars_note") }}</p>
  </div>
</template>
