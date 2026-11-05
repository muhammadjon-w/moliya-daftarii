<script setup lang="ts">
// "Boshqa": katalogdagi barcha moddalar guruh va toifa bo'yicha, qidiruv bilan.
import { computed, ref } from "vue"
import { useI18n } from "@/composables/useI18n"
import AppIcon from "@/components/AppIcon.vue"
import IconTile from "@/components/IconTile.vue"
import { lookOf } from "@/constants/categoryStyle"
import { EXPENSE_GROUPS, ITEMS } from "@/constants/catalog"
import type { Group, TxType } from "@/types/ledger"

const props = defineProps<{ type: TxType; modelValue: string }>()
const emit = defineEmits<{ "update:modelValue": [string]; back: [] }>()
const { t, itemLabel, groupLabel } = useI18n()
const q = ref("")

const sections = computed(() => {
  const groups: Group[] = props.type === "income" ? ["inc"] : [...EXPENSE_GROUPS]
  const needle = q.value.trim().toLowerCase()
  return groups
    .map((g) => ({
      group: g,
      items: ITEMS.filter((i) => i.group === g && (!needle || itemLabel(i.id).toLowerCase().includes(needle))).map((i) => ({ id: i.id, ...lookOf(i.id, i.category, i.group) })),
    }))
    .filter((s) => s.items.length)
})

function pick(id: string) {
  emit("update:modelValue", id)
  emit("back")
}
</script>

<template>
  <div>
    <div class="cl__top">
      <button class="cl__back" type="button" :aria-label="t('back')" @click="emit('back')"><AppIcon name="chevronLeft" /></button>
      <label class="cl__search">
        <AppIcon name="search" :size="20" />
        <input v-model="q" class="sr-input" type="search" :placeholder="t('all_categories')" :aria-label="t('all_categories')" />
      </label>
    </div>
    <section v-for="s in sections" :key="s.group" class="cl__sec">
      <h3>{{ groupLabel(s.group) }}</h3>
      <button v-for="i in s.items" :key="i.id" type="button" class="cl__item" :class="{ 'cl__item--on': modelValue === i.id }" @click="pick(i.id)">
        <IconTile :icon="i.icon" :tone="i.tone" :size="40" :icon-size="20" />
        <span>{{ itemLabel(i.id) }}</span>
        <AppIcon v-if="modelValue === i.id" name="check" :size="20" class="positive" />
      </button>
    </section>
  </div>
</template>

<style scoped>
.cl__top {
  position: sticky;
  top: -8px;
  z-index: 1;
  display: flex;
  gap: 10px;
  padding: 4px 0 12px;
  background: var(--bg);
}

.cl__back {
  display: grid;
  place-items: center;
  flex: none;
  width: 50px;
  height: 50px;
  border-radius: var(--r-md);
  background: var(--surface-2);
}

.cl__search {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  padding: 0 14px;
  border-radius: var(--r-md);
  background: var(--surface-2);
  border: 1px solid var(--border);
  color: var(--muted);
}

.sr-input {
  flex: 1;
  min-width: 0;
  height: 48px;
  border: 0;
  outline: none;
  background: transparent;
  color: var(--text);
  font-size: 17px;
}

.cl__sec h3 {
  margin: 14px 4px 8px;
  color: var(--muted);
  font-size: 14px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.cl__item {
  display: flex;
  align-items: center;
  gap: 14px;
  width: 100%;
  padding: 10px 6px;
  border-radius: var(--r-md);
  text-align: left;
  font-size: 17px;
}

.cl__item span {
  flex: 1;
}

.cl__item--on {
  background: var(--surface);
}
</style>
