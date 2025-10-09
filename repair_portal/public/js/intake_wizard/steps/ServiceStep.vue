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
          <strong>Tip:</strong> Use the issue description to document how the instrument currently feels to the player (response,
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
            <button type="button" class="secondary" @click="fetchAvailableLoaners" :disabled="loading">Refresh List</button>
            <span class="loaner-count" aria-live="polite">{{ loaners.length }} loaners available</span>
          </div>
          <label>
            <span>Select Loaner</span>
            <select v-model="local.loanerInstrument" @change="update">
              <option value="">Choose loaner</option>
              <option v-for="row in loaners" :key="row.loaner" :value="row.loaner">
                {{ row.loaner }} — {{ row.instrument_details.manufacturer || 'Unknown' }} {{ row.instrument_details.model || '' }}
              </option>
            </select>
          </label>
          <div v-if="selectedLoaner" class="loaner-preview">
            <h4>{{ selectedLoaner.loaner }}</h4>
            <p>
              {{ selectedLoaner.instrument_details.manufacturer || '—' }}
              {{ selectedLoaner.instrument_details.model || '' }} · Serial {{ selectedLoaner.instrument_details.serial_no || '—' }}
            </p>
          </div>
          <div class="loaner-agreement">
            <h4>Loaner Agreement</h4>
            <label class="checkbox">
              <input type="checkbox" v-model="local.loanerAgreement.terms_ack" @change="update" /> Borrower agrees to terms
            </label>
            <label :class="{ 'has-error': errors.borrower_signature }">
              <span>Borrower Signature (data URL)</span>
              <input v-model.trim="local.loanerAgreement.borrower_signature" type="text" @input="update" />
              <p v-if="errors.borrower_signature" class="field-error">{{ errors.borrower_signature }}</p>
            </label>
            <label :class="{ 'has-error': errors.staff_signature }">
              <span>Staff Signature (data URL)</span>
              <input v-model.trim="local.loanerAgreement.staff_signature" type="text" @input="update" />
              <p v-if="errors.staff_signature" class="field-error">{{ errors.staff_signature }}</p>
            </label>
          </div>
        </div>
      </transition>
    </article>
  </section>
</template>

<script setup>
import { computed, reactive, watch } from "vue";

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

watch(
  () => props.modelValue,
  (value) => {
    Object.assign(local, { ...local, ...value });
    if (!local.loanerAgreement) {
      local.loanerAgreement = { terms_ack: false, borrower_signature: "", staff_signature: "", linked_loaner: "" };
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
.wizard-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.section-hint {
  margin: 0.25rem 0 0;
  color: #64748b;
  max-width: 620px;
}

.status-cluster {
  display: flex;
  gap: 0.5rem;
}

.status-pill {
  border-radius: 999px;
  padding: 0.35rem 0.75rem;
  font-size: 0.8rem;
  font-weight: 600;
  background: #e2e8f0;
  color: #475569;
}

.status-pill--success {
  background: #dcfce7;
  color: #166534;
}

.status-pill--warning {
  background: #fef3c7;
  color: #92400e;
}

.status-pill--neutral {
  background: #e0f2fe;
  color: #0369a1;
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.25rem;
}

.card {
  background: #f8fafc;
  border-radius: 1rem;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.card h3 {
  margin: 0;
  font-size: 1rem;
}

.field-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}

label {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  font-weight: 600;
  font-size: 0.85rem;
}

input,
select,
textarea {
  padding: 0.6rem 0.85rem;
  border-radius: 0.75rem;
  border: 1px solid #cbd5f5;
  font-size: 0.95rem;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

textarea {
  resize: vertical;
}

input:focus-visible,
select:focus-visible,
textarea:focus-visible {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2);
}

.field-error {
  margin: 0;
  font-size: 0.8rem;
  color: #b91c1c;
}

.has-error input,
.has-error textarea {
  border-color: #f87171;
}

.callout {
  background: #fff7ed;
  padding: 0.75rem 1rem;
  border-radius: 0.75rem;
  margin: 0;
  color: #7c2d12;
}

.char-count {
  font-size: 0.8rem;
  color: #94a3b8;
  text-align: right;
}

.loaner-card {
  background: #fff;
}

.loaner-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.checkbox {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 600;
}

.loaner-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.loaner-toolbar {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.secondary {
  border: 1px solid #cbd5f5;
  padding: 0.5rem 1rem;
  border-radius: 0.75rem;
  background: transparent;
  cursor: pointer;
  font-weight: 600;
  color: #1e3a8a;
}

.loaner-count {
  font-size: 0.85rem;
  color: #64748b;
}

.loaner-preview {
  background: #f8fafc;
  border-radius: 0.75rem;
  padding: 0.75rem 1rem;
  color: #475569;
}

.loaner-agreement {
  display: grid;
  gap: 0.75rem;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
