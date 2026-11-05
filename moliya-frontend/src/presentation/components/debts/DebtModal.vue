<script setup lang="ts">
import { computed, ref } from "vue"
import { debtCalc } from "@/domain/ledger"
import { todayIso } from "@/domain/money"
import type { Debt, DebtStatus } from "@/domain/types"
import { useGateways } from "@/application/container"
import { saveDebtVars, useSaveDebt } from "@/application/ledger/mutations"
import { useUiStore } from "@/application/session/ui"
import { useI18n } from "@/presentation/i18n"
import ModalShell from "../common/ModalShell.vue"
import MoneyInput from "../common/MoneyInput.vue"

const props = defineProps<{ debt: Debt | null }>()
const emit = defineEmits<{ close: [] }>()
const ui = useUiStore()
const { platform } = useGateways()
const save = useSaveDebt()
const { t, sum } = useI18n()

const d = props.debt
const date = ref(d ? d.date ?? "" : todayIso())
const lender = ref(d?.lender ?? "")
const principal = ref(d ? d.principal : NaN)
const paid = ref(d ? d.paid : NaN)
const months = ref<number | "">(d?.months || "")
const status = ref<DebtStatus>(d?.status ?? "")
const payDate = ref(d?.payDate ?? "")
const deadline = ref(d?.deadline ?? "")
const note = ref(d?.note ?? "")
const tried = ref(false)
const STATUSES: DebtStatus[] = ["", "active", "paid", "overdue"]

const calc = computed(() => debtCalc({ principal: principal.value || 0, paid: paid.value || 0, months: Number(months.value) || 0 }, todayIso()))

function submit() {
  tried.value = true
  if (!(principal.value > 0)) return
  save.mutate(
    saveDebtVars(
      {
        date: date.value || null,
        lender: lender.value.trim(),
        principal: principal.value,
        paid: paid.value > 0 ? paid.value : 0,
        months: Math.max(0, Math.floor(Number(months.value) || 0)),
        status: status.value,
        payDate: payDate.value || null,
        deadline: deadline.value || null,
        note: note.value.trim(),
      },
      d?.id,
    ),
    { onSuccess: () => (ui.notify(t("saved")), platform.haptic("success")) },
  )
  emit("close")
}
</script>

<template>
  <ModalShell :title="t(debt ? 'edit_debt' : 'new_debt')" autofocus="#dLender" @close="emit('close')" @submit="submit">
    <div class="row2">
      <label><span>{{ t("d_date") }}</span><input v-model="date" type="date" /></label>
      <label><span>{{ t("d_lender") }}</span><input id="dLender" v-model="lender" autocomplete="off" /></label>
    </div>
    <div class="row2">
      <label><span>{{ t("d_principal") }}</span><MoneyInput v-model="principal" /></label>
      <label><span>{{ t("d_paid") }}</span><MoneyInput v-model="paid" /></label>
    </div>
    <div v-if="tried && !(principal > 0)" class="field-error">{{ t("err_debt") }}</div>
    <div class="row2">
      <label><span>{{ t("d_months") }}</span><input v-model="months" type="number" min="0" step="1" inputmode="numeric" /></label>
      <label>
        <span>{{ t("d_status") }}</span>
        <select v-model="status"><option v-for="s in STATUSES" :key="s" :value="s">{{ t(s ? "st_" + s : "st_auto") }}</option></select>
      </label>
    </div>
    <p class="auto-note">
      {{ t("d_remaining") }}: <b>{{ sum(calc.remaining) }}</b><template v-if="calc.months"> · {{ t("d_monthly") }}: <b>{{ sum(calc.monthly) }}</b></template>
    </p>
    <div class="row2">
      <label><span>{{ t("d_paydate") }}</span><input v-model="payDate" type="date" /></label>
      <label><span>{{ t("d_deadline") }}</span><input v-model="deadline" type="date" /></label>
    </div>
    <label><span>{{ t("f_note") }}</span><textarea v-model="note" rows="2"></textarea></label>
    <div class="modal-actions">
      <button class="btn-ghost" type="button" @click="emit('close')">{{ t("cancel") }}</button>
      <button class="btn-primary" type="submit">{{ t("save") }}</button>
    </div>
  </ModalShell>
</template>
