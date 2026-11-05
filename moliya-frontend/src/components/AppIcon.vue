<script setup lang="ts">
import { ICONS, type IconName } from "@/constants/icons"

withDefaults(defineProps<{ name: IconName; size?: number; stroke?: number }>(), { size: 24, stroke: 2 })
</script>

<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    :stroke-width="stroke"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
    focusable="false"
  >
    <path v-for="(d, i) in ICONS[name]" :key="i" :d="d" />
  </svg>
</template>
