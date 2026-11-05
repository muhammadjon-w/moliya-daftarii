<script setup lang="ts">
// Bosh sahifa, Daromadlar, Chiqimlar: bir xil karkas, yon panel va ro'yxat filtri bilan farqlanadi.
import { computed } from "vue"
import { useRoute } from "vue-router"
import KpiBand from "../components/dashboard/KpiBand.vue"
import MonthBars from "../components/dashboard/MonthBars.vue"
import SidePanel from "../components/dashboard/SidePanel.vue"
import YearBanner from "../components/dashboard/YearBanner.vue"
import TransactionList from "../components/ledger/TransactionList.vue"

const route = useRoute()
const mode = computed(() => (route.meta.tab === "income" || route.meta.tab === "expense" ? route.meta.tab : "dash"))
</script>

<template>
  <section>
    <KpiBand />
    <div class="dash-row">
      <MonthBars />
      <SidePanel :mode="mode" />
    </div>
    <YearBanner v-if="mode === 'dash'" />
  </section>
  <TransactionList :mode="mode" />
</template>
