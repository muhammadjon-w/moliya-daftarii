<script setup lang="ts">
import { computed } from "vue"
import { useRoute } from "vue-router"
import ToastHost from "@/components/ToastHost.vue"
import AppShell from "@/features/shell/AppShell.vue"

const route = useRoute()
const standalone = computed(() => !!route.meta.standalone)
</script>

<template>
  <RouterView />
  <AppShell v-if="!standalone" />
  <ToastHost />
</template>
