<script setup lang="ts">
// Sozlamalar: til, dollar kursi, boshlang'ich qoldiq, obuna.
import { ref } from "vue"
import { useI18n } from "@/composables/useI18n"
import { useSheets } from "@/composables/useSheets"
import { useUi } from "@/composables/useUi"
import BaseSheet from "@/components/BaseSheet.vue"
import MoneyInput from "@/components/MoneyInput.vue"
import SegmentedControl from "@/components/SegmentedControl.vue"
import { LANGS } from "@/plugins/i18n"
import { useLedgerQuery } from "@/rest/queries/ledger.queries"
import { useUpdateSettings } from "@/rest/queries/ledger.mutations"
import type { Lang } from "@/types/ui"

const emit = defineEmits<{ close: [] }>()
const { ui, setLang, notify } = useUi()
const sheets = useSheets()
const { state } = useLedgerQuery()
const update = useUpdateSettings()
const { t } = useI18n()

const lang = ref<Lang>(ui.lang)
const langOptions = LANGS.map((l) => ({ value: l, label: l === "uz" ? "O'zbek" : l === "ru" ? "Русский" : "English" }))
const usdRate = ref(state.value.settings.usdRate)
const opening = ref(state.value.settings.openingBalance)

function save() {
  setLang(lang.value)
  const patch: { usdRate?: number; openingBalance?: number } = {}
  if (usdRate.value > 0 && usdRate.value !== state.value.settings.usdRate) patch.usdRate = usdRate.value
  const o = Number.isFinite(opening.value) ? opening.value : 0
  if (o !== state.value.settings.openingBalance) patch.openingBalance = o
  if (Object.keys(patch).length) update.mutate(patch, { onSuccess: () => notify(t("saved")) })
  emit("close")
}

const accessText = () => {
  const a = state.value.access
  return a.state === "expired" ? t("sub_state_expired") : t(a.state === "trial" ? "sub_state_trial" : "sub_state_active", { d: a.daysLeft })
}
</script>

<template>
  <BaseSheet :title="t('settings')" @close="emit('close')">
    <form id="settings-form" @submit.prevent="save">
      <div class="field">
        <span class="field__label">{{ t("language") }}</span>
        <SegmentedControl v-model="lang" :options="langOptions" :label="t('language')" />
      </div>
      <label class="field">
        <span class="field__label">{{ t("usd_rate") }}</span>
        <MoneyInput v-model="usdRate" class="input num" />
      </label>
      <label class="field">
        <span class="field__label">{{ t("opening") }}</span>
        <MoneyInput v-model="opening" class="input num" allow-negative zero-as-text />
        <span class="hint">{{ t("opening_hint") }}</span>
      </label>
      <div class="field sub">
        <div>
          <span class="field__label">{{ t("subscription") }}</span>
          <b>{{ accessText() }}</b>
        </div>
        <button class="btn btn--ghost" type="button" @click="sheets.paywall()">{{ t("extend") }}</button>
      </div>
    </form>
    <template #footer>
      <button class="btn btn--primary btn--block" type="submit" form="settings-form">{{ t("save") }}</button>
    </template>
  </BaseSheet>
</template>

<style scoped>
.hint {
  display: block;
  margin-top: 8px;
  color: var(--muted);
  font-size: 14px;
}

.sub {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 16px 18px;
  border-radius: var(--r-md);
  background: var(--surface);
}

.sub .field__label {
  margin-bottom: 4px;
}
</style>
