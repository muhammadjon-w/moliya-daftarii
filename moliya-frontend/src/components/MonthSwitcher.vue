<script setup lang="ts">
// ‹ Noyabr 2026 › — tanlangan oyni almashtirish.
import { useI18n } from "@/composables/useI18n"
import { useUi } from "@/composables/useUi"
import AppIcon from "./AppIcon.vue"

const { ui, shiftPeriod } = useUi()
const { periodLabel } = useI18n()
</script>

<template>
  <div class="ms">
    <button class="ms__arrow" type="button" aria-label="−1" @click="shiftPeriod(-1)"><AppIcon name="chevronLeft" :size="22" /></button>
    <span class="ms__label">{{ periodLabel(ui.period) }}</span>
    <button class="ms__arrow" type="button" aria-label="+1" @click="shiftPeriod(1)"><AppIcon name="chevronRight" :size="22" /></button>
  </div>
</template>

<style scoped>
.ms {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  min-width: 0;
}

.ms__label {
  min-width: 140px;
  text-align: center;
  font-size: 22px;
  font-weight: 600;
  white-space: nowrap;
}

.ms__arrow {
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  color: var(--text-2);
}
</style>
