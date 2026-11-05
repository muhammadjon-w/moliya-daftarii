<script setup lang="ts">
import { computed, watchEffect } from "vue"
import { useRoute } from "vue-router"
import { useGlassPointer } from "@/presentation/composables/useGlass"
import { useI18n } from "@/presentation/i18n"
import LedgerShell from "@/presentation/components/layout/LedgerShell.vue"
import ToastHost from "@/presentation/components/common/ToastHost.vue"

const route = useRoute()
const { lang } = useI18n()
const standalone = computed(() => route.meta.standalone === true)

useGlassPointer()
watchEffect(() => document.documentElement.setAttribute("lang", lang.value))
</script>

<template>
  <RouterView v-if="standalone" />
  <LedgerShell v-else />
  <ToastHost />
</template>
