<script setup lang="ts">
// Bir guruh (Tushum / To'lovlar / Xarajatlar / Qarz to'lovi) toifalari: reja summasi va fakt.
import { computed } from "vue"
import { useI18n } from "@/composables/useI18n"
import MoneyInput from "@/components/MoneyInput.vue"
import ProgressBar from "@/components/ProgressBar.vue"
import { GROUP_TONE } from "@/constants/categoryStyle"
import type { Group } from "@/types/ledger"
import type { PlanRow } from "@/utils/ledger"
import { num } from "@/utils/money"

const props = defineProps<{ group: Group; rows: PlanRow[] }>()
const emit = defineEmits<{ change: [key: string, value: number] }>()
const { t, groupLabel, catLabel } = useI18n()

const total = computed(() => props.rows.reduce((s, r) => ({ plan: s.plan + r.plan, fact: s.fact + r.fact }), { plan: 0, fact: 0 }))
const tone = (r: PlanRow) => (r.group !== "inc" && r.fact > r.plan ? "red" : GROUP_TONE[props.group])
</script>

<template>
  <section>
    <h2 class="section-title">
      {{ groupLabel(group) }}
      <small class="pg__total num">{{ num(total.fact) }} / {{ num(total.plan) }}</small>
    </h2>
    <div class="card pg">
      <div v-for="r in rows" :key="r.key" class="pg__row">
        <div class="pg__line">
          <label :for="'plan-' + r.key" class="pg__name">{{ catLabel(r.category) }}</label>
          <MoneyInput :id="'plan-' + r.key" class="pg__input num" :model-value="r.plan" @commit="(v) => emit('change', r.key, v)" />
        </div>
        <div v-if="r.plan || r.fact" class="pg__fact">
          <ProgressBar v-if="r.plan" :value="(r.fact / r.plan) * 100" :tone="tone(r)" :height="6" />
          <span class="num">{{ t("fact", { v: num(r.fact) }) }}</span>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.pg__total {
  color: var(--muted);
  font-size: 15px;
  font-weight: 500;
}

.pg {
  padding: 6px 20px;
}

.pg__row {
  padding: 14px 0;
}

.pg__row + .pg__row {
  border-top: 1px solid var(--border);
}

.pg__line {
  display: flex;
  align-items: center;
  gap: 12px;
}

.pg__name {
  flex: 1;
  min-width: 0;
  font-size: 17px;
}

.pg__input {
  width: 46%;
  max-width: 180px;
  height: 46px;
  padding: 0 14px;
  border-radius: var(--r-sm);
  border: 1px solid var(--border);
  background: var(--surface-2);
  outline: none;
  text-align: right;
  font-size: 17px;
  font-weight: 500;
}

.pg__input:focus {
  border-color: rgba(var(--tone-teal), 0.6);
}

.pg__fact {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 10px;
  color: var(--muted);
  font-size: 14px;
}

.pg__fact span {
  flex: none;
}
</style>
