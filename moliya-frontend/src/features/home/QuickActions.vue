<script setup lang="ts">
// Tushum · Chiqim · Qarz · Reja — tez amallar.
import { useRouter } from "vue-router"
import { useI18n } from "@/composables/useI18n"
import { useSheets } from "@/composables/useSheets"
import IconTile from "@/components/IconTile.vue"
import { ROUTES } from "@/constants/routes"

const sheets = useSheets()
const router = useRouter()
const { t } = useI18n()
</script>

<template>
  <div class="qa">
    <button class="qa__btn" type="button" @click="sheets.newRecord('income')">
      <IconTile icon="arrowUp" tone="teal" :size="70" :icon-size="26" outlined />
      <span>{{ t("qa_income") }}</span>
    </button>
    <button class="qa__btn" type="button" @click="sheets.newRecord('expense')">
      <IconTile icon="arrowDown" tone="red" :size="70" :icon-size="26" outlined />
      <span>{{ t("qa_expense") }}</span>
    </button>
    <button class="qa__btn" type="button" @click="sheets.newDebt()">
      <IconTile icon="card" tone="yellow" :size="70" :icon-size="26" outlined />
      <span>{{ t("qa_debt") }}</span>
    </button>
    <button class="qa__btn" type="button" @click="router.push({ name: ROUTES.plan })">
      <IconTile icon="target" tone="blue" :size="70" :icon-size="26" outlined />
      <span>{{ t("qa_plan") }}</span>
    </button>
  </div>
</template>

<style scoped>
.qa {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  margin-top: 22px;
}

.qa__btn {
  display: grid;
  justify-items: center;
  gap: 10px;
  font-size: 17px;
  font-weight: 600;
}
</style>
