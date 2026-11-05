<script setup lang="ts">
// Bo'limlar: faol bo'lim ostidagi shisha "glider" bo'limlar orasida oqib o'tadi.
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue"
import { useRoute } from "vue-router"
import type { TabName } from "@/app/router"
import { useI18n } from "@/presentation/i18n"

const TABS: { name: TabName; path: string; label: string }[] = [
  { name: "dash", path: "/", label: "tab_dash" },
  { name: "income", path: "/income", label: "tab_income" },
  { name: "expense", path: "/expense", label: "tab_expense" },
  { name: "plan", path: "/plan", label: "tab_plan" },
  { name: "year", path: "/year", label: "tab_year" },
  { name: "debts", path: "/debts", label: "tab_debts" },
  { name: "report", path: "/report", label: "tab_report" },
]

const route = useRoute()
const { t, lang } = useI18n()
const nav = ref<HTMLElement | null>(null)
const glider = ref({ left: 0, top: 0, width: 0, height: 0, visible: false })

function place() {
  const a = nav.value?.querySelector<HTMLElement>(".tab-btn.active")
  if (!a || !a.offsetWidth) {
    glider.value.visible = false
    return
  }
  glider.value = { left: a.offsetLeft, top: a.offsetTop, width: a.offsetWidth, height: a.offsetHeight, visible: true }
  a.scrollIntoView?.({ block: "nearest", inline: "nearest", behavior: "smooth" })
}

watch([() => route.meta.tab, lang], () => nextTick(place))
onMounted(() => {
  place()
  window.addEventListener("resize", place)
  document.fonts?.ready.then(place).catch(() => undefined)
})
onBeforeUnmount(() => window.removeEventListener("resize", place))
</script>

<template>
  <nav ref="nav" class="tab-nav has-glider">
    <span
      class="tab-glider"
      aria-hidden="true"
      :style="{ left: glider.left + 'px', top: glider.top + 'px', width: glider.width + 'px', height: glider.height + 'px', opacity: glider.visible ? 1 : 0 }"
    ></span>
    <RouterLink v-for="tab in TABS" :key="tab.name" :to="tab.path" class="tab-btn" :class="{ active: route.meta.tab === tab.name }">
      {{ t(tab.label) }}
    </RouterLink>
  </nav>
</template>
