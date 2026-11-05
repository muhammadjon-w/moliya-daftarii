<script setup lang="ts">
import { computed } from "vue"
import { yearRows } from "@/domain/ledger"
import { useMonth } from "@/application/ledger/useMonth"
import { useI18n } from "@/presentation/i18n"

const { state, usdRate, period, opening } = useMonth()
const { t, kcompact } = useI18n()
const year = computed(() =>
  yearRows(state.value.transactions, period.value.y, usdRate.value, opening.value).reduce((s, r) => ({ inc: s.inc + r.totals.inc, out: s.out + r.totals.out }), { inc: 0, out: 0 }),
)
</script>

<template>
  <div class="band year-banner">
    <div class="yb-icon" aria-hidden="true">
      <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18" /><path d="M7 15l4-4 3 3 5-6" /></svg>
    </div>
    <div class="yb-text"><h2>{{ t("yb_title") }}</h2><p>{{ t("yb_sub") }}</p></div>
    <div class="yb-chips">
      <div class="yb-chip"><span>{{ t("yb_inc") }}</span><b>{{ kcompact(year.inc) }}</b></div>
      <div class="yb-chip"><span>{{ t("yb_out") }}</span><b>{{ kcompact(year.out) }}</b></div>
      <div class="yb-chip"><span>{{ t("yb_saved") }}</span><b>{{ year.inc > 0 ? Math.round((1 - year.out / year.inc) * 100) + "%" : "—" }}</b></div>
    </div>
    <RouterLink class="btn-yellow" to="/year">{{ t("yb_open") }}</RouterLink>
  </div>
</template>
