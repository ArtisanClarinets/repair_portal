<template>
  <section aria-labelledby="service-heading" class="wizard-section">
    <h2 id="service-heading">Service Intake</h2>
    <p class="section-hint">Record service expectations, condition notes, and loaner details.</p>

    <div class="form-grid">
      <label>
        Intake Type
        <select v-model="local.intakeType" @change="update">
          <option>Repair</option>
          <option>Maintenance</option>
          <option>New Inventory</option>
        </select>
      </label>
      <label v-if="local.intakeType === 'New Inventory'">
        Acquisition Cost
        <input v-model.number="local.acquisition_cost" type="number" min="0" step="0.01" @input="update" />
      </label>
      <label v-if="local.intakeType === 'New Inventory'">
        Store Asking Price
        <input v-model.number="local.store_asking_price" type="number" min="0" step="0.01" @input="update" />
      </label>
    </div>

    <label>
      Issue Description
      <textarea v-model.trim="local.issue_description" rows="3" @input="update"></textarea>
    </label>
    <label>
      Condition Notes
      <textarea v-model.trim="local.condition_notes" rows="3" @input="update"></textarea>
    </label>

    <div class="loaner-toggle">
      <label class="checkbox">
        <input type="checkbox" v-model="local.loanerRequired" @change="toggleLoaner" /> Loaner instrument required
      </label>
    </div>

    <div v-if="local.loanerRequired" class="loaner-section">
      <button type="button" class="secondary" @click="fetchAvailableLoaners">Refresh Loaner List</button>
      <label>
        Select Loaner
        <select v-model="local.loanerInstrument" @change="update">
          <option value="">Choose loaner</option>
          <option v-for="row in loaners" :key="row.loaner" :value="row.loaner">
            {{ row.loaner }} — {{ row.instrument_details.manufacturer || 'Unknown' }} {{ row.instrument_details.model || '' }}
          </option>
        </select>
      </label>
      <div class="loaner-agreement">
        <h3>Loaner Agreement</h3>
        <label class="checkbox">
          <input type="checkbox" v-model="local.loanerAgreement.terms_ack" @change="update" /> Borrower agrees to terms
        </label>
        <label>
          Borrower Signature (data URL)
          <input v-model.trim="local.loanerAgreement.borrower_signature" type="text" @input="update" />
        </label>
        <label>
          Staff Signature (data URL)
          <input v-model.trim="local.loanerAgreement.staff_signature" type="text" @input="update" />
        </label>
      </div>
    </div>
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

const loaners = computed(() => props.loaners);

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
  },
});

watch(
  () => props.modelValue,
  (value) => {
    Object.assign(local, { ...local, ...value });
    if (!local.loanerAgreement) {
      local.loanerAgreement = { terms_ack: false, borrower_signature: "", staff_signature: "" };
    }
    validate();
  },
  { immediate: true, deep: true }
);

function update() {
  if (local.loanerAgreement) {
    local.loanerAgreement.linked_loaner = local.loanerInstrument || "";
  }
  emit("update:modelValue", { ...local, intakeDetails: buildIntakeDetails(), loanerAgreement: local.loanerAgreement });
  validate();
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

function validate() {
  let valid = true;
  if (local.intakeType === "New Inventory") {
    valid = valid && local.acquisition_cost >= 0 && local.store_asking_price >= 0;
  } else {
    valid = valid && Boolean(local.issue_description);
  }
  if (local.loanerRequired) {
    valid =
      valid &&
      Boolean(
        local.loanerInstrument &&
          local.loanerAgreement.terms_ack &&
          local.loanerAgreement.borrower_signature &&
          local.loanerAgreement.staff_signature
      );
  }
  emit("validity-change", valid);
  return valid;
}
</script>

<style scoped>
.wizard-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1rem;
}
label {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-weight: 600;
  font-size: 0.85rem;
}
textarea, select, input {
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  border: 1px solid #d1d5db;
}
.loaner-toggle {
  margin-top: 0.5rem;
}
.checkbox {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.loaner-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  background: #f9fafb;
  border-radius: 0.75rem;
  padding: 1rem;
}
.secondary {
  align-self: flex-start;
  border: 1px solid #d1d5db;
  padding: 0.4rem 0.9rem;
  border-radius: 0.5rem;
  background: transparent;
  cursor: pointer;
}
.loaner-agreement {
  display: grid;
  gap: 0.75rem;
}
.section-hint {
  margin: 0;
  color: #6b7280;
}
</style>
