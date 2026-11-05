<script setup lang="ts">
// Yumaloq ikonka tugmasi (orqaga, yuklab olish).
import type { IconName } from "@/constants/icons"
import AppIcon from "./AppIcon.vue"

defineProps<{ icon: IconName; label: string }>()
</script>

<template>
  <button class="round" type="button" :aria-label="label" :title="label">
    <AppIcon :name="icon" :size="24" />
  </button>
</template>

<style scoped>
.round {
  display: grid;
  place-items: center;
  flex: none;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--surface-2);
  border: 1px solid var(--border);
}
</style>
