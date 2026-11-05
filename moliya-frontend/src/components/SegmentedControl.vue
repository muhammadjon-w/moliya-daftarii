<script setup lang="ts" generic="T extends string">
// Bir nechta variantdan bittasini tanlash (Tushum/Chiqim, Naqd/Karta/Bank).
// activeTone berilsa tanlangan variant o'sha rang bilan to'ldiriladi.
import type { Tone } from "@/types/ui"

defineProps<{ options: { value: T; label: string; tone?: Tone }[]; label: string; size?: "lg" | "md" }>()
const model = defineModel<T>({ required: true })
</script>

<template>
  <div class="seg" :class="'seg--' + (size ?? 'md')" role="radiogroup" :aria-label="label">
    <button
      v-for="o in options"
      :key="o.value"
      type="button"
      role="radio"
      class="seg__opt"
      :class="{ 'seg__opt--on': model === o.value, 'seg__opt--tone': model === o.value && o.tone }"
      :style="o.tone ? { '--rgb': `var(--tone-${o.tone})` } : undefined"
      :aria-checked="model === o.value"
      @click="model = o.value"
    >
      {{ o.label }}
    </button>
  </div>
</template>

<style scoped>
.seg {
  display: flex;
  gap: 4px;
  padding: 5px;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
}

.seg__opt {
  flex: 1;
  min-height: 44px;
  border-radius: var(--r-md);
  color: var(--muted);
  font-weight: 500;
  font-size: 17px;
  transition: background 0.15s, color 0.15s;
}

.seg--lg .seg__opt {
  min-height: 58px;
  font-size: 21px;
}

.seg__opt--on {
  background: var(--surface-3);
  color: var(--text);
}

.seg__opt--tone {
  background: rgb(var(--rgb));
  color: var(--bg-deep);
  font-weight: 600;
}
</style>
