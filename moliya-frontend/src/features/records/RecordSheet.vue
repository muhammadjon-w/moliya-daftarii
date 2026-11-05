<script setup lang="ts">
// "Yangi yozuv" / tahrirlash: tur, summa, valyuta, toifa, sana, to'lov usuli, izoh.
import { computed, ref, watch } from "vue"
import { useI18n } from "@/composables/useI18n"
import { useTelegram } from "@/composables/useTelegram"
import { useUi } from "@/composables/useUi"
import AppIcon from "@/components/AppIcon.vue"
import BaseSheet from "@/components/BaseSheet.vue"
import MoneyInput from "@/components/MoneyInput.vue"
import SegmentedControl from "@/components/SegmentedControl.vue"
import { QUICK_ITEMS } from "@/constants/categoryStyle"
import { ITEM_BY_ID, METHODS } from "@/constants/catalog"
import { saveTransactionVars, useDeleteTransaction, useSaveTransaction } from "@/rest/queries/ledger.mutations"
import type { Currency, ExpenseGroup, Method, Transaction, TxType } from "@/types/ledger"
import { formatInput, todayIso } from "@/utils/money"
import CatalogList from "./CatalogList.vue"
import CategoryGrid from "./CategoryGrid.vue"

const props = defineProps<{ type: TxType; tx?: Transaction }>()
const emit = defineEmits<{ close: [] }>()
const { t, methodLabel } = useI18n()
const { notify } = useUi()
const tg = useTelegram()
const save = useSaveTransaction()
const remove = useDeleteTransaction()

const tx = props.tx
const type = ref<TxType>(tx?.type ?? props.type)
const amount = ref(tx ? tx.amount : NaN)
const currency = ref<Currency>(tx?.currency ?? "UZS")
const item = ref(tx?.item ?? QUICK_ITEMS[props.type][0])
const date = ref(tx?.date ?? todayIso())
const method = ref<Method>(tx?.method ?? "card")
const note = ref(tx?.note ?? "")
const picking = ref(false)
const tried = ref(false)

// Tur almashsa, boshqa turga tegishli toifa qolib ketmasin
watch(type, (v) => {
  const it = ITEM_BY_ID[item.value]
  if (!it || (it.group === "inc") !== (v === "income")) item.value = QUICK_ITEMS[v][0]
})

const typeOptions = computed(() => [
  { value: "income" as const, label: t("income"), tone: "teal" as const },
  { value: "expense" as const, label: t("expense"), tone: "red" as const },
])
const methodOptions = computed(() => METHODS.map((m) => ({ value: m, label: methodLabel(m) })))
const amountOk = computed(() => amount.value > 0)

function submit() {
  tried.value = true
  if (!amountOk.value || !item.value) return
  const it = ITEM_BY_ID[item.value]
  const group = type.value === "income" ? "inc" : ((it && it.group !== "inc" ? it.group : "exp") as ExpenseGroup)
  save.mutate(
    saveTransactionVars(
      {
        type: type.value,
        group,
        item: item.value,
        category: it?.category ?? item.value,
        amount: amount.value,
        currency: currency.value,
        date: date.value || todayIso(),
        method: method.value,
        note: note.value.trim(),
      },
      tx?.id,
    ),
    { onSuccess: () => (notify(t("saved")), tg.haptic("success")) },
  )
  emit("close")
}

async function destroy() {
  if (!tx || !(await tg.confirm(t("confirm_delete")))) return
  remove.mutate(tx.id, { onSuccess: () => notify(t("deleted")) })
  emit("close")
}
</script>

<template>
  <BaseSheet :title="t(tx ? 'edit_record' : 'new_record')" full @close="emit('close')">
    <CatalogList v-if="picking" v-model="item" :type="type" @back="picking = false" />

    <form v-else id="record-form" @submit.prevent="submit">
      <SegmentedControl v-model="type" :options="typeOptions" :label="t('category')" size="lg" />

      <label class="amount">
        <span class="amount__label">{{ t("amount") }}</span>
        <span class="amount__row">
          <!-- Ko'rinmas nusxa maydon kengligini matnga tenglaydi: summa "so'm" bilan birga markazda turadi -->
          <span class="amount__fit num">
            <span class="amount__mirror" aria-hidden="true">{{ formatInput(amount) || "0" }}</span>
            <MoneyInput v-model="amount" class="amount__input" :aria-invalid="tried && !amountOk" />
          </span>
          <span class="amount__cur">{{ currency === "USD" ? "$" : t("sum") }}</span>
        </span>
      </label>
      <div class="cur" role="radiogroup" :aria-label="t('amount')">
        <button type="button" role="radio" class="chip" :class="{ 'chip--on': currency === 'UZS' }" :aria-checked="currency === 'UZS'" @click="currency = 'UZS'">{{ t("sum") }}</button>
        <button type="button" role="radio" class="chip" :class="{ 'chip--on': currency === 'USD' }" :aria-checked="currency === 'USD'" @click="currency = 'USD'">{{ t("usd") }}</button>
      </div>
      <p v-if="tried && !amountOk" class="field-error center">{{ t("err_amount") }}</p>

      <div class="field">
        <span class="field__label">{{ t("category") }}</span>
        <CategoryGrid v-model="item" :type="type" @more="picking = true" />
      </div>

      <div class="row-2">
        <label class="field">
          <span class="field__label">{{ t("date") }}</span>
          <input v-model="date" class="input" type="date" required />
        </label>
        <div class="field">
          <span class="field__label">{{ t("method") }}</span>
          <SegmentedControl v-model="method" :options="methodOptions" :label="t('method')" class="method" />
        </div>
      </div>

      <label class="field">
        <span class="field__label">{{ t("note") }}</span>
        <input v-model="note" class="input" maxlength="1000" :placeholder="t('note_ph')" />
      </label>
    </form>

    <template v-if="!picking" #footer>
      <button v-if="tx" class="btn btn--danger" type="button" :aria-label="t('delete')" @click="destroy"><AppIcon name="trash" /></button>
      <button class="btn btn--primary btn--block" type="submit" form="record-form">{{ t("save") }}</button>
    </template>
  </BaseSheet>
</template>

<style scoped>
.amount {
  display: grid;
  justify-items: center;
  margin-top: 26px;
}

.amount__label {
  color: var(--text-2);
  font-size: 18px;
}

.amount__row {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 10px;
  width: 100%;
}

.amount__fit {
  position: relative;
  display: inline-block;
  max-width: calc(100% - 70px);
  font-size: clamp(40px, 13vw, 62px);
  font-weight: 600;
}

.amount__mirror,
.amount__input {
  padding: 6px 2px;
  font: inherit;
  white-space: pre;
}

.amount__mirror {
  display: block;
  overflow: hidden;
  visibility: hidden;
}

.amount__input {
  position: absolute;
  inset: 0;
  width: 100%;
  border: 0;
  outline: none;
  background: transparent;
  text-align: center;
}

.amount__input::placeholder {
  color: var(--surface-3);
}

.amount__cur {
  flex: none;
  color: var(--text-2);
  font-size: 24px;
}

.cur {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 10px;
}

.chip {
  min-width: 96px;
  height: 46px;
  padding: 0 18px;
  border-radius: var(--r-pill);
  border: 1px solid var(--border-strong);
  color: var(--text-2);
  font-size: 18px;
  font-weight: 500;
}

.chip--on {
  border-color: var(--teal);
  background: rgba(var(--tone-teal), 0.14);
  color: var(--teal);
  font-weight: 600;
}

.center {
  text-align: center;
}

.method :deep(.seg__opt) {
  min-height: 42px;
  font-size: 15px;
}

@media (max-width: 420px) {
  .row-2 {
    grid-template-columns: 1fr;
    gap: 0;
  }
}
</style>
