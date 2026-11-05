<script setup lang="ts">
// Pastki oyna (bottom sheet): fon bosilsa yoki Esc — yopiladi. Kontent slot orqali, pastki tugmalar #footer slotida.
import { nextTick, onBeforeUnmount, onMounted, ref } from "vue"
import { useI18n } from "@/composables/useI18n"
import AppIcon from "./AppIcon.vue"

const props = withDefaults(defineProps<{ title: string; full?: boolean; autofocus?: string }>(), { full: false, autofocus: "" })
const emit = defineEmits<{ close: [] }>()
const { t } = useI18n()
const panel = ref<HTMLElement | null>(null)

function onKey(e: KeyboardEvent) {
  if (e.key === "Escape") emit("close")
}
onMounted(async () => {
  document.addEventListener("keydown", onKey)
  document.body.style.overflow = "hidden"
  await nextTick()
  const el = props.autofocus ? panel.value?.querySelector<HTMLElement>(props.autofocus) : null
  el?.focus()
})
onBeforeUnmount(() => {
  document.removeEventListener("keydown", onKey)
  document.body.style.overflow = ""
})
</script>

<template>
  <Teleport to="body">
    <div class="backdrop" @click.self="emit('close')">
      <section ref="panel" class="sheet" :class="{ 'sheet--full': full }" role="dialog" aria-modal="true" :aria-label="title">
        <div class="sheet__handle" aria-hidden="true"></div>
        <header class="sheet__head">
          <h2>{{ title }}</h2>
          <button class="sheet__close" type="button" :aria-label="t('close')" @click="emit('close')"><AppIcon name="x" :size="22" /></button>
        </header>
        <div class="sheet__body">
          <slot />
        </div>
        <footer v-if="$slots.footer" class="sheet__foot">
          <slot name="footer" />
        </footer>
      </section>
    </div>
  </Teleport>
</template>

<style scoped>
.backdrop {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  background: rgba(3, 7, 15, 0.62);
  animation: fade 0.18s ease-out;
}

.sheet {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 560px;
  max-height: 92vh;
  background: var(--bg);
  border: 1px solid var(--border-strong);
  border-bottom: 0;
  border-radius: 32px 32px 0 0;
  box-shadow: var(--shadow);
  animation: rise 0.24s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.sheet--full {
  height: 92vh;
}

.sheet__handle {
  width: 40px;
  height: 5px;
  margin: 10px auto 0;
  border-radius: var(--r-pill);
  background: var(--border-strong);
}

.sheet__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 20px 6px;
}

.sheet__head h2 {
  font-size: 26px;
  font-weight: 600;
}

.sheet__close {
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--surface-2);
  color: var(--text-2);
}

.sheet__body {
  flex: 1;
  overflow-y: auto;
  padding: 8px 20px 20px;
  overscroll-behavior: contain;
}

.sheet__foot {
  display: flex;
  gap: 10px;
  padding: 12px 20px calc(16px + var(--safe-bottom));
  border-top: 1px solid var(--border);
}

@keyframes fade {
  from {
    opacity: 0;
  }
}

@keyframes rise {
  from {
    transform: translateY(40px);
    opacity: 0;
  }
}
</style>
