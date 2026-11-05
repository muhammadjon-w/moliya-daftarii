<script setup lang="ts">
// Toifa plitkalari: 7 ta tez tanlov + "Boshqa". Katalogdan boshqa modda tanlangan bo'lsa "Boshqa" o'rnida ko'rinadi.
import { computed } from "vue"
import { useI18n } from "@/composables/useI18n"
import AppIcon from "@/components/AppIcon.vue"
import { QUICK_ITEMS, lookOf } from "@/constants/categoryStyle"
import { ITEM_BY_ID } from "@/constants/catalog"
import type { TxType } from "@/types/ledger"

const props = defineProps<{ type: TxType; modelValue: string }>()
const emit = defineEmits<{ "update:modelValue": [string]; more: [] }>()
const { t, tileLabel, itemLabel } = useI18n()

const tiles = computed(() =>
  QUICK_ITEMS[props.type].map((id) => {
    const it = ITEM_BY_ID[id]
    return { id, label: tileLabel(id), ...lookOf(id, it.category, it.group) }
  }),
)
const custom = computed(() => {
  const id = props.modelValue
  if (!id || QUICK_ITEMS[props.type].includes(id)) return null
  const it = ITEM_BY_ID[id]
  return { id, label: itemLabel(id), ...lookOf(id, it?.category ?? "", it?.group ?? (props.type === "income" ? "inc" : "exp")) }
})
</script>

<template>
  <div class="grid" role="radiogroup" :aria-label="t('category')">
    <button
      v-for="tile in tiles"
      :key="tile.id"
      type="button"
      role="radio"
      class="cat"
      :class="{ 'cat--on': modelValue === tile.id }"
      :style="{ '--rgb': `var(--tone-${tile.tone})` }"
      :aria-checked="modelValue === tile.id"
      @click="emit('update:modelValue', tile.id)"
    >
      <AppIcon :name="tile.icon" :size="26" :stroke="1.8" />
      <span>{{ tile.label }}</span>
    </button>
    <button
      v-if="custom"
      type="button"
      role="radio"
      class="cat cat--on"
      :style="{ '--rgb': `var(--tone-${custom.tone})` }"
      aria-checked="true"
      @click="emit('more')"
    >
      <AppIcon :name="custom.icon" :size="26" :stroke="1.8" />
      <span>{{ custom.label }}</span>
    </button>
    <button v-else type="button" class="cat cat--more" @click="emit('more')">
      <AppIcon name="plus" :size="26" :stroke="1.8" />
      <span>{{ t("other") }}</span>
    </button>
  </div>
</template>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}

.cat {
  display: grid;
  justify-items: center;
  align-content: center;
  gap: 10px;
  min-height: 112px;
  padding: 10px 4px;
  border-radius: var(--r-lg);
  background: var(--surface);
  border: 1px solid var(--border-strong);
  color: var(--text-2);
}

.cat span {
  overflow: hidden;
  max-width: 100%;
  color: var(--text);
  font-size: 15px;
  font-weight: 500;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.cat--on {
  background: rgba(var(--rgb), 0.12);
  border-color: rgb(var(--rgb));
  color: rgb(var(--rgb));
}

.cat--on span {
  color: rgb(var(--rgb));
}

.cat--more {
  border-style: dashed;
  background: transparent;
  color: var(--muted);
}

.cat--more span {
  color: var(--muted);
}

@media (max-width: 380px) {
  .cat {
    min-height: 96px;
  }

  .cat span {
    font-size: 13px;
  }
}
</style>
