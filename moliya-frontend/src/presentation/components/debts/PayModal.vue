<script setup lang="ts">
import { ref } from "vue"
import { debtCalc } from "@/domain/ledger"
import { todayIso } from "@/domain/money"
import type { Debt } from "@/domain/types"
import { useGateways } from "@/application/container"
import { usePayDebt } from "@/application/ledger/mutations"
import { useUiStore } from "@/application/session/ui"
import { useI18n } from "@/presentation/i18n"
import ModalShell from "../common/ModalShell.vue"
import MoneyInput from "../common/MoneyInput.vue"

const props = defineProps<{ debt: Debt }>()
const emit = defineEmits<{ close: [] }>()
const ui = useUiStore()
const { platform } = useGateways()
const pay = usePayDebt()
const { t, sum } = useI18n()

const calc = debtCalc(props.debt, todayIso())
const amount = ref(calc.monthly ? Math.round(Math.min(calc.monthly, calc.remaining)) : NaN)
const date = ref(todayIso())
const log = ref(true)
const tried = ref(false)

function submit() {
  tried.value = true
  if (!(amount.value > 0)) return
  pay.mutate(
    { id: props.debt.id, payment: { amount: amount.value, date: date.value || todayIso(), logTransaction: log.value } },
    {
      onSuccess: () => {
        ui.notify(t("saved"))
        platform.haptic("success")
        emit("close")
      },
    },
  )
}
</script>

<template>
  <ModalShell :title="t('pay_title')" autofocus=".money" @close="emit('close')" @submit="submit">
    <p class="auto-note" style="margin-top: 0">{{ debt.lender || t("unnamed") }} · {{ t("pay_info") }}: <b>{{ sum(calc.remaining) }}</b></p>
    <div class="row2">
      <label><span>{{ t("f_amount") }}</span><MoneyInput v-model="amount" /></label>
      <label><span>{{ t("f_date") }}</span><input v-model="date" type="date" /></label>
    </div>
    <div v-if="tried && !(amount > 0)" class="field-error">{{ t("err_amount") }}</div>
    <label class="check-row"><input v-model="log" type="checkbox" /><span>{{ t("pay_log") }}</span></label>
    <div class="modal-actions">
      <button class="btn-ghost" type="button" @click="emit('close')">{{ t("cancel") }}</button>
      <button class="btn-primary" type="submit" :disabled="pay.isPending.value">{{ t("save") }}</button>
    </div>
  </ModalShell>
</template>
