<script setup lang="ts">
// Tushum (o'tgan oyga nisbatan) va Chiqim (tushumga nisbatan) kartochkalari.
import { computed } from "vue"
import { useI18n } from "@/composables/useI18n"
import { changePct, percent, type Totals } from "@/utils/ledger"
import { num } from "@/utils/money"

const props = defineProps<{ sums: Totals; prev: Totals }>()
const { t } = useI18n()

const change = computed(() => changePct(props.sums.inc, props.prev.inc))
const share = computed(() => percent(props.sums.out, props.sums.inc))
</script>

<template>
  <div class="kpis">
    <div class="card kpi">
      <span class="kpi__label">{{ t("income") }}</span>
      <b class="kpi__value kpi__value--green num">{{ num(sums.inc) }}</b>
      <span v-if="change !== null" class="kpi__note">{{ t("vs_prev", { p: (change > 0 ? "+" : change < 0 ? "−" : "") + Math.abs(change) + "%" }) }}</span>
    </div>
    <div class="card kpi">
      <span class="kpi__label">{{ t("expense") }}</span>
      <b class="kpi__value kpi__value--orange num">{{ num(sums.out) }}</b>
      <span v-if="share !== null" class="kpi__note">{{ t("of_income", { p: share }) }}</span>
    </div>
  </div>
</template>

<style scoped>
.kpis {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.kpi {
  display: grid;
  gap: 8px;
  padding: 20px 22px;
  border-radius: var(--r-lg);
}

.kpi__label {
  color: var(--text-2);
  font-size: 17px;
}

.kpi__value {
  font-size: clamp(22px, 7.6vw, 34px);
  font-weight: 600;
  line-height: 1.1;
}

.kpi__value--green {
  color: var(--green);
}

.kpi__value--orange {
  color: var(--orange);
}

.kpi__note {
  color: var(--text-2);
  font-size: 15px;
}
</style>
