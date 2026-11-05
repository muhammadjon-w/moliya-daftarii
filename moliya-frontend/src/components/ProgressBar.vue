<script setup lang="ts">
import type { Tone } from "@/types/ui"

const props = withDefaults(defineProps<{ value: number; tone?: Tone; height?: number; track?: "dark" | "light" }>(), {
  tone: "teal",
  height: 10,
  track: "dark",
})
const width = () => Math.max(0, Math.min(100, props.value)).toFixed(1) + "%"
</script>

<template>
  <div class="bar" :class="'bar--' + track" :style="{ height: height + 'px' }" role="presentation">
    <i :style="{ width: width(), background: `rgb(var(--tone-${tone}))` }"></i>
  </div>
</template>

<style scoped>
.bar {
  width: 100%;
  overflow: hidden;
  border-radius: var(--r-pill);
}

.bar--dark {
  background: var(--surface-3);
}

.bar--light {
  background: rgba(255, 255, 255, 0.1);
}

.bar i {
  display: block;
  height: 100%;
  border-radius: inherit;
  transition: width 0.4s ease;
}
</style>
