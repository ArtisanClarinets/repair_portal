<template>
  <section aria-labelledby="service-heading" class="wizard-section">
    <header class="section-header">
      <div>
        <h2 id="service-heading">Service Intake</h2>
        <p class="section-hint">
          Outline the service scope, capture condition observations, and coordinate any loaner commitments.
        </p>
      </div>
      <div class="status-cluster" aria-live="polite">
        <span class="status-pill" :class="statusClass">{{ statusMessage }}</span>
      </div>
    </header>

    <div class="content-grid">
      <article class="card">
        <h3>Intake Type &amp; Commercials</h3>
        <div class="field-grid">
          <label>
            <span>Intake Type</span>
            <select v-model="local.intakeType" @change="handleIntakeTypeChange">
              <option>Repair</option>
              <option>Maintenance</option>
              <option>New Inventory</option>
            </select>
          </label>
          <label v-if="local.intakeType === 'New Inventory'">
            <span>Acquisition Cost</span>
            <input v-model.number="local.acquisition_cost" type="number" min="0" step="0.01" @input="update" />
          </label>
          <label v-if="local.intakeType === 'New Inventory'">
            <span>Store Asking Price</span>
            <input v-model.number="local.store_asking_price" type="number" min="0" step="0.01" @input="update" />
          </label>
        </div>
        <p class="callout" v-if="local.intakeType !== 'New Inventory'">
          <strong>Tip:</strong> Use the issue description to document how the instrument currently feels to the player
          (response,
          tuning, resistance).
        </p>
      </article>

      <article class="card">
        <h3>Condition Details</h3>
        <label :class="{ 'has-error': errors.issue_description }">
          <span>Issue Description</span>
          <textarea v-model.trim="local.issue_description" rows="3" @input="update"></textarea>
          <p v-if="errors.issue_description" class="field-error">{{ errors.issue_description }}</p>
        </label>
        <label>
          <span>Condition Notes</span>
          <textarea v-model.trim="local.condition_notes" rows="3" @input="update"></textarea>
        </label>
        <div class="char-count">{{ local.issue_description?.length || 0 }}/500 characters</div>
      </article>
    </div>

    <article class="card loaner-card">
      <header class="loaner-header">
        <div>
          <h3>Loaner Planning</h3>
          <p class="section-hint">Secure an available loaner if the client needs a temporary instrument.</p>
        </div>
        <label class="checkbox">
          <input type="checkbox" v-model="local.loanerRequired" @change="toggleLoaner" />
          Loaner instrument required
        </label>
      </header>

      <transition name="fade">
        <div v-if="local.loanerRequired" class="loaner-body">
          <div class="loaner-toolbar">
            <button type="button" class="secondary" @click="fetchAvailableLoaners" :disabled="loading">Refresh
              List</button>
            <span class="loaner-count" aria-live="polite">{{ loaners.length }} loaners available</span>
          </div>
          <label>
            <span>Select Loaner</span>
            <select v-model="local.loanerInstrument" @change="update">
              <option value="">Choose loaner</option>
              <option v-for="row in loaners" :key="row.loaner" :value="row.loaner">
                {{ row.loaner }} — {{ row.instrument_details.manufacturer || 'Unknown' }} {{
                  row.instrument_details.model || '' }}
              </option>
            </select>
          </label>
          <div v-if="selectedLoaner" class="loaner-preview">
            <h4>{{ selectedLoaner.loaner }}</h4>
            <p>
              {{ selectedLoaner.instrument_details.manufacturer || '—' }}
              {{ selectedLoaner.instrument_details.model || '' }} · Serial {{
                selectedLoaner.instrument_details.serial_no || '—' }}
            </p>
          </div>
          <div class="loaner-agreement">
            <h4>Loaner Agreement</h4>
            <p class="section-hint">
              Capture borrower and staff approvals. Signatures are stored as secure image data and surfaced on the
              agreement PDF.
            </p>
            <label class="checkbox">
              <input type="checkbox" v-model="local.loanerAgreement.terms_ack" @change="update" /> Borrower agrees to
              terms
            </label>
            <div :class="['signature-field', { 'has-error': signatureErrors.borrower || errors.borrower_signature }]">
              <SignaturePad v-model="local.loanerAgreement.borrower_signature" label="Borrower Signature"
                :max-bytes="MAX_SIGNATURE_BYTES" @update:modelValue="setSignature('borrower_signature', $event)"
                @invalid="handleSignatureError('borrower', $event)" />
              <p v-if="signatureErrors.borrower" class="field-error">{{ signatureErrors.borrower }}</p>
              <p v-else-if="errors.borrower_signature" class="field-error">{{ errors.borrower_signature }}</p>
            </div>
            <div :class="['signature-field', { 'has-error': signatureErrors.staff || errors.staff_signature }]">
              <SignaturePad v-model="local.loanerAgreement.staff_signature" label="Staff Signature"
                :max-bytes="MAX_SIGNATURE_BYTES" @update:modelValue="setSignature('staff_signature', $event)"
                @invalid="handleSignatureError('staff', $event)" />
              <p v-if="signatureErrors.staff" class="field-error">{{ signatureErrors.staff }}</p>
              <p v-else-if="errors.staff_signature" class="field-error">{{ errors.staff_signature }}</p>
            </div>
          </div>
        </div>
      </transition>
    </article>
  </section>
</template>

<script setup>
import { computed, reactive, watch } from "vue";

import SignaturePad from "../components/SignaturePad.vue";

const props = defineProps({
  modelValue: { type: Object, default: () => ({ loanerRequired: false }) },
  fetchLoaners: { type: Function, required: true },
  loaners: { type: Array, default: () => [] },
});

const emit = defineEmits(["update:modelValue", "validity-change", "log"]);

const local = reactive({
  intakeType: "Repair",
  acquisition_cost: 0,
  store_asking_price: 0,
  issue_description: "",
  condition_notes: "",
  loanerRequired: false,
  loanerInstrument: "",
  loanerAgreement: {
    terms_ack: false,
    borrower_signature: "",
    staff_signature: "",
    linked_loaner: "",
  },
});

const errors = reactive({ issue_description: null, borrower_signature: null, staff_signature: null });
const signatureErrors = reactive({ borrower: null, staff: null });
const loading = computed(() => props.loaners.length === 0 && local.loanerRequired);

const loaners = computed(() => props.loaners || []);

const selectedLoaner = computed(() => loaners.value.find((row) => row.loaner === local.loanerInstrument));

const statusMessage = computed(() => {
  if (local.loanerRequired) {
    return local.loanerInstrument ? `Loaner reserved (${local.loanerInstrument})` : "Loaner pending";
  }
  return `${local.intakeType} intake`;
});

const statusClass = computed(() => {
  if (local.loanerRequired && local.loanerInstrument && local.loanerAgreement.terms_ack) {
    return "status-pill--success";
  }
  if (local.loanerRequired) {
    return "status-pill--warning";
  }
  return "status-pill--neutral";
});

const MAX_SIGNATURE_BYTES = 180 * 1024;

watch(
  () => props.modelValue,
  (value) => {
    Object.assign(local, { ...local, ...value });
    if (!local.loanerAgreement) {
      local.loanerAgreement = { terms_ack: false, borrower_signature: "", staff_signature: "", linked_loaner: "" };
    }
    if (!local.loanerAgreement.borrower_signature) {
      signatureErrors.borrower = null;
    }
    if (!local.loanerAgreement.staff_signature) {
      signatureErrors.staff = null;
    }
    validate(false);
  },
  { immediate: true, deep: true }
);

watch(
  () => props.loaners,
  () => {
    if (local.loanerRequired && !loaners.value.length) {
      fetchAvailableLoaners();
    }
  },
  { immediate: true }
);

function update() {
  if (local.loanerAgreement) {
    local.loanerAgreement.linked_loaner = local.loanerInstrument || "";
  }
  emit("update:modelValue", { ...local, intakeDetails: buildIntakeDetails(), loanerAgreement: local.loanerAgreement });
  validate(false);
}

function setSignature(field, value) {
  if (!local.loanerAgreement) {
    return;
  }
  local.loanerAgreement[field] = value || "";
  update();
}

function handleSignatureError(type, message) {
  signatureErrors[type] = message;
}

function buildIntakeDetails() {
  return {
    intake_type: local.intakeType,
    acquisition_cost: local.acquisition_cost,
    store_asking_price: local.store_asking_price,
    issue_description: local.issue_description,
    condition_notes: local.condition_notes,
  };
}

async function fetchAvailableLoaners() {
  const rows = await props.fetchLoaners({});
  emit("log", { type: "loaner_refresh", count: rows.length });
}

function toggleLoaner() {
  if (local.loanerRequired) {
    fetchAvailableLoaners();
  } else {
    local.loanerInstrument = "";
    local.loanerAgreement = { terms_ack: false, borrower_signature: "", staff_signature: "", linked_loaner: "" };
    signatureErrors.borrower = null;
    signatureErrors.staff = null;
  }
  update();
}

function handleIntakeTypeChange() {
  if (local.intakeType !== "New Inventory") {
    local.acquisition_cost = 0;
    local.store_asking_price = 0;
  }
  update();
}

function clearErrors() {
  Object.keys(errors).forEach((key) => {
    errors[key] = null;
  });
}

function validate(show = true) {
  clearErrors();
  let valid = true;
  if (local.intakeType !== "New Inventory") {
    if (!local.issue_description) {
      errors.issue_description = "Describe the reported issue.";
      valid = false;
    }
  }
  if (local.loanerRequired) {
    if (!local.loanerInstrument) {
      valid = false;
    }
    if (!local.loanerAgreement.terms_ack) {
      valid = false;
    }
    if (!local.loanerAgreement.borrower_signature) {
      errors.borrower_signature = "Borrower signature required.";
      valid = false;
    }
    if (!local.loanerAgreement.staff_signature) {
      errors.staff_signature = "Staff signature required.";
      valid = false;
    }
    if (signatureErrors.borrower) {
      valid = false;
    }
    if (signatureErrors.staff) {
      valid = false;
    }
  }
  if (show) {
    emit("validity-change", valid);
  } else {
    emit("validity-change", valid);
  }
  return valid;
}
</script>

<style scoped>
/* --- Core Section & Card Styles --- */
.wizard-section {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1.5rem;
}

.section-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--text);
}

.section-hint {
  margin: 0.25rem 0 0;
  color: var(--muted);
  max-width: 620px;
}

.status-cluster {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.card {
  background-color: var(--card-bg);
  border-radius: 0.75rem;
  border: 1px solid var(--border);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.card h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text);
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.field-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.25rem;
}

/* --- Status Pill Styles --- */
.status-pill {
  border-radius: 999px;
  padding: 0.375rem 0.875rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.status-pill--success {
  background-color: var(--success-surface);
  color: var(--success);
}

.status-pill--warning {
  background-color: var(--warning-surface);
  color: var(--warning);
}

.status-pill--neutral {
  background-color: color-mix(in srgb, var(--primary) 8%, var(--surface));
  color: var(--primary-600);
}

/* --- Form Element Styles --- */
label {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  font-weight: 500;
  font-size: 0.875rem;
  color: color-mix(in srgb, var(--text) 92%, var(--muted));
}

input,
select,
textarea {
  padding: 0.65rem 0.875rem;
  border-radius: 0.5rem;
  border: 1px solid var(--border);
  background-color: var(--card-bg);
  font-size: 1rem;
  color: var(--text);
}

input:focus-visible,
select:focus-visible,
textarea:focus-visible {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--focus);
}

textarea {
  resize: vertical;
  min-height: 80px;
}

.field-error {
  margin: 0;
  font-size: 0.875rem;
  color: var(--danger);
}

.has-error input,
.has-error textarea {
  border-color: color-mix(in srgb, var(--danger) 40%, var(--border));
}

/* --- Special Components --- */
.callout {
  background-color: color-mix(in srgb, var(--primary) 8%, var(--surface));
  color: var(--primary-600);
  padding: 1rem;
  border-radius: 0.5rem;
  border: 1px solid color-mix(in srgb, var(--primary) 20%, var(--border));
  margin: 0;
}

.char-count {
  font-size: 0.875rem;
  color: var(--muted);
  text-align: right;
}

.checkbox {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 500;
}

/* --- Loaner Section --- */
.loaner-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.loaner-body {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border);
  max-width: 100%;
}

.loaner-toolbar {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.loaner-count {
  font-size: 0.875rem;
  color: var(--muted);
}

.loaner-preview {
  background-color: var(--bg);
  border-radius: 0.5rem;
  padding: 1rem;
  color: color-mix(in srgb, var(--text) 80%, var(--muted));
  border: 1px solid var(--border);
  word-break: break-word;
}

.loaner-agreement {
  display: grid;
  gap: 1.25rem;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  align-items: start;
  max-width: 100%;
}

.loaner-agreement>* {
  min-width: 0;
}

.signature-field {
  min-width: 0;
}

.signature-field :deep(.signature-pad) {
  width: 100%;
}

.signature-field :deep(.pad-wrapper) {
  width: 100%;
  max-width: 100%;
}

.signature-field :deep(canvas) {
  width: 100% !important;
}

.signature-field.has-error :deep(.pad-wrapper) {
  border-color: color-mix(in srgb, var(--danger) 40%, var(--border));
  box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.2);
}

/* --- Shared Button Styles --- */
.secondary {
  border: 1px solid var(--border);
  padding: 0.65rem 1rem;
  border-radius: 0.5rem;
  background-color: var(--card-bg);
  cursor: pointer;
  font-weight: 600;
  color: var(--text);
}

/* --- Transitions --- */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
