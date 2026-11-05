<script setup lang="ts">
import { computed } from "vue"
import { axisLabel } from "@/domain/money"
import { useI18n } from "@/presentation/i18n"

const props = defineProps<{ months: { m: number; inc: number; out: number; hl: boolean }[]; label: string }>()
const { t, months: monthNames, sum } = useI18n()

const W = 600
const H = 230
const L = 58
const R = 10
const T = 12
const B = 30
const chart = computed(() => {
  const max = Math.max(1, ...props.months.map((x) => Math.max(x.inc, x.out)))
  const step = Math.pow(10, Math.floor(Math.log10(max)))
  let nice = Math.ceil(max / step) * step
  if (nice / step <= 2) nice = Math.ceil(max / (step / 2)) * (step / 2)
  const ch = H - T - B
  const gw = (W - L - R) / props.months.length
  const bw = Math.min(26, gw * 0.3)
  const grid = [0, 1, 2, 3, 4].map((g) => ({ y: T + ch - (ch * g) / 4, v: axisLabel((nice * g) / 4), dashed: g > 0 }))
  const bars = props.months.map((mo, i) => {
    const cx = L + gw * i + gw / 2
    const hi = (ch * mo.inc) / nice
    const he = (ch * mo.out) / nice
    return { ...mo, cx, inc: { x: cx - bw - 2, y: T + ch - hi, h: hi }, out: { x: cx + 2, y: T + ch - he, h: he }, raw: mo }
  })
  return { grid, bars, bw }
})
</script>

<template>
  <svg :viewBox="`0 0 ${W} ${H}`" role="img" :aria-label="label">
    <g v-for="g in chart.grid" :key="g.y">
      <line :x1="L" :x2="W - R" :y1="g.y" :y2="g.y" stroke="var(--border)" stroke-width="1" :stroke-dasharray="g.dashed ? '3 4' : undefined" />
      <text :x="L - 8" :y="g.y + 4" text-anchor="end">{{ g.v }}</text>
    </g>
    <g v-for="b in chart.bars" :key="b.m">
      <rect :x="b.inc.x" :y="b.inc.y" :width="chart.bw" :height="b.inc.h" rx="3" fill="var(--green)" :opacity="b.hl ? 1 : 0.55"><title>{{ t("g_inc") }}: {{ sum(b.raw.inc) }}</title></rect>
      <rect :x="b.out.x" :y="b.out.y" :width="chart.bw" :height="b.out.h" rx="3" fill="var(--brick)" :opacity="b.hl ? 1 : 0.55"><title>{{ t("l_out") }}: {{ sum(b.raw.out) }}</title></rect>
      <text :x="b.cx" :y="H - 10" text-anchor="middle" :style="b.hl ? 'fill:var(--ink);font-weight:700' : undefined">{{ monthNames()[b.m].slice(0, 3) }}</text>
    </g>
  </svg>
</template>
