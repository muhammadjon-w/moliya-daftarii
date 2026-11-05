<script setup lang="ts">
// Yangi qarz / tahrirlash.
import { computed, ref } from "vue"
import { useI18n } from "@/composables/useI18n"
import { useTelegram } from "@/composables/useTelegram"
import { useUi } from "@/composables/useUi"
import AppIcon from "@/components/AppIcon.vue"
import BaseSheet from "@/components/BaseSheet.vue"
import MoneyInput from "@/components/MoneyInput.vue"
import { saveDebtVars, useDeleteDebt, useSaveDebt } from "@/rest/queries/ledger.mutations"
import type { Debt } from "@/types/ledger"
import { debtCalc } from "@/utils/ledger"
import { num, todayIso } from "@/utils/money"

const props = defineProps<{ debt?: Debt }>()
const emit = defineEmits<{ close: [] }>()
const { t } = useI18n()
const { notify } = useUi()
const tg = useTelegram()
const save = useSaveDebt()
const remove = useDeleteDebt()

const d = props.debt
const lender = ref(d?.lender ?? "")
const principal = ref(d ? d.principal : NaN)
const paid = ref(d ? d.paid : NaN)
const months = ref<number | "">(d?.months || "")
const payDate = ref(d?.payDate ?? "")
const note = ref(d?.note ?? "")
const tried = ref(false)

const calc = computed(() => debtCalc({ principal: principal.value || 0, paid: paid.value || 0, months: Number(months.value) || 0 }, todayIso()))
const lenderOk = computed(() => lender.value.trim().length > 0)
const principalOk = computed(() => principal.value > 0)

function submit() {
  tried.value = true
  if (!lenderOk.value || !principalOk.value) return
  save.mutate(
    saveDebtVars(
      {
        lender: lender.value.trim(),
        principal: principal.value,
        paid: paid.value > 0 ? paid.value : 0,
        months: Math.max(0, Math.floor(Number(months.value) || 0)),
        // Yangi qarzda holat bo'sh: server qoldiq va muddatdan o'zi hisoblaydi
        status: d?.status ?? "",
        date: d?.date ?? todayIso(),
        payDate: payDate.value || null,
        deadline: d?.deadline ?? null,
        note: note.value.trim(),
      },
      d?.id,
    ),
    { onSuccess: () => (notify(t("saved")), tg.haptic("success")) },
  )
  emit("close")
}

async function destroy() {
  if (!d || !(await tg.confirm(t("confirm_delete")))) return
  remove.mutate(d.id, { onSuccess: () => notify(t("deleted")) })
  emit("close")
}
</script>

<template>
  <BaseSheet :title="t(debt ? 'edit_debt' : 'new_debt')" autofocus="#debt-lender" @close="emit('close')">
    <form id="debt-form" @submit.prevent="submit">
      <label class="field">
        <span class="field__label">{{ t("lender") }}</span>
        <input id="debt-lender" v-model="lender" class="input" maxlength="200" autocomplete="off" :placeholder="t('lender_ph')" />
        <span v-if="tried && !lenderOk" class="field-error">{{ t("err_lender") }}</span>
      </label>
      <div class="row-2">
        <label class="field">
          <span class="field__label">{{ t("principal") }}</span>
          <MoneyInput v-model="principal" class="input num" />
        </label>
        <label class="field">
          <span class="field__label">{{ t("paid_already") }}</span>
          <MoneyInput v-model="paid" class="input num" />
        </label>
      </div>
      <p v-if="tried && !principalOk" class="field-error">{{ t("err_principal") }}</p>
      <div class="row-2">
        <label class="field">
          <span class="field__label">{{ t("term_months") }}</span>
          <input v-model="months" class="input num" type="number" min="0" max="600" step="1" inputmode="numeric" placeholder="12" />
        </label>
        <label class="field">
          <span class="field__label">{{ t("pay_date") }}</span>
          <input v-model="payDate" class="input" type="date" />
        </label>
      </div>
      <p class="calc num">
        {{ t("remaining") }}: <b>{{ num(calc.remaining) }}</b>
        <template v-if="calc.months"> · {{ t("monthly_pay") }}: <b>{{ num(calc.monthly) }}</b></template>
      </p>
      <label class="field">
        <span class="field__label">{{ t("note") }}</span>
        <input v-model="note" class="input" maxlength="1000" />
      </label>
    </form>
    <template #footer>
      <button v-if="debt" class="btn btn--danger" type="button" :aria-label="t('delete')" @click="destroy"><AppIcon name="trash" /></button>
      <button class="btn btn--primary btn--block" type="submit" form="debt-form">{{ t("save") }}</button>
    </template>
  </BaseSheet>
</template>

<style scoped>
.calc {
  margin-top: 14px;
  padding: 14px 16px;
  border-radius: var(--r-md);
  background: var(--surface);
  color: var(--text-2);
}

.calc b {
  color: var(--text);
}
</style>
