<script setup lang="ts">
// Rangli fon ustidagi ikonka (yozuvlar, tez amallar, qarzlar).
import type { IconName } from "@/constants/icons"
import type { Tone } from "@/types/ui"
import AppIcon from "./AppIcon.vue"

withDefaults(defineProps<{ icon?: IconName; text?: string; tone: Tone; size?: number; iconSize?: number; outlined?: boolean }>(), {
  size: 52,
  iconSize: 22,
  outlined: false,
})
</script>

<template>
  <span
    class="tile"
    :class="{ 'tile--outlined': outlined }"
    :style="{ '--rgb': `var(--tone-${tone})`, width: size + 'px', height: size + 'px', borderRadius: Math.round(size * 0.3) + 'px' }"
  >
    <AppIcon v-if="icon" :name="icon" :size="iconSize" />
    <span v-else class="tile__text">{{ text }}</span>
  </span>
</template>

<style scoped>
.tile {
  display: inline-grid;
  place-items: center;
  flex: none;
  color: rgb(var(--rgb));
  background: rgba(var(--rgb), 0.14);
}

.tile--outlined {
  background: rgba(var(--rgb), 0.12);
  border: 1px solid rgba(var(--rgb), 0.45);
}

.tile__text {
  font-weight: 600;
  font-size: 20px;
  letter-spacing: 0.02em;
}
</style>
