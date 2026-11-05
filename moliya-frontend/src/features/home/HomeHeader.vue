<script setup lang="ts">
// "Xayrli kech, Muhammadjon" · oy tanlash · avatar (sozlamalar).
import { computed } from "vue"
import { useI18n } from "@/composables/useI18n"
import { useSheets } from "@/composables/useSheets"
import { useTelegram } from "@/composables/useTelegram"
import { useUi } from "@/composables/useUi"
import AppIcon from "@/components/AppIcon.vue"
import type { Account } from "@/types/account"
import { initials } from "@/utils/money"

const props = defineProps<{ account: Account | null }>()
const { ui } = useUi()
const sheets = useSheets()
const tg = useTelegram()
const { t, greeting, periodLabel } = useI18n()

const name = computed(() => props.account?.firstName || tg.firstName || "")
</script>

<template>
  <header class="hh">
    <div class="hh__hello">
      <span class="hh__greet">{{ greeting() }}{{ name ? "," : "" }}</span>
      <h1 v-if="name" class="hh__name">{{ name }}</h1>
    </div>
    <button class="hh__month" type="button" :aria-label="t('pick_month')" @click="sheets.monthPicker()">
      {{ periodLabel(ui.period) }}
      <AppIcon name="chevronDown" :size="18" />
    </button>
    <button class="hh__avatar" type="button" :aria-label="t('settings')" @click="sheets.settings()">{{ initials(name || "?").charAt(0) }}</button>
  </header>
</template>

<style scoped>
.hh {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 22px;
}

.hh__hello {
  flex: 1;
  min-width: 0;
}

.hh__greet {
  color: var(--text-2);
  font-size: 18px;
}

.hh__name {
  overflow: hidden;
  font-size: 30px;
  font-weight: 600;
  line-height: 1.15;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.hh__month {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  flex: none;
  height: 52px;
  padding: 0 18px;
  border-radius: var(--r-pill);
  background: var(--surface-2);
  border: 1px solid var(--border-strong);
  font-size: 18px;
  font-weight: 500;
}

.hh__avatar {
  display: grid;
  place-items: center;
  flex: none;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--avatar);
  font-size: 22px;
  font-weight: 600;
}

@media (max-width: 380px) {
  .hh__month {
    padding: 0 12px;
    font-size: 16px;
  }
}
</style>
