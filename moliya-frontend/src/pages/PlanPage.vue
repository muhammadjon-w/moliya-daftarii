<script setup lang="ts">
import { computed } from "vue"
import { useRouter } from "vue-router"
import { useI18n } from "@/composables/useI18n"
import { useMonth } from "@/composables/useMonth"
import { useUi } from "@/composables/useUi"
import MonthSwitcher from "@/components/MonthSwitcher.vue"
import QueryState from "@/components/QueryState.vue"
import RoundButton from "@/components/RoundButton.vue"
import { ALL_GROUPS } from "@/constants/catalog"
import { ROUTES } from "@/constants/routes"
import PlanGroup from "@/features/plan/PlanGroup.vue"
import { useCopyPreviousPlan, useSavePlan } from "@/rest/queries/ledger.mutations"
import { planRows } from "@/utils/ledger"
import { monthKey, shiftMonth } from "@/utils/money"

const router = useRouter()
const { t } = useI18n()
const { notify } = useUi()
const { query, state, period, key, list, plan, usdRate } = useMonth()
const savePlan = useSavePlan()
const copyPlan = useCopyPreviousPlan()

const groups = computed(() => ALL_GROUPS.map((g) => ({ group: g, rows: planRows(list.value, plan.value, usdRate.value, g) })))

function setPlan(planKey: string, v: number) {
  const values = { ...plan.value }
  if (v > 0) values[planKey] = v
  else delete values[planKey]
  if ((plan.value[planKey] ?? 0) === (values[planKey] ?? 0)) return
  savePlan.mutate({ month: key.value, values })
}

function copyPrevious() {
  const p = shiftMonth(period.value.y, period.value.m, -1)
  if (!Object.keys(state.value.plans[monthKey(p.y, p.m)] ?? {}).length) return notify(t("plan_none"))
  copyPlan.mutate(key.value, { onSuccess: () => notify(t("plan_copied")) })
}
</script>

<template>
  <main class="page">
    <header class="ph">
      <RoundButton icon="chevronLeft" :label="t('back')" @click="router.push({ name: ROUTES.home })" />
      <MonthSwitcher />
    </header>
    <h1 class="ph__title">{{ t("plan_title") }}</h1>
    <p class="muted">{{ t("plan_hint") }}</p>
    <button class="btn btn--ghost ph__copy" type="button" :disabled="copyPlan.isPending.value" @click="copyPrevious">{{ t("copy_prev") }}</button>
    <QueryState :pending="query.isPending.value" :error="query.error.value" :has-data="!!query.data.value" @retry="query.refetch()">
      <PlanGroup v-for="g in groups" :key="g.group" :group="g.group" :rows="g.rows" @change="setPlan" />
    </QueryState>
  </main>
</template>

<style scoped>
.ph {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
}

.ph :deep(.ms) {
  flex: 1;
}

.ph__title {
  margin-bottom: 6px;
  font-size: 30px;
  font-weight: 600;
}

.ph__copy {
  margin-top: 16px;
  min-height: 46px;
  font-size: 16px;
}
</style>
