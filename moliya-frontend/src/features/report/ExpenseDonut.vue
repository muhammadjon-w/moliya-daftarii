<script setup lang="ts">
// Chiqim tarkibi (To'lovlar / Xarajatlar / Qarz to'lovi) va markazda sof qoldiq.
import { computed } from "vue"
import { useI18n } from "@/composables/useI18n"
import DonutChart from "@/components/DonutChart.vue"
import { GROUP_TONE } from "@/constants/categoryStyle"
import { expenseShares, type Totals } from "@/utils/ledger"

const props = defineProps<{ sums: Totals }>()
const { t, groupLabel, compact } = useI18n()

const shares = computed(() => expenseShares(props.sums))
const parts = computed(() => shares.value.map((s) => ({ value: s.value, tone: GROUP_TONE[s.group], label: `${groupLabel(s.group)} ${s.pct}%` })))
</script>

<template>
  <section class="card donut-card">
    <DonutChart :parts="parts" :size="190">
      <span class="dc__label">{{ t("net") }}</span>
      <b class="dc__value num" :class="sums.net >= 0 ? 'dc__value--pos' : 'negative'">{{ sums.net >= 0 ? "+" : "" }}{{ compact(sums.net) }}</b>
    </DonutChart>
    <ul v-if="shares.length" class="legend">
      <li v-for="s in shares" :key="s.group">
        <i :style="{ background: `rgb(var(--tone-${GROUP_TONE[s.group]}))` }"></i>
        <span>{{ groupLabel(s.group) }}</span>
        <b class="num">{{ s.pct }}%</b>
      </li>
    </ul>
    <p v-else class="legend muted">{{ t("no_expense") }}</p>
  </section>
</template>

<style scoped>
.donut-card {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-top: 16px;
  padding: 24px 22px;
}

.dc__label {
  color: var(--text-2);
  font-size: 15px;
}

.dc__value {
  font-size: 24px;
  font-weight: 600;
}

.dc__value--pos {
  color: var(--green);
}

.legend {
  flex: 1;
  display: grid;
  gap: 16px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.legend li {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 18px;
}

.legend i {
  flex: none;
  width: 16px;
  height: 16px;
  border-radius: 5px;
}

.legend span {
  flex: 1;
}

.legend b {
  font-weight: 600;
}

@media (max-width: 400px) {
  .donut-card {
    flex-direction: column;
  }

  .legend {
    width: 100%;
  }
}
</style>
