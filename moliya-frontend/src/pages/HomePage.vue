<script setup lang="ts">
import { computed } from "vue"
import { useMonth } from "@/composables/useMonth"
import QueryState from "@/components/QueryState.vue"
import BalanceCard from "@/features/home/BalanceCard.vue"
import HomeHeader from "@/features/home/HomeHeader.vue"
import QuickActions from "@/features/home/QuickActions.vue"
import RecentRecords from "@/features/home/RecentRecords.vue"

const RECENT_LIMIT = 5
const { query, state, list, sums, endBalance } = useMonth()
const recent = computed(() => list.value.slice(0, RECENT_LIMIT))
</script>

<template>
  <main class="page">
    <HomeHeader :account="state.account" />
    <QueryState :pending="query.isPending.value" :error="query.error.value" :has-data="!!query.data.value" @retry="query.refetch()">
      <BalanceCard :balance="endBalance" :sums="sums" :access="state.access" />
      <QuickActions />
      <RecentRecords :items="recent" />
    </QueryState>
  </main>
</template>
