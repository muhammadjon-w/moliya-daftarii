<script setup lang="ts">
// Pul maydoni: yozayotganda 10 000 000 ko'rinishida guruhlanadi, kursor joyida qoladi.
import { ref, watch } from "vue"
import { formatInput, parseMoney, reformatTyping } from "@/domain/money"

const props = withDefaults(defineProps<{ modelValue: number; allowNegative?: boolean; placeholder?: string; zeroAsText?: boolean }>(), {
  allowNegative: false,
  placeholder: "",
  zeroAsText: false,
})
const emit = defineEmits<{ "update:modelValue": [number]; commit: [number] }>()

const show = (n: number) => formatInput(n) || (props.zeroAsText ? "0" : "")
const text = ref(show(props.modelValue))
const focused = ref(false)

watch(
  () => props.modelValue,
  (v) => {
    // Tashqaridan o'zgarsa (masalan, server javobi), foydalanuvchi yozmayotgan paytda yangilanadi
    if (!focused.value) text.value = show(v)
  },
)

function onInput(e: Event) {
  const el = e.target as HTMLInputElement
  const raw = el.value
  const caret = el.selectionStart ?? raw.length
  const before = raw.slice(0, caret).replace(/[^0-9.,-]/g, "").length
  const out = reformatTyping(raw, props.allowNegative)
  text.value = out
  if (out !== raw) {
    el.value = out
    let pos = 0
    let seen = 0
    while (pos < out.length && seen < before) {
      if (/[0-9,-]/.test(out[pos])) seen++
      pos++
    }
    try {
      el.setSelectionRange(pos, pos)
    } catch {
      /* type=text bo'lmasa */
    }
  }
  emit("update:modelValue", parseMoney(out))
}

function onBlur() {
  focused.value = false
  const n = parseMoney(text.value)
  text.value = show(Number.isFinite(n) ? n : props.modelValue)
}

function onChange() {
  emit("commit", parseMoney(text.value))
}
</script>

<template>
  <input
    class="money"
    type="text"
    inputmode="decimal"
    autocomplete="off"
    :value="text"
    :placeholder="placeholder"
    @focus="focused = true"
    @blur="onBlur"
    @input="onInput"
    @change="onChange"
  />
</template>
