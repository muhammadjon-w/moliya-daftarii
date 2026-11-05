<script setup lang="ts">
// Pastki navigatsiya: 4 ta bo'lim va o'rtada "+" (yangi yozuv).
import { useRoute } from "vue-router"
import { useI18n } from "@/composables/useI18n"
import type { IconName } from "@/constants/icons"
import { ROUTES, type RouteName } from "@/constants/routes"
import type { MessageKey } from "@/plugins/i18n"
import AppIcon from "./AppIcon.vue"

const emit = defineEmits<{ add: [] }>()
const route = useRoute()
const { t } = useI18n()

const LEFT: { name: RouteName; icon: IconName; label: MessageKey }[] = [
  { name: ROUTES.home, icon: "home", label: "nav_home" },
  { name: ROUTES.records, icon: "list", label: "nav_records" },
]
const RIGHT: { name: RouteName; icon: IconName; label: MessageKey }[] = [
  { name: ROUTES.report, icon: "chart", label: "nav_report" },
  { name: ROUTES.debts, icon: "card", label: "nav_debts" },
]
</script>

<template>
  <nav class="nav" :aria-label="t('app_title')">
    <RouterLink v-for="i in LEFT" :key="i.name" :to="{ name: i.name }" class="nav__item" :class="{ 'nav__item--on': route.name === i.name }">
      <AppIcon :name="i.icon" :size="26" :stroke="1.8" />
      <span>{{ t(i.label) }}</span>
    </RouterLink>
    <span class="nav__spacer"></span>
    <RouterLink v-for="i in RIGHT" :key="i.name" :to="{ name: i.name }" class="nav__item" :class="{ 'nav__item--on': route.name === i.name }">
      <AppIcon :name="i.icon" :size="26" :stroke="1.8" />
      <span>{{ t(i.label) }}</span>
    </RouterLink>
    <button class="nav__fab" type="button" :aria-label="t('nav_add')" @click="emit('add')">
      <AppIcon name="plus" :size="34" :stroke="2.4" />
    </button>
  </nav>
</template>

<style scoped>
.nav {
  position: fixed;
  left: 50%;
  bottom: calc(14px + var(--safe-bottom));
  z-index: 40;
  display: flex;
  align-items: center;
  width: calc(100% - 2 * var(--gutter));
  max-width: 528px;
  height: var(--nav-h);
  padding: 0 8px;
  transform: translateX(-50%);
  background: rgba(19, 29, 51, 0.92);
  border: 1px solid var(--border-strong);
  border-radius: 34px;
  box-shadow: var(--shadow);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
}

.nav__item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: var(--muted);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
}

.nav__item--on {
  color: var(--teal);
}

.nav__spacer {
  flex: 0.9;
}

.nav__fab {
  position: absolute;
  left: 50%;
  top: -22px;
  display: grid;
  place-items: center;
  width: 76px;
  height: 76px;
  transform: translateX(-50%);
  border-radius: 50%;
  background: var(--teal);
  color: var(--teal-ink);
  box-shadow: var(--glow-teal);
  transition: transform 0.15s;
}

.nav__fab:active {
  transform: translateX(-50%) scale(0.94);
}
</style>
