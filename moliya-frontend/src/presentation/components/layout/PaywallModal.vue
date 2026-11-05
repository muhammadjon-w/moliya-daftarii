<script setup lang="ts">
// Obuna tugaganda: yozuvlar ko'rinadi, lekin yozish uchun to'lov saytiga yo'naltiriladi (to'lov Telegram ichida emas).
import { storeToRefs } from "pinia"
import { useGateways } from "@/application/container"
import { useUiStore } from "@/application/session/ui"
import { useI18n } from "@/presentation/i18n"
import ModalShell from "../common/ModalShell.vue"

const ui = useUiStore()
const { paywallOpen } = storeToRefs(ui)
const { platform } = useGateways()
const { t } = useI18n()
const siteUrl = (import.meta.env.VITE_SITE_URL || window.location.origin).replace(/\/$/, "")

function open() {
  platform.openLink(siteUrl + "/obuna")
  ui.paywallOpen = false
}
</script>

<template>
  <ModalShell v-if="paywallOpen" :title="t('pw_title')" :form="false" @close="ui.paywallOpen = false">
    <p class="pw-text">{{ t("pw_text") }}</p>
    <div class="modal-actions">
      <button class="btn-ghost" type="button" @click="ui.paywallOpen = false">{{ t("pw_later") }}</button>
      <button class="btn-primary" type="button" @click="open">{{ t("pw_btn") }}</button>
    </div>
  </ModalShell>
</template>
