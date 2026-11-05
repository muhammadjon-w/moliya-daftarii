<script setup lang="ts">
import { computed, ref } from "vue"
import { debtCalc, debtSummary } from "@/domain/ledger"
import { fmtDate } from "@/domain/money"
import type { Debt } from "@/domain/types"
import { useDeleteDebt } from "@/application/ledger/mutations"
import { useMonth } from "@/application/ledger/useMonth"
import { useUiStore } from "@/application/session/ui"
import { useI18n } from "@/presentation/i18n"
import ConfirmModal from "../components/common/ConfirmModal.vue"
import DebtModal from "../components/debts/DebtModal.vue"
import PayModal from "../components/debts/PayModal.vue"

const ui = useUiStore()
const { state, today } = useMonth()
const remove = useDeleteDebt()
const { t, sum } = useI18n()

const editing = ref<{ debt: Debt | null } | null>(null)
const paying = ref<Debt | null>(null)
const deleting = ref<Debt | null>(null)

const rows = computed(() =>
  [...state.value.debts]
    .sort((a, b) => String(a.date || "9999").localeCompare(String(b.date || "9999")))
    .map((debt) => ({ debt, c: debtCalc(debt, today) })),
)
const s = computed(() => debtSummary(state.value.debts, today))
const pending = (d: Debt) => d.id.startsWith("tmp-")

function confirmDelete() {
  const d = deleting.value
  deleting.value = null
  if (d) remove.mutate(d.id, { onSuccess: () => ui.notify(t("deleted")) })
}
</script>

<template>
  <section>
    <div class="debt-stats">
      <div class="stat"><div class="val">{{ sum(s.principal) }}</div><div class="lbl">{{ t("ds_total") }}</div></div>
      <div class="stat"><div class="val" style="color: var(--green-dark)">{{ sum(s.paid) }}</div><div class="lbl">{{ t("ds_paid") }}</div></div>
      <div class="stat"><div class="val" :style="s.remaining ? 'color: var(--brick)' : undefined">{{ sum(s.remaining) }}</div><div class="lbl">{{ t("ds_left") }}</div></div>
      <div class="stat"><div class="val" style="color: var(--amber)">{{ sum(s.monthly) }}</div><div class="lbl">{{ t("ds_monthly") }}</div></div>
    </div>
    <div class="toolbar">
      <h2>{{ t("debts_title") }}</h2>
      <div class="tool-actions"><button class="btn-primary" type="button" @click="editing = { debt: null }">{{ t("add_debt") }}</button></div>
    </div>

    <div v-if="!rows.length" class="empty-state"><p>{{ t("debts_empty") }}</p></div>
    <div v-else class="table-scroll">
      <table class="debt-table">
        <thead>
          <tr>
            <th>#</th><th>{{ t("d_date") }}</th><th>{{ t("d_lender") }}</th><th class="num">{{ t("d_principal") }}</th><th class="num">{{ t("d_paid") }}</th>
            <th class="num">{{ t("d_remaining") }}</th><th class="num">{{ t("d_months") }}</th><th class="num">{{ t("d_monthly") }}</th>
            <th>{{ t("d_paydate") }}</th><th>{{ t("d_deadline") }}</th><th>{{ t("d_status") }}</th><th>{{ t("f_note") }}</th><th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="({ debt, c }, i) in rows" :key="debt.id" :class="{ pending: pending(debt) }">
            <td class="date">{{ i + 1 }}</td>
            <td class="date">{{ fmtDate(debt.date) }}</td>
            <td class="cat">{{ debt.lender || t("unnamed") }}</td>
            <td class="num">{{ sum(c.principal) }}</td>
            <td class="num inc">
              {{ sum(c.paid) }}
              <div class="mini-prog"><i :style="{ width: Math.min(c.principal ? (c.paid / c.principal) * 100 : 0, 100).toFixed(1) + '%' }"></i></div>
            </td>
            <td class="num" :class="{ exp: c.remaining }">{{ sum(c.remaining) }}</td>
            <td class="num" style="font-weight: 500">{{ c.months || "—" }}</td>
            <td class="num">{{ c.monthly ? sum(c.monthly) : "—" }}</td>
            <td class="date">{{ fmtDate(debt.payDate) }}</td>
            <td class="date">{{ fmtDate(debt.deadline) }}</td>
            <td><span class="badge" :class="c.status">{{ t("st_" + c.status) }}</span></td>
            <td class="note">{{ debt.note }}</td>
            <td class="row-actions">
              <template v-if="!pending(debt)">
                <button v-if="c.remaining > 0" class="btn-link" type="button" @click="paying = debt">{{ t("pay_btn") }}</button>
                <button class="btn-link" type="button" @click="editing = { debt }">{{ t("edit") }}</button>
                <button class="btn-link danger" type="button" @click="deleting = debt">{{ t("delete") }}</button>
              </template>
            </td>
          </tr>
        </tbody>
        <tfoot>
          <tr>
            <td colspan="3">{{ t("total") }}</td><td class="num">{{ sum(s.principal) }}</td><td class="num">{{ sum(s.paid) }}</td>
            <td class="num">{{ sum(s.remaining) }}</td><td></td><td class="num">{{ sum(s.monthly) }}</td><td colspan="5"></td>
          </tr>
        </tfoot>
      </table>
    </div>

    <DebtModal v-if="editing" :debt="editing.debt" @close="editing = null" />
    <PayModal v-if="paying" :debt="paying" @close="paying = null" />
    <ConfirmModal v-if="deleting" :text="`${t('del_text')} ${deleting.lender || t('unnamed')} · ${sum(deleting.principal)}`" @close="deleting = null" @confirm="confirmDelete" />
  </section>
</template>
