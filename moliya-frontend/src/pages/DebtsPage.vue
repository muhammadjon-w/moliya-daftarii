<script setup lang="ts">
import { computed } from "vue"
import { useI18n } from "@/composables/useI18n"
import { useSheets } from "@/composables/useSheets"
import AppIcon from "@/components/AppIcon.vue"
import QueryState from "@/components/QueryState.vue"
import DebtCard from "@/features/debts/DebtCard.vue"
import DebtSummaryCard from "@/features/debts/DebtSummaryCard.vue"
import { useLedgerQuery } from "@/rest/queries/ledger.queries"
import { debtSummary, splitDebts } from "@/utils/ledger"
import { todayIso } from "@/utils/money"

const { query, state } = useLedgerQuery()
const sheets = useSheets()
const { t } = useI18n()
const today = todayIso()

const summary = computed(() => debtSummary(state.value.debts, today))
const groups = computed(() => splitDebts(state.value.debts, today))
</script>

<template>
  <main class="page">
    <header class="dh">
      <h1>{{ t("debts_title") }}</h1>
      <button class="dh__add" type="button" @click="sheets.newDebt()"><AppIcon name="plus" :size="22" :stroke="2.4" />{{ t("add") }}</button>
    </header>
    <QueryState :pending="query.isPending.value" :error="query.error.value" :has-data="!!query.data.value" @retry="query.refetch()">
      <DebtSummaryCard :summary="summary" />

      <h2 class="section-title">{{ t("upcoming") }}</h2>
      <DebtCard
        v-for="(v, i) in groups.open"
        :key="v.debt.id"
        :view="v"
        :index="i"
        @open="sheets.editDebt(v.debt)"
        @pay="sheets.payDebt(v.debt)"
      />
      <p v-if="!groups.open.length" class="card dh__empty">{{ t("empty_debts") }}</p>

      <template v-if="groups.closed.length">
        <h2 class="section-title">{{ t("closed_debts") }}</h2>
        <DebtCard v-for="(v, i) in groups.closed" :key="v.debt.id" :view="v" :index="i" class="dh__closed" @open="sheets.editDebt(v.debt)" />
      </template>
    </QueryState>
  </main>
</template>

<style scoped>
.dh {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 22px;
}

.dh h1 {
  font-size: 36px;
  font-weight: 600;
}

.dh__add {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  height: 58px;
  padding: 0 24px;
  border-radius: var(--r-pill);
  background: var(--teal);
  color: var(--teal-ink);
  font-size: 19px;
  font-weight: 600;
}

.dh__empty {
  padding: 28px 22px;
  color: var(--text-2);
  text-align: center;
}

.dh__closed {
  opacity: 0.6;
}
</style>
