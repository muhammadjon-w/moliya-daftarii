<script setup lang="ts">
// Reja bajarilishi: rejasi bor toifalar, holat yorlig'i bilan ("+600 000 oshdi", "93% bajarildi").
import { useI18n } from "@/composables/useI18n"
import { ROUTES } from "@/constants/routes"
import { planStatus, type PlanRow, type PlanStatus } from "@/utils/ledger"
import { num } from "@/utils/money"

defineProps<{ rows: PlanRow[] }>()
const { t, catLabel } = useI18n()

function pill(s: PlanStatus): { text: string; cls: string } {
  switch (s.kind) {
    case "over":
      return { text: t("plan_over", { v: num(s.amount) }), cls: "pill--red" }
    case "left":
      return { text: t("plan_left", { v: num(s.amount) }), cls: "pill--teal" }
    case "done":
      return { text: t("plan_done"), cls: "pill--teal" }
    case "progress":
      return { text: t("plan_progress", { p: s.pct }), cls: "pill--yellow" }
  }
}
</script>

<template>
  <section>
    <h2 class="section-title">{{ t("plan_exec") }}</h2>
    <div class="card plan">
      <div v-for="r in rows" :key="r.key" class="plan__row">
        <div class="plan__main">
          <span class="plan__name">{{ catLabel(r.category) }}</span>
          <span class="plan__sub num">{{ t("plan_line", { v: num(r.plan) }) }}</span>
        </div>
        <span class="pill" :class="pill(planStatus(r)).cls">{{ pill(planStatus(r)).text }}</span>
      </div>
      <div v-if="!rows.length" class="plan__empty">
        <p class="muted">{{ t("plan_empty") }}</p>
        <RouterLink class="link" :to="{ name: ROUTES.plan }">{{ t("make_plan") }}</RouterLink>
      </div>
    </div>
  </section>
</template>

<style scoped>
.plan {
  display: grid;
  gap: 22px;
  padding: 22px;
}

.plan__row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.plan__main {
  display: grid;
  gap: 4px;
  min-width: 0;
}

.plan__name {
  font-size: 19px;
}

.plan__sub {
  color: var(--muted);
  font-size: 15px;
}

.pill {
  flex: none;
  padding: 9px 16px;
  border-radius: var(--r-md);
  font-size: 16px;
  font-weight: 600;
  white-space: nowrap;
}

.pill--red {
  background: rgba(var(--tone-red), 0.14);
  color: var(--red);
}

.pill--yellow {
  background: rgba(var(--tone-yellow), 0.14);
  color: var(--yellow);
}

.pill--teal {
  background: rgba(var(--tone-teal), 0.14);
  color: var(--teal);
}

.plan__empty {
  display: grid;
  justify-items: start;
  gap: 8px;
}
</style>
