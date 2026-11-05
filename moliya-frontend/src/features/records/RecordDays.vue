<script setup lang="ts">
// Yozuvlar kunlar bo'yicha guruhlangan; har kun sarlavhasida o'sha kunning sof natijasi.
import { computed } from "vue"
import { useI18n } from "@/composables/useI18n"
import { useSheets } from "@/composables/useSheets"
import TransactionRow from "@/components/TransactionRow.vue"
import type { Transaction } from "@/types/ledger"
import { toUzs } from "@/utils/ledger"
import { fmtDate } from "@/utils/money"

const props = defineProps<{ items: Transaction[]; usdRate: number }>()
const sheets = useSheets()
const { t, signedAmount } = useI18n()

const days = computed(() => {
  const map = new Map<string, Transaction[]>()
  for (const tx of props.items) map.set(tx.date, [...(map.get(tx.date) ?? []), tx])
  return [...map.entries()].map(([date, list]) => ({
    date,
    list,
    net: list.reduce((s, x) => s + (x.type === "income" ? 1 : -1) * toUzs(x, props.usdRate), 0),
  }))
})
</script>

<template>
  <div v-if="days.length">
    <section v-for="d in days" :key="d.date" class="day">
      <h3 class="day__head">
        <span>{{ fmtDate(d.date) }}</span>
        <span class="num" :class="d.net >= 0 ? 'positive' : 'muted'">{{ signedAmount(d.net, d.net >= 0) }}</span>
      </h3>
      <div class="card">
        <TransactionRow v-for="tx in d.list" :key="tx.id" :tx="tx" @open="sheets.editRecord" />
      </div>
    </section>
  </div>
  <p v-else class="card empty">{{ t("empty_month") }}</p>
</template>

<style scoped>
.day + .day {
  margin-top: 18px;
}

.day__head {
  display: flex;
  justify-content: space-between;
  margin: 0 6px 10px;
  color: var(--text-2);
  font-size: 15px;
  font-weight: 500;
}

.empty {
  padding: 28px 22px;
  color: var(--text-2);
  text-align: center;
}
</style>
