<script setup lang="ts">
import { computed, ref } from "vue"
import { CATEGORIES, EXPENSE_GROUPS, ITEMS, ITEM_BY_ID, METHODS } from "@/domain/catalog"
import { monthKey, todayIso } from "@/domain/money"
import type { Currency, ExpenseGroup, Method, Transaction, TransactionDraft, TxType } from "@/domain/types"
import { useGateways } from "@/application/container"
import { saveTransactionVars, useSaveTransaction } from "@/application/ledger/mutations"
import { useUiStore } from "@/application/session/ui"
import { useI18n } from "@/presentation/i18n"
import ModalShell from "../common/ModalShell.vue"
import MoneyInput from "../common/MoneyInput.vue"

const CUSTOM = "__custom"
const props = defineProps<{ type: TxType; tx?: Transaction | null }>()
const emit = defineEmits<{ close: [] }>()

const ui = useUiStore()
const { platform } = useGateways()
const save = useSaveTransaction()
const { t, itemLabel, catLabel, groupLabel, methodLabel } = useI18n()

const editing = props.tx ?? null
const known = editing && ITEM_BY_ID[editing.item] ? editing.item : null
const now = new Date()
const inMonth = now.getFullYear() === ui.period.y && now.getMonth() === ui.period.m

const type = ref<TxType>(editing ? (editing.type === "income" ? "income" : "expense") : props.type)
const item = ref(editing ? known ?? CUSTOM : props.type === "income" ? "salary" : "meals")
const custom = ref(editing && !known ? editing.item || editing.category : "")
const customGroup = ref<ExpenseGroup>(editing && editing.group !== "inc" ? editing.group : "exp")
const amount = ref(editing ? editing.amount : NaN)
const currency = ref<Currency>(editing?.currency ?? "UZS")
const date = ref(editing?.date ?? (inMonth ? todayIso() : monthKey(ui.period.y, ui.period.m) + "-01"))
const method = ref<Method>(editing?.method ?? "cash")
const note = ref(editing?.note ?? "")
const tried = ref(false)

const isCustom = computed(() => item.value === CUSTOM)
const amountOk = computed(() => amount.value > 0)
const customOk = computed(() => !isCustom.value || !!custom.value.trim())
const title = computed(() => (editing ? t("edit_tx") : t(type.value === "income" ? "new_income" : "new_expense")))

const optionGroups = computed(() => {
  if (type.value === "income") {
    return Object.keys(CATEGORIES)
      .map((c) => ({ label: catLabel(c), items: ITEMS.filter((i) => i.group === "inc" && i.category === c).map((i) => ({ id: i.id, label: itemLabel(i.id) })) }))
      .filter((g) => g.items.length)
  }
  return EXPENSE_GROUPS.map((g) => ({
    label: groupLabel(g),
    items: ITEMS.filter((i) => i.group === g).map((i) => ({ id: i.id, label: itemLabel(i.id) + " · " + catLabel(i.category) })),
  }))
})
const autoNote = computed(() => {
  const it = ITEM_BY_ID[item.value]
  if (isCustom.value || !it) return null
  return { cat: catLabel(it.category), group: it.group !== "inc" ? groupLabel(it.group) : null }
})

function setType(v: TxType) {
  if (type.value === v) return
  type.value = v
  item.value = v === "income" ? "salary" : "meals"
}

function submit() {
  tried.value = true
  if (!amountOk.value || !customOk.value) return
  const it = ITEM_BY_ID[item.value]
  const name = custom.value.trim()
  const draft: TransactionDraft = {
    type: type.value,
    item: isCustom.value ? name : item.value,
    category: isCustom.value ? name : it.category,
    group: type.value === "income" ? "inc" : isCustom.value ? customGroup.value : it.group,
    amount: Math.round(amount.value * 100) / 100,
    currency: currency.value,
    date: date.value || monthKey(ui.period.y, ui.period.m) + "-01",
    method: method.value,
    note: note.value.trim(),
  }
  save.mutate(saveTransactionVars(draft, editing?.id), {
    onSuccess: () => {
      ui.notify(t("saved"))
      platform.haptic("success")
    },
  })
  // Optimistik: oyna darhol yopiladi, yozuv ro'yxatda ko'rinadi; xato bo'lsa orqaga qaytariladi va xabar chiqadi
  const [y, m] = draft.date.split("-").map(Number)
  ui.setPeriod({ y, m: m - 1 })
  emit("close")
}
</script>

<template>
  <ModalShell :title="title" autofocus=".money" @close="emit('close')" @submit="submit">
    <div class="type-switch">
      <button type="button" class="inc" :class="{ on: type === 'income' }" @click="setType('income')">{{ t("g_inc") }}</button>
      <button type="button" class="exp" :class="{ on: type === 'expense' }" @click="setType('expense')">{{ t("l_out") }}</button>
    </div>
    <label>
      <span>{{ t("f_item") }}</span>
      <select v-model="item">
        <optgroup v-for="g in optionGroups" :key="g.label" :label="g.label">
          <option v-for="o in g.items" :key="o.id" :value="o.id">{{ o.label }}</option>
        </optgroup>
        <option :value="CUSTOM">{{ t("custom_opt") }}</option>
      </select>
    </label>
    <div v-if="isCustom" class="row2">
      <label><span>{{ t("f_custom") }}</span><input v-model="custom" autocomplete="off" /></label>
      <label v-if="type === 'expense'">
        <span>{{ t("f_group") }}</span>
        <select v-model="customGroup"><option v-for="g in EXPENSE_GROUPS" :key="g" :value="g">{{ groupLabel(g) }}</option></select>
      </label>
    </div>
    <p class="auto-note">
      <template v-if="autoNote">
        {{ t("auto_cat") }}: <b>{{ autoNote.cat }}</b><template v-if="autoNote.group"> · {{ t("auto_group") }}: <b>{{ autoNote.group }}</b></template>
      </template>
    </p>
    <div class="row2">
      <label><span>{{ t("f_amount") }}</span><MoneyInput v-model="amount" /></label>
      <label>
        <span>{{ t("f_currency") }}</span>
        <select v-model="currency"><option value="UZS">{{ t("sum") }}</option><option value="USD">$</option></select>
      </label>
    </div>
    <div v-if="tried && !amountOk" class="field-error">{{ t("err_amount") }}</div>
    <div v-if="tried && !customOk" class="field-error">{{ t("err_custom") }}</div>
    <div class="row2">
      <label><span>{{ t("f_date") }}</span><input v-model="date" type="date" required /></label>
      <label>
        <span>{{ t("f_method") }}</span>
        <select v-model="method"><option v-for="m in METHODS" :key="m" :value="m">{{ methodLabel(m) }}</option></select>
      </label>
    </div>
    <label><span>{{ t("f_note") }}</span><textarea v-model="note" rows="2"></textarea></label>
    <div class="modal-actions">
      <button class="btn-ghost" type="button" @click="emit('close')">{{ t("cancel") }}</button>
      <button class="btn-primary" :class="{ expense: type === 'expense' }" type="submit" :disabled="save.isPending.value">{{ t("save") }}</button>
    </div>
  </ModalShell>
</template>
