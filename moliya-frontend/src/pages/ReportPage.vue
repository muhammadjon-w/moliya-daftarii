<script setup lang="ts">
import { computed } from "vue"
import { useRouter } from "vue-router"
import { useI18n } from "@/composables/useI18n"
import { useMonth } from "@/composables/useMonth"
import { useTelegram } from "@/composables/useTelegram"
import { useUi } from "@/composables/useUi"
import MonthSwitcher from "@/components/MonthSwitcher.vue"
import QueryState from "@/components/QueryState.vue"
import RoundButton from "@/components/RoundButton.vue"
import { ROUTES } from "@/constants/routes"
import ExpenseDonut from "@/features/report/ExpenseDonut.vue"
import PlanProgress from "@/features/report/PlanProgress.vue"
import ReportKpis from "@/features/report/ReportKpis.vue"
import TopSpending from "@/features/report/TopSpending.vue"
import { useExportExcel } from "@/rest/queries/ledger.mutations"
import { plannedRows, topItems } from "@/utils/ledger"

const router = useRouter()
const { t } = useI18n()
const { notify } = useUi()
const tg = useTelegram()
const { query, key, list, sums, prevSums, plan, usdRate } = useMonth()
const exportExcel = useExportExcel()

const top = computed(() => topItems(list.value, usdRate.value, false))
const planList = computed(() => plannedRows(list.value, plan.value, usdRate.value))

function download() {
  exportExcel.mutate(key.value, { onSuccess: () => (notify(t("export_sent")), tg.haptic("success")) })
}
</script>

<template>
  <main class="page">
    <header class="rh">
      <RoundButton icon="chevronLeft" :label="t('back')" @click="router.push({ name: ROUTES.home })" />
      <MonthSwitcher />
      <RoundButton icon="download" :label="t('export')" :disabled="exportExcel.isPending.value" @click="download" />
    </header>
    <QueryState :pending="query.isPending.value" :error="query.error.value" :has-data="!!query.data.value" @retry="query.refetch()">
      <ReportKpis :sums="sums" :prev="prevSums" />
      <ExpenseDonut :sums="sums" />
      <TopSpending :items="top" />
      <PlanProgress :rows="planList" />
    </QueryState>
  </main>
</template>

<style scoped>
.rh {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 22px;
}

.rh :deep(.ms__label) {
  min-width: 0;
}
</style>
