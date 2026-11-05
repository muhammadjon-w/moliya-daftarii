<script setup lang="ts">
// Oy va yilni tanlash.
import { ref } from "vue"
import { useI18n } from "@/composables/useI18n"
import { useUi } from "@/composables/useUi"
import AppIcon from "@/components/AppIcon.vue"
import BaseSheet from "@/components/BaseSheet.vue"

const emit = defineEmits<{ close: [] }>()
const { ui, setPeriod } = useUi()
const { t, monthName } = useI18n()
const year = ref(ui.period.y)
const now = new Date()

function pick(m: number) {
  setPeriod({ y: year.value, m })
  emit("close")
}
</script>

<template>
  <BaseSheet :title="t('pick_month')" @close="emit('close')">
    <div class="mp__year">
      <button type="button" aria-label="−1" @click="year--"><AppIcon name="chevronLeft" /></button>
      <b class="num">{{ year }}</b>
      <button type="button" aria-label="+1" @click="year++"><AppIcon name="chevronRight" /></button>
    </div>
    <div class="mp__grid">
      <button
        v-for="m in 12"
        :key="m"
        type="button"
        class="mp__m"
        :class="{ 'mp__m--on': ui.period.y === year && ui.period.m === m - 1, 'mp__m--now': now.getFullYear() === year && now.getMonth() === m - 1 }"
        @click="pick(m - 1)"
      >
        {{ monthName(m - 1) }}
      </button>
    </div>
  </BaseSheet>
</template>

<style scoped>
.mp__year {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  margin: 6px 0 18px;
  font-size: 24px;
}

.mp__year button {
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--surface-2);
}

.mp__grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.mp__m {
  min-height: 54px;
  border-radius: var(--r-md);
  background: var(--surface);
  border: 1px solid var(--border);
  font-weight: 500;
}

.mp__m--now {
  border-color: rgba(var(--tone-teal), 0.5);
}

.mp__m--on {
  background: var(--teal);
  color: var(--teal-ink);
  font-weight: 600;
}
</style>
