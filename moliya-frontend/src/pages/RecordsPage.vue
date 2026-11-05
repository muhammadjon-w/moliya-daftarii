<script setup lang="ts">
import { computed, ref } from "vue"
import { useI18n } from "@/composables/useI18n"
import { useMonth } from "@/composables/useMonth"
import MonthSwitcher from "@/components/MonthSwitcher.vue"
import QueryState from "@/components/QueryState.vue"
import SegmentedControl from "@/components/SegmentedControl.vue"
import RecordDays from "@/features/records/RecordDays.vue"
import type { TxType } from "@/types/ledger"

type Filter = "all" | TxType
const { query, list, sums, usdRate } = useMonth()
const { t, compact } = useI18n()
const filter = ref<Filter>("all")

const options = computed(() => [
  { value: "all" as const, label: t("filter_all") },
  { value: "income" as const, label: t("income") },
  { value: "expense" as const, label: t("expense") },
])
const shown = computed(() => (filter.value === "all" ? list.value : list.value.filter((x) => x.type === filter.value)))
</script>

<template>
  <main class="page">
    <header class="rp__head">
      <h1>{{ t("nav_records") }}</h1>
      <MonthSwitcher />
    </header>
    <SegmentedControl v-model="filter" :options="options" :label="t('nav_records')" />
    <p class="rp__sums num">
      <span class="positive">+{{ compact(sums.inc) }}</span>
      <span class="negative">−{{ compact(sums.out) }}</span>
    </p>
    <QueryState :pending="query.isPending.value" :error="query.error.value" :has-data="!!query.data.value" @retry="query.refetch()">
      <RecordDays :items="shown" :usd-rate="usdRate" />
    </QueryState>
  </main>
</template>

<style scoped>
.rp__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 18px;
}

.rp__head h1 {
  font-size: 30px;
  font-weight: 600;
}

.rp__head :deep(.ms__label) {
  min-width: 0;
  font-size: 18px;
}

.rp__sums {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin: 16px 0 20px;
  font-size: 18px;
  font-weight: 600;
}
</style>
