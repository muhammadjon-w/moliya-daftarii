<script setup lang="ts">
// So'rov holati: birinchi yuklanish, xato, tayyor. Ma'lumot keshda bo'lsa darhol kontent ko'rsatiladi.
import { toRef } from "vue"
import { useI18n } from "@/composables/useI18n"
import { useSlowLoading } from "@/composables/useSlowLoading"

const props = defineProps<{ pending: boolean; error: unknown; hasData: boolean }>()
const emit = defineEmits<{ retry: [] }>()
const { t } = useI18n()
const slow = useSlowLoading(toRef(() => props.pending && !props.hasData))
</script>

<template>
  <slot v-if="hasData" />
  <div v-else-if="pending" class="state" role="status">
    <span class="spinner" aria-hidden="true"></span>
    <p>{{ slow ? t("waking") : t("loading") }}</p>
  </div>
  <div v-else-if="error" class="state">
    <p>{{ t("load_error") }}</p>
    <button class="btn btn--primary" type="button" @click="emit('retry')">{{ t("retry") }}</button>
  </div>
</template>

<style scoped>
.state {
  display: grid;
  justify-items: center;
  gap: 16px;
  padding: 80px 20px;
  color: var(--text-2);
  text-align: center;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid var(--surface-3);
  border-top-color: var(--teal);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
