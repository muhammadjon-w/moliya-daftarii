<script setup lang="ts">
// Bitta qarz: kimdan, muddat va to'lov sanasi, necha kun qolgani, qoldiq va "To'lash" tugmasi.
import { computed } from "vue"
import { useI18n } from "@/composables/useI18n"
import IconTile from "@/components/IconTile.vue"
import ProgressBar from "@/components/ProgressBar.vue"
import type { Tone } from "@/types/ui"
import type { DebtView } from "@/utils/ledger"
import { fmtDate, initials, num } from "@/utils/money"

const props = defineProps<{ view: DebtView; index: number }>()
defineEmits<{ open: []; pay: [] }>()
const { t } = useI18n()

const d = computed(() => props.view.debt)
const c = computed(() => props.view.calc)
const tone = computed<Tone>(() => (props.index % 2 ? "blue" : "teal"))
const meta = computed(() => {
  const due = d.value.payDate || d.value.deadline
  if (!c.value.months) return due ? fmtDate(due) : t("no_paydate")
  return due ? t("debt_meta", { n: c.value.months, d: fmtDate(due) }) : t("debt_meta_nodate", { n: c.value.months })
})
const days = computed(() => {
  const n = props.view.daysLeft
  if (n === null || c.value.remaining <= 0) return null
  if (n < 0) return { text: t("days_over", { n: -n }), cls: "days--red" }
  if (n === 0) return { text: t("due_today"), cls: "days--red" }
  return { text: t("days_left", { n }), cls: n <= 14 ? "days--yellow" : "" }
})
const payAmount = computed(() => c.value.monthly || c.value.remaining)
</script>

<template>
  <article class="card dc">
    <button class="dc__head" type="button" @click="$emit('open')">
      <IconTile :text="initials(d.lender)" :tone="tone" :size="64" />
      <span class="dc__main">
        <span class="dc__name">{{ d.lender || "—" }}</span>
        <span class="dc__meta">{{ meta }}</span>
      </span>
      <span v-if="days" class="days" :class="days.cls">{{ days.text }}</span>
    </button>
    <ProgressBar :value="c.paidPct" tone="teal" :height="10" />
    <div class="dc__foot">
      <div class="dc__left">
        <span>{{ t("remaining") }}</span>
        <b class="num">{{ num(c.remaining) }}</b>
      </div>
      <button v-if="c.remaining > 0" class="dc__pay num" type="button" @click="$emit('pay')">{{ t("pay_btn", { v: num(payAmount) }) }}</button>
    </div>
  </article>
</template>

<style scoped>
.dc {
  padding: 22px;
}

.dc + .dc {
  margin-top: 16px;
}

.dc__head {
  display: flex;
  align-items: center;
  gap: 16px;
  width: 100%;
  margin-bottom: 20px;
  text-align: left;
}

.dc__main {
  display: grid;
  gap: 4px;
  flex: 1;
  min-width: 0;
}

.dc__name {
  overflow: hidden;
  font-size: 22px;
  font-weight: 600;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.dc__meta {
  color: var(--muted);
  font-size: 16px;
}

.days {
  flex: none;
  padding: 8px 14px;
  border-radius: var(--r-md);
  background: var(--surface-3);
  color: var(--muted);
  font-size: 16px;
  font-weight: 600;
}

.days--yellow {
  background: rgba(var(--tone-yellow), 0.14);
  color: var(--yellow);
}

.days--red {
  background: rgba(var(--tone-red), 0.14);
  color: var(--red);
}

.dc__foot {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
  margin-top: 20px;
}

.dc__left {
  display: grid;
  gap: 4px;
}

.dc__left span {
  color: var(--muted);
  font-size: 16px;
}

.dc__left b {
  font-size: 24px;
  font-weight: 600;
}

.dc__pay {
  min-height: 56px;
  padding: 0 20px;
  border-radius: var(--r-md);
  background: rgba(var(--tone-teal), 0.1);
  border: 1px solid rgba(var(--tone-teal), 0.55);
  color: var(--teal);
  font-size: 18px;
  font-weight: 600;
  white-space: nowrap;
}

@media (max-width: 380px) {
  .dc__pay {
    padding: 0 12px;
    font-size: 15px;
  }
}
</style>
