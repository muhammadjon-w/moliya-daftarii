<script setup lang="ts">
import { computed } from "vue"
import { byCategory } from "@/domain/ledger"
import type { Transaction } from "@/domain/types"
import { useI18n } from "@/presentation/i18n"

const props = defineProps<{ list: Transaction[]; usdRate: number; income: boolean; empty: string; limit?: number }>()
const { catLabel, sum } = useI18n()

const rows = computed(() => byCategory(props.list, props.usdRate, props.income))
const total = computed(() => rows.value.reduce((s, r) => s + r.value, 0))
</script>

<template>
  <p v-if="!rows.length" class="muted-note">{{ empty }}</p>
  <div v-else class="cat-list">
    <div v-for="r in rows.slice(0, limit ?? 10)" :key="r.key" class="cat-row">
      <span class="nm">{{ catLabel(r.key) }}</span>
      <span class="am">{{ sum(r.value) }} · {{ total ? Math.round((r.value / total) * 100) : 0 }}%</span>
      <div class="cat-bar" :class="{ inc: income }"><i :style="{ width: ((r.value / rows[0].value) * 100).toFixed(1) + '%' }"></i></div>
    </div>
  </div>
</template>
