<script setup lang="ts">
// Mini app qobig'i: pastki navigatsiya va global oynalar (yozuv, qarz, to'lov, sozlamalar, obuna).
// Faqat mini app sahifalarida yuklanadi — /obuna (to'lov sayti) ledger so'rovini yubormasligi uchun.
import { useSheets } from "@/composables/useSheets"
import { useUi } from "@/composables/useUi"
import BottomNav from "@/components/BottomNav.vue"
import DebtSheet from "@/features/debts/DebtSheet.vue"
import PaySheet from "@/features/debts/PaySheet.vue"
import MonthPickerSheet from "@/features/home/MonthPickerSheet.vue"
import PaywallScreen from "@/features/paywall/PaywallScreen.vue"
import RecordSheet from "@/features/records/RecordSheet.vue"
import SettingsSheet from "@/features/settings/SettingsSheet.vue"
import { useLedgerQuery } from "@/rest/queries/ledger.queries"

const { ui, closeSheet, closePaywall } = useUi()
const { state } = useLedgerQuery()
const sheets = useSheets()
</script>

<template>
  <BottomNav @add="sheets.newRecord('expense')" />

  <RecordSheet v-if="ui.sheet?.kind === 'record'" :key="ui.sheet.tx?.id ?? 'new'" :type="ui.sheet.type" :tx="ui.sheet.tx" @close="closeSheet" />
  <DebtSheet v-else-if="ui.sheet?.kind === 'debt'" :debt="ui.sheet.debt" @close="closeSheet" />
  <PaySheet v-else-if="ui.sheet?.kind === 'pay'" :debt="ui.sheet.debt" @close="closeSheet" />
  <SettingsSheet v-else-if="ui.sheet?.kind === 'settings'" @close="closeSheet" />
  <MonthPickerSheet v-else-if="ui.sheet?.kind === 'month'" @close="closeSheet" />

  <PaywallScreen v-if="ui.paywallOpen" :access="state.access" @close="closePaywall" />
</template>
