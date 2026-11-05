<script setup lang="ts">
import { useI18n } from "@/presentation/i18n"
import ModalShell from "./ModalShell.vue"

defineProps<{ text: string }>()
const emit = defineEmits<{ close: []; confirm: [] }>()
const { t } = useI18n()
</script>

<template>
  <ModalShell :title="t('del_title')" :form="false" @close="emit('close')">
    <p style="margin: 0">{{ text }}</p>
    <div class="modal-actions">
      <button class="btn-ghost" type="button" @click="emit('close')">{{ t("cancel") }}</button>
      <button class="btn-ghost danger" type="button" @click="emit('confirm')">{{ t("delete") }}</button>
    </div>
  </ModalShell>
</template>
