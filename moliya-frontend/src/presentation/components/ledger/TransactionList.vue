<script setup lang="ts">
import { computed, ref, watch } from "vue"
import { EXPENSE_GROUPS } from "@/domain/catalog"
import { groupOf, totals } from "@/domain/ledger"
import { fmtDate, num, usd } from "@/domain/money"
import type { Group, Transaction, TxType } from "@/domain/types"
import { useGateways } from "@/application/container"
import { useDeleteTransaction, useExportExcel } from "@/application/ledger/mutations"
import { useMonth } from "@/application/ledger/useMonth"
import { useUiStore } from "@/application/session/ui"
import { useI18n } from "@/presentation/i18n"
import ConfirmModal from "../common/ConfirmModal.vue"
import TransactionModal from "./TransactionModal.vue"

const props = defineProps<{ mode: "dash" | "income" | "expense" }>()
const ui = useUiStore()
const { platform } = useGateways()
const { state, usdRate, list, key } = useMonth()
const remove = useDeleteTransaction()
const exporter = useExportExcel()
const { t, itemLabel, catLabel, groupLabel, methodLabel, sum } = useI18n()

const search = ref("")
const groupFilter = ref<Group | "">("")
const catFilter = ref("")
const modal = ref<{ type: TxType; tx: Transaction | null } | null>(null)
const pendingDelete = ref<Transaction | null>(null)

watch(() => props.mode, () => {
  search.value = ""
  groupFilter.value = ""
  catFilter.value = ""
})

const groupOptions = computed<Group[]>(() => (props.mode === "income" ? [] : props.mode === "expense" ? [...EXPENSE_GROUPS] : ["inc", ...EXPENSE_GROUPS]))
const byMode = computed(() =>
  list.value.filter((x) => (props.mode === "income" ? x.type === "income" : props.mode === "expense" ? x.type !== "income" : true)),
)
const byGroup = computed(() => (groupFilter.value ? byMode.value.filter((x) => groupOf(x) === groupFilter.value) : byMode.value))
const categories = computed(() => [...new Set(byGroup.value.map((x) => x.category).filter(Boolean))])
const rows = computed(() => {
  let r = catFilter.value && categories.value.includes(catFilter.value) ? byGroup.value.filter((x) => x.category === catFilter.value) : byGroup.value
  const q = search.value.trim().toLowerCase()
  if (q) r = r.filter((x) => `${itemLabel(x.item)} ${catLabel(x.category)} ${x.note}`.toLowerCase().includes(q))
  return [...r].sort((a, b) => b.date.localeCompare(a.date) || String(b.createdAt ?? "").localeCompare(String(a.createdAt ?? "")))
})
const sums = computed(() => totals(rows.value, usdRate.value))
const title = computed(() => t(props.mode === "income" ? "list_income" : props.mode === "expense" ? "list_expense" : "list_all"))
const filtered = computed(() => !!(search.value || catFilter.value || groupFilter.value))

const amountText = (x: Transaction) => (x.currency === "USD" ? usd(x.amount) : num(x.amount) + " " + t("sum"))
const pending = (x: Transaction) => x.id.startsWith("tmp-")

function confirmDelete() {
  const tx = pendingDelete.value
  pendingDelete.value = null
  if (!tx) return
  remove.mutate(tx.id, { onSuccess: () => ui.notify(t("deleted")) })
}
function exportExcel() {
  exporter.mutate(key.value, {
    onSuccess: () => {
      ui.notify(t("export_sent"))
      platform.haptic("success")
    },
  })
}
</script>

<template>
  <section>
    <div class="toolbar">
      <h2>{{ title }}</h2>
      <div class="tool-actions">
        <button class="btn-primary" type="button" @click="modal = { type: 'income', tx: null }">{{ t("add_income") }}</button>
        <button class="btn-primary expense" type="button" @click="modal = { type: 'expense', tx: null }">{{ t("add_expense") }}</button>
        <button class="btn-ghost" type="button" :disabled="exporter.isPending.value" @click="exportExcel">{{ t("export_bot") }}</button>
      </div>
    </div>
    <div class="search-row">
      <input v-model="search" type="search" :placeholder="t('search_ph')" />
      <select v-if="groupOptions.length" v-model="groupFilter" :aria-label="t('all_groups')">
        <option value="">{{ t("all_groups") }}</option>
        <option v-for="g in groupOptions" :key="g" :value="g">{{ groupLabel(g) }}</option>
      </select>
      <select v-model="catFilter" :aria-label="t('all_cats')">
        <option value="">{{ t("all_cats") }}</option>
        <option v-for="c in categories" :key="c" :value="c">{{ catLabel(c) }}</option>
      </select>
    </div>

    <div v-if="!state.transactions.length" class="empty-state"><p>{{ t("empty_all") }}</p></div>
    <div v-else-if="!rows.length" class="empty-state"><p>{{ filtered ? t("no_match") : t("empty_month") }}</p></div>
    <div v-else class="table-scroll">
      <table>
        <thead>
          <tr>
            <th>{{ t("th_date") }}</th><th>{{ t("th_type") }}</th><th>{{ t("th_item") }}</th><th>{{ t("th_note") }}</th>
            <th>{{ t("th_method") }}</th><th class="num">{{ t("th_amount") }}</th><th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="x in rows" :key="x.id" :class="{ pending: pending(x) }">
            <td class="date">{{ fmtDate(x.date) }}</td>
            <td><span class="badge" :class="groupOf(x)">{{ t("b_" + groupOf(x)) }}</span></td>
            <td class="cat item">
              {{ itemLabel(x.item || x.category) }}
              <span v-if="catLabel(x.category) !== itemLabel(x.item || x.category)" class="sub">{{ catLabel(x.category) }}</span>
            </td>
            <td class="note">{{ x.note }}</td>
            <td><span class="badge plain">{{ methodLabel(x.method) }}</span></td>
            <td class="num" :class="x.type === 'income' ? 'inc' : 'exp'">{{ x.type === "income" ? "+" : "−" }} {{ amountText(x) }}</td>
            <td class="row-actions">
              <template v-if="!pending(x)">
                <button class="btn-link" type="button" @click="modal = { type: x.type, tx: x }">{{ t("edit") }}</button>
                <button class="btn-link danger" type="button" @click="pendingDelete = x">{{ t("delete") }}</button>
              </template>
            </td>
          </tr>
        </tbody>
        <tfoot>
          <tr>
            <td colspan="5">{{ t("total") }} · {{ rows.length }} {{ t("records") }}</td>
            <td class="num" colspan="2" style="text-align: right">
              <template v-if="mode === 'income'">{{ sum(sums.inc) }}</template>
              <template v-else-if="mode === 'expense'">{{ sum(sums.out) }}</template>
              <span v-else :style="{ color: sums.net < 0 ? 'var(--brick)' : 'var(--green-dark)' }">{{ sums.net < 0 ? "−" : "+" }} {{ sum(Math.abs(sums.net)) }}</span>
            </td>
          </tr>
        </tfoot>
      </table>
    </div>

    <TransactionModal v-if="modal" :type="modal.type" :tx="modal.tx" @close="modal = null" />
    <ConfirmModal
      v-if="pendingDelete"
      :text="`${t('del_text')} ${fmtDate(pendingDelete.date)} · ${itemLabel(pendingDelete.item || pendingDelete.category)} · ${amountText(pendingDelete)}`"
      @close="pendingDelete = null"
      @confirm="confirmDelete"
    />
  </section>
</template>
