<script setup lang="ts">
import { computed } from "vue"

const props = defineProps<{ values: number[]; color: string }>()
const W = 120
const H = 40
const points = computed(() => {
  let v = props.values
  if (!v.length || v.every((x) => x === 0)) return ""
  if (v.length === 1) v = [v[0], v[0]]
  const mx = Math.max(...v)
  const mn = Math.min(...v)
  const rg = mx - mn || 1
  return v.map((x, i) => ((i * W) / (v.length - 1)).toFixed(1) + "," + (H - 4 - ((x - mn) / rg) * (H - 8)).toFixed(1)).join(" ")
})
</script>

<template>
  <svg class="spark" viewBox="0 0 120 40" aria-hidden="true">
    <polyline v-if="points" :points="points" fill="none" :stroke="color" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" />
  </svg>
</template>
