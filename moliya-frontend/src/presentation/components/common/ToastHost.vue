<script setup lang="ts">
import { storeToRefs } from "pinia"
import { useUiStore } from "@/application/session/ui"

const { toast } = storeToRefs(useUiStore())
</script>

<template>
  <Transition name="toast">
    <div v-if="toast" :key="toast.id" class="toast" :class="{ error: toast.error }" role="status" aria-live="polite">{{ toast.text }}</div>
  </Transition>
</template>
