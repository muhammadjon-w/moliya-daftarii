<script setup lang="ts">
import { useUi } from "@/composables/useUi"

const { ui } = useUi()
</script>

<template>
  <Teleport to="body">
    <Transition name="toast">
      <div v-if="ui.toast" :key="ui.toast.id" class="toast" :class="{ 'toast--error': ui.toast.error }" role="status" aria-live="polite">
        {{ ui.toast.text }}
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.toast {
  position: fixed;
  left: 50%;
  top: calc(14px + env(safe-area-inset-top, 0px));
  z-index: 80;
  max-width: calc(100% - 32px);
  padding: 12px 18px;
  transform: translateX(-50%);
  background: var(--surface-3);
  border: 1px solid rgba(var(--tone-teal), 0.4);
  border-radius: var(--r-md);
  box-shadow: var(--shadow);
  font-weight: 500;
}

.toast--error {
  border-color: rgba(var(--tone-red), 0.5);
  color: var(--red);
}

.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.2s, transform 0.2s;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translate(-50%, -10px);
}
</style>
