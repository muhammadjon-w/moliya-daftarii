<script setup lang="ts">
// Qarzga to'lov: summa (oylik to'lov bilan to'ldirilgan), sana, chiqimga yozish.
import { computed, ref } from "vue"
import { useI18n } from "@/composables/useI18n"
import { useTelegram } from "@/composables/useTelegram"
import { useUi } from "@/composables/useUi"
import BaseSheet from "@/components/BaseSheet.vue"
import MoneyInput from "@/components/MoneyInput.vue"
import { usePayDebt } from "@/rest/queries/ledger.mutations"
import type { Debt } from "@/types/ledger"
import { debtCalc } from "@/utils/ledger"
import { num, todayIso } from "@/utils/money"

const props = defineProps<{ debt: Debt }>()
const emit = defineEmits<{ close: [] }>()
const { t } = useI18n()
const { notify } = useUi()
const tg = useTelegram()
const pay = usePayDebt()

const calc = debtCalc(props.debt, todayIso())
const amount = ref(Math.round(calc.monthly || calc.remaining))
const date = ref(todayIso())
const logTransaction = ref(true)
const tried = ref(false)
const ok = computed(() => amount.value > 0)

function submit() {
  tried.value = true
  if (!ok.value) return
  pay.mutate(
    { id: props.debt.id, payment: { amount: amount.value, date: date.value || todayIso(), logTransaction: logTransaction.value } },
    {
      onSuccess: () => {
        notify(t("paid_ok"))
        tg.haptic("success")
        emit("close")
      },
    },
  )
}
</script>

<template>
  <BaseSheet :title="t('pay_title')" @close="emit('close')">
    <form id="pay-form" @submit.prevent="submit">
      <p class="who">
        <b>{{ debt.lender }}</b> · {{ t("remaining") }} <span class="num">{{ num(calc.remaining) }}</span>
      </p>
      <label class="field">
        <span class="field__label">{{ t("pay_amount") }}</span>
        <MoneyInput v-model="amount" class="input num" />
        <span v-if="tried && !ok" class="field-error">{{ t("err_amount") }}</span>
      </label>
      <label class="field">
        <span class="field__label">{{ t("date") }}</span>
        <input v-model="date" class="input" type="date" />
      </label>
      <label class="check">
        <input v-model="logTransaction" type="checkbox" />
        <span>{{ t("log_expense") }}</span>
      </label>
    </form>
    <template #footer>
      <button class="btn btn--primary btn--block" type="submit" form="pay-form" :disabled="pay.isPending.value">{{ t("pay") }}</button>
    </template>
  </BaseSheet>
</template>

<style scoped>
.who {
  color: var(--text-2);
  font-size: 17px;
}

.who b {
  color: var(--text);
}

.check {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 20px;
  font-size: 17px;
}

.check input {
  width: 22px;
  height: 22px;
  accent-color: var(--teal);
}
</style>
