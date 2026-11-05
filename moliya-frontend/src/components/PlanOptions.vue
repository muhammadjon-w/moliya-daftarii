<script setup lang="ts">
// Tarif tanlash (1 / 6 / 12 oy). Eng arzon oylik narxli tarif "Tejamkor" belgisi bilan.
// Mini app'dagi to'lov oynasi va /obuna sahifasida ishlatiladi.
import { computed, watch } from "vue"
import { useI18n } from "@/composables/useI18n"
import type { Prices } from "@/types/account"
import { num } from "@/utils/money"

const props = defineProps<{ prices: Prices }>()
const model = defineModel<number | null>({ required: true })
const { t } = useI18n()

const options = computed(() =>
  Object.entries(props.prices)
    .map(([m, v]) => ({ months: Number(m), amount: v }))
    .sort((a, b) => a.months - b.months),
)
const best = computed(() => {
  const o = options.value
  return o.length < 2 ? null : o.reduce((b, x) => (x.amount / x.months < b.amount / b.months ? x : b)).months
})

// Hech narsa tanlanmagan bo'lsa — eng tejamkor tarif
watch(
  options,
  (o) => {
    if (o.length && !o.some((x) => x.months === model.value)) model.value = best.value ?? o[0].months
  },
  { immediate: true },
)
</script>

<template>
  <div class="po" role="radiogroup">
    <button
      v-for="o in options"
      :key="o.months"
      type="button"
      role="radio"
      class="po__opt"
      :class="{ 'po__opt--on': model === o.months }"
      :aria-checked="model === o.months"
      @click="model = o.months"
    >
      <span v-if="best === o.months" class="po__tag">{{ t("best") }}</span>
      <span class="po__left">
        <b>{{ t("plan_months", { n: o.months }) }}</b>
        <small class="num">{{ t("per_month", { v: num(o.amount / o.months) }) }}</small>
      </span>
      <b class="po__price num">{{ num(o.amount) }} {{ t("sum") }}</b>
    </button>
  </div>
</template>

<style scoped>
.po {
  display: grid;
  gap: 14px;
}

.po__opt {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-height: 92px;
  padding: 16px 22px;
  border-radius: var(--r-lg);
  background: var(--surface);
  border: 1px solid var(--border-strong);
  text-align: left;
}

.po__opt--on {
  background: rgba(var(--tone-teal), 0.08);
  border: 2px solid var(--teal);
}

.po__left {
  display: grid;
  gap: 4px;
}

.po__left b {
  font-size: 22px;
  font-weight: 600;
}

.po__left small {
  color: var(--muted);
  font-size: 16px;
}

.po__price {
  font-size: 22px;
  font-weight: 600;
  white-space: nowrap;
}

.po__tag {
  position: absolute;
  top: -14px;
  right: 22px;
  padding: 4px 14px;
  border-radius: var(--r-pill);
  background: var(--yellow);
  color: var(--bg-deep);
  font-size: 14px;
  font-weight: 600;
}
</style>
