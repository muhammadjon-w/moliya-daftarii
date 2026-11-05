<script setup lang="ts">
// Umumiy oyna: fon bosilsa yoki Esc bosilsa yopiladi. Ichidagi forma submit bo'lsa "submit" chiqadi.
import { nextTick, onBeforeUnmount, onMounted, ref } from "vue"

const props = withDefaults(defineProps<{ title: string; form?: boolean; autofocus?: string }>(), { form: true, autofocus: "" })
const emit = defineEmits<{ close: []; submit: [] }>()
const root = ref<HTMLElement | null>(null)

function onKey(e: KeyboardEvent) {
  if (e.key === "Escape") emit("close")
}
onMounted(async () => {
  document.addEventListener("keydown", onKey)
  await nextTick()
  const el = props.autofocus ? root.value?.querySelector<HTMLElement>(props.autofocus) : null
  el?.focus()
})
onBeforeUnmount(() => document.removeEventListener("keydown", onKey))
</script>

<template>
  <Teleport to="body">
    <div class="modal-backdrop" @click.self="emit('close')">
      <component :is="form ? 'form' : 'div'" ref="root" class="modal" novalidate role="dialog" aria-modal="true" :aria-label="title" @submit.prevent="emit('submit')">
        <div class="modal-head">
          <h2>{{ title }}</h2>
          <button class="modal-x" type="button" aria-label="×" @click="emit('close')">×</button>
        </div>
        <slot />
      </component>
    </div>
  </Teleport>
</template>
