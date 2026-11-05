<script setup lang="ts">
// Eng ko'p sarflangan moddalar: chiziq uzunligi eng kattasiga nisbatan, rangi guruhga qarab.
import { computed } from "vue"
import { useI18n } from "@/composables/useI18n"
import ProgressBar from "@/components/ProgressBar.vue"
import { GROUP_TONE } from "@/constants/categoryStyle"
import type { ItemSum } from "@/utils/ledger"
import { num } from "@/utils/money"

const props = defineProps<{ items: ItemSum[] }>()
const { t, itemLabel } = useI18n()
const max = computed(() => Math.max(1, ...props.items.map((i) => i.value)))
</script>

<template>
  <section>
    <h2 class="section-title">{{ t("top_spent") }}</h2>
    <div class="card top">
      <div v-for="i in items" :key="i.item" class="top__row">
        <div class="top__line">
          <span>{{ itemLabel(i.item) }}</span>
          <b class="num">{{ num(i.value) }}</b>
        </div>
        <ProgressBar :value="(i.value / max) * 100" :tone="GROUP_TONE[i.group]" :height="10" />
      </div>
      <p v-if="!items.length" class="muted">{{ t("no_expense") }}</p>
    </div>
  </section>
</template>

<style scoped>
.top {
  display: grid;
  gap: 22px;
  padding: 24px 22px;
}

.top__line {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
  font-size: 18px;
}

.top__line b {
  font-weight: 600;
}
</style>
