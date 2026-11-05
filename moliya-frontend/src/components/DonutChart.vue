<script setup lang="ts">
// Halqa diagramma. Bo'laklar orasida kichik bo'shliq; markazga slot orqali matn.
import { computed } from "vue"
import type { Tone } from "@/types/ui"

const props = withDefaults(defineProps<{ parts: { value: number; tone: Tone; label: string }[]; size?: number; thickness?: number }>(), {
  size: 170,
  thickness: 16,
})

const R = 50
const C = 2 * Math.PI * R
const GAP = 1.6

const arcs = computed(() => {
  const total = props.parts.reduce((s, p) => s + p.value, 0)
  if (total <= 0) return []
  const single = props.parts.filter((p) => p.value > 0).length === 1
  let offset = 0
  return props.parts
    .filter((p) => p.value > 0)
    .map((p) => {
      const len = (p.value / total) * C
      const arc = { tone: p.tone, label: p.label, dash: `${Math.max(len - (single ? 0 : GAP), 0.01)} ${C}`, offset: -offset }
      offset += len
      return arc
    })
})
</script>

<template>
  <div class="donut" :style="{ width: size + 'px', height: size + 'px' }">
    <svg viewBox="0 0 120 120" role="img" :aria-label="parts.map((p) => p.label).join(', ')">
      <circle cx="60" cy="60" :r="R" fill="none" stroke="var(--surface-3)" :stroke-width="thickness * 0.75" />
      <circle
        v-for="(a, i) in arcs"
        :key="i"
        cx="60"
        cy="60"
        :r="R"
        fill="none"
        :stroke="`rgb(var(--tone-${a.tone}))`"
        :stroke-width="thickness * 0.75"
        :stroke-dasharray="a.dash"
        :stroke-dashoffset="a.offset"
        transform="rotate(-90 60 60)"
      />
    </svg>
    <div class="donut__center"><slot /></div>
  </div>
</template>

<style scoped>
.donut {
  position: relative;
  flex: none;
}

.donut svg {
  width: 100%;
  height: 100%;
}

.donut__center {
  position: absolute;
  inset: 0;
  display: grid;
  place-content: center;
  text-align: center;
}
</style>
