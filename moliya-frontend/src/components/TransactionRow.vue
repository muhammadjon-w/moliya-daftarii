<script setup lang="ts">
// Bitta yozuv qatori: ikonka, nom, "05.11 · Bank", summa. Bosh sahifa va Yozuvlar sahifasida ishlatiladi.
import { computed } from "vue"
import { useI18n } from "@/composables/useI18n"
import { lookOf } from "@/constants/categoryStyle"
import type { Transaction } from "@/types/ledger"
import { groupOf } from "@/utils/ledger"
import { shortDate } from "@/utils/money"
import IconTile from "./IconTile.vue"

const props = defineProps<{ tx: Transaction }>()
defineEmits<{ open: [Transaction] }>()
const { itemLabel, methodLabel, signedAmount } = useI18n()

const look = computed(() => lookOf(props.tx.item, props.tx.category, groupOf(props.tx)))
const income = computed(() => props.tx.type === "income")
const pending = computed(() => props.tx.id.startsWith("tmp-"))
</script>

<template>
  <button class="row" :class="{ 'row--pending': pending }" type="button" @click="$emit('open', tx)">
    <IconTile :icon="look.icon" :tone="look.tone" />
    <span class="row__main">
      <span class="row__title">{{ itemLabel(tx.item) }}</span>
      <span class="row__meta">{{ shortDate(tx.date) }} · {{ methodLabel(tx.method) }}</span>
    </span>
    <span class="row__amount num" :class="{ positive: income }">{{ signedAmount(tx.amount, income, tx.currency) }}</span>
  </button>
</template>

<style scoped>
.row {
  display: flex;
  align-items: center;
  gap: 16px;
  width: 100%;
  padding: 18px 22px;
  text-align: left;
}

.row + .row {
  border-top: 1px solid var(--border);
}

.row--pending {
  opacity: 0.6;
}

.row__main {
  display: grid;
  gap: 4px;
  flex: 1;
  min-width: 0;
}

.row__title {
  overflow: hidden;
  font-size: 19px;
  font-weight: 500;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.row__meta {
  overflow: hidden;
  color: var(--muted);
  font-size: 15px;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.row__amount {
  flex: none;
  font-size: 19px;
  font-weight: 600;
}
</style>
