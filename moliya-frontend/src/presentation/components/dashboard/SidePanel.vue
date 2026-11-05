<script setup lang="ts">
// Bosh sahifada: yaqin qarz to'lovlari. Daromad/chiqim bo'limlarida: toifalar bo'yicha taqsimot.
import { computed } from "vue"
import { byCategory, upcomingDebts } from "@/domain/ledger"
import { fmtDate, initials, num } from "@/domain/money"
import { useMonth } from "@/application/ledger/useMonth"
import { useI18n } from "@/presentation/i18n"
import CategoryBars from "./CategoryBars.vue"

const props = defineProps<{ mode: "dash" | "income" | "expense" }>()
const { state, usdRate, list, today } = useMonth()
const { t, kcompact, sum } = useI18n()

const debts = computed(() => upcomingDebts(state.value.debts, today))
const income = computed(() => props.mode === "income")
const catTotal = computed(() => byCategory(list.value, usdRate.value, income.value).reduce((s, r) => s + r.value, 0))
</script>

<template>
  <div class="dpanel">
    <template v-if="mode === 'dash'">
      <div class="panel-head">
        <h2>{{ t("side_debts") }}</h2>
        <RouterLink class="link-btn" to="/debts">{{ t("all_link") }}</RouterLink>
      </div>
      <p v-if="!debts.length" class="side-empty">{{ t("no_debts_side") }}</p>
      <div v-else class="side-list">
        <RouterLink v-for="o in debts" :key="o.debt.id" to="/debts" class="srow">
          <span class="ava">{{ initials(o.debt.lender || t("unnamed")) }}</span>
          <span class="sinfo">
            <span class="sname">{{ o.debt.lender || t("unnamed") }}</span>
            <span class="ssub">
              {{ o.calc.months ? o.calc.months + " " + t("mo_short") + " · " : "" }}{{
                o.debt.payDate || o.debt.deadline ? t("pay_word") + " " + fmtDate(o.debt.payDate || o.debt.deadline) : t("d_remaining") + " " + kcompact(o.calc.remaining)
              }}
            </span>
          </span>
          <span class="spill">{{ num(o.calc.monthly || o.calc.remaining) }}</span>
        </RouterLink>
      </div>
    </template>
    <template v-else>
      <div class="panel-head">
        <h2>{{ income ? t("inc_cat_title") : t("cat_title") }}</h2>
        <small>{{ catTotal ? t("total") + ": " + sum(catTotal) : "" }}</small>
      </div>
      <CategoryBars :list="list" :usd-rate="usdRate" :income="income" :empty="income ? t('no_inc') : t('no_out')" />
    </template>
  </div>
</template>
