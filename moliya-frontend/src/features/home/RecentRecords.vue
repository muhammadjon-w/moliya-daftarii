<script setup lang="ts">
// So'nggi yozuvlar (tanlangan oy) va "Hammasi" havolasi.
import { useI18n } from "@/composables/useI18n"
import { useSheets } from "@/composables/useSheets"
import TransactionRow from "@/components/TransactionRow.vue"
import { ROUTES } from "@/constants/routes"
import type { Transaction } from "@/types/ledger"

defineProps<{ items: Transaction[] }>()
const sheets = useSheets()
const { t } = useI18n()
</script>

<template>
  <section>
    <h2 class="section-title">
      {{ t("recent") }}
      <RouterLink class="link" :to="{ name: ROUTES.records }">{{ t("see_all") }}</RouterLink>
    </h2>
    <div v-if="items.length" class="card">
      <TransactionRow v-for="tx in items" :key="tx.id" :tx="tx" @open="sheets.editRecord" />
    </div>
    <p v-else class="card empty">{{ t("empty_records") }}</p>
  </section>
</template>

<style scoped>
.empty {
  padding: 28px 22px;
  color: var(--text-2);
  text-align: center;
}
</style>
