<script setup lang="ts">
import { computed } from "vue"
import { ApiError } from "@/application/errors"
import { useLedgerState } from "@/application/ledger/queries"
import { useI18n } from "@/presentation/i18n"
import AppHeader from "./AppHeader.vue"
import PaywallModal from "./PaywallModal.vue"

const { query } = useLedgerState()
const { t } = useI18n()
const failed = computed(() => !!query.error.value && !query.data.value)
const unauthorized = computed(() => query.error.value instanceof ApiError && query.error.value.unauthorized)
</script>

<template>
  <div class="app">
    <AppHeader />
    <div v-if="query.isPending.value && !failed" class="state-box"><span class="spinner" aria-hidden="true"></span>{{ t("loading") }}</div>
    <div v-else-if="failed" class="state-box error">
      <p>{{ unauthorized ? t("not_in_telegram") : t("load_error") }}</p>
      <button v-if="!unauthorized" class="btn-primary" type="button" @click="query.refetch()">{{ t("retry") }}</button>
    </div>
    <RouterView v-else />
    <PaywallModal />
  </div>
</template>
