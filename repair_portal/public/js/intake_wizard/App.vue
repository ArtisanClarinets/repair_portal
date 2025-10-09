<template>
  <div class="intake-wizard" role="application" aria-label="Intake wizard">
    <header class="wizard-header">
      <div>
        <h1 tabindex="0">Intake Wizard</h1>
        <p class="wizard-subtitle">Streamlined customer, instrument, player, and service intake for clarinet workflows.</p>
      </div>
      <div class="sla-indicator" :class="sla.statusClass" role="status" aria-live="polite">
        <span class="sla-label">SLA</span>
        <span class="sla-text">{{ sla.message }}</span>
      </div>
    </header>

    <nav class="wizard-steps" role="navigation" aria-label="Wizard progress">
      <ol>
        <li
          v-for="(step, index) in steps"
          :key="step.key"
          :class="stepClass(step, index)"
        >
          <button
            type="button"
            class="step-button"
            :aria-current="index === activeStepIndex ? 'step' : undefined"
            @click="goToStep(index)"
          >
            <span class="step-index">{{ index + 1 }}</span>
            <span class="step-label">{{ step.label }}</span>
          </button>
        </li>
      </ol>
    </nav>

    <main class="wizard-body" tabindex="0">
      <component
        :is="currentStep.component"
        v-model="stepModels[currentStep.key]"
        :customer="stepModels.customer"
        :service="stepModels.service"
        :player="stepModels.player"
        :instrument="stepModels.instrument"
        :step-key="currentStep.key"
        :loaners="loaners"
        :loading="loadingStates[currentStep.key]"
        @validity-change="updateValidity(currentStep.key, $event)"
        :fetch-customers="fetchCustomers"
        :upsert-customer="handleCustomerUpsert"
        :search-player="searchPlayers"
        :upsert-player="handlePlayerUpsert"
        :serial-lookup="lookupSerial"
        :fetch-loaners="loadLoaners"
        @log="logTelemetry"
      />
    </main>

    <footer class="wizard-footer">
      <button type="button" class="secondary" @click="prevStep" :disabled="activeStepIndex === 0">
        ← Previous
      </button>
      <button
        v-if="!isLastStep"
        type="button"
        class="primary"
        @click="nextStep"
        :disabled="!currentStepValid"
      >
        Next →
      </button>
      <button
        v-else
        type="button"
        class="primary"
        @click="submitIntake"
        :disabled="!canSubmit || submissionState.loading"
      >
        {{ submissionState.loading ? 'Submitting…' : 'Submit Intake' }}
      </button>
    </footer>

    <section v-if="submissionState.success" class="submission-summary" aria-live="polite">
      <h2>Intake Created</h2>
      <ul>
        <li><a :href="submissionState.links.intake_form_route">Open Intake Record</a></li>
        <li v-if="submissionState.links.intake_receipt_print"><a :href="submissionState.links.intake_receipt_print" target="_blank">Print Intake Receipt</a></li>
        <li v-if="submissionState.links.instrument_tag_print"><a :href="submissionState.links.instrument_tag_print" target="_blank">Print Instrument Tag</a></li>
        <li v-if="submissionState.links.instrument_qr_print"><a :href="submissionState.links.instrument_qr_print" target="_blank">Print Instrument QR</a></li>
        <li><a :href="submissionState.links.create_repair_request_route" target="_blank">Create Repair Request</a></li>
      </ul>
    </section>

    <section v-if="submissionState.error" class="submission-error" role="alert">
      <h2>Submission Failed</h2>
      <p>{{ submissionState.error }}</p>
    </section>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from "vue";

import CustomerStep from "./steps/CustomerStep.vue";
import InstrumentStep from "./steps/InstrumentStep.vue";
import PlayerStep from "./steps/PlayerStep.vue";
import ServiceStep from "./steps/ServiceStep.vue";
import ReviewStep from "./steps/ReviewStep.vue";

const steps = [
  { key: "customer", label: "Customer", component: CustomerStep },
  { key: "instrument", label: "Instrument", component: InstrumentStep },
  { key: "player", label: "Player", component: PlayerStep },
  { key: "service", label: "Service", component: ServiceStep },
  { key: "review", label: "Review", component: ReviewStep },
];

const activeStepIndex = ref(0);
const stepValidity = reactive({ customer: false, instrument: false, player: true, service: false, review: false });
const stepModels = reactive({
  customer: {},
  instrument: { accessories: [] },
  player: { sameAsCustomer: true },
  service: { loanerRequired: false, accessories: [] },
  review: {},
});
const sessionState = reactive({ id: null, status: "Draft" });
const loadingStates = reactive({ customer: false, instrument: false, player: false, service: false, review: false });
const loaners = ref([]);
const submissionState = reactive({ loading: false, success: false, error: null, links: {} });
const sla = reactive({ message: "Loading SLA…", statusClass: "sla-pending", due: null });

const currentStep = computed(() => steps[activeStepIndex.value]);
const currentStepValid = computed(() => !!stepValidity[currentStep.value.key]);
const isLastStep = computed(() => activeStepIndex.value === steps.length - 1);
const canSubmit = computed(() => Object.values(stepValidity).every(Boolean));

let debounceTimer = null;
let keyHandler = null;

function debounceSave(fn) {
  return function (...args) {
    if (debounceTimer) {
      clearTimeout(debounceTimer);
    }
    debounceTimer = setTimeout(() => {
      fn(...args);
    }, 400);
  };
}

const scheduleSave = debounceSave(async function saveSession(stepKey) {
  try {
    const response = await frappe.call({
      method: "repair_portal.intake.api.save_intake_session",
      args: {
        session_id: sessionState.id,
        last_step: stepKey,
        status: sessionState.status,
        payload: {
          customer: stepModels.customer,
          instrument: stepModels.instrument,
          player: stepModels.player,
          intake: {
            service: stepModels.service,
          },
        },
      },
    });
    if (response && response.message) {
      sessionState.id = response.message.session_id;
      sessionState.status = response.message.status;
      updateUrlSessionParam();
    }
  } catch (error) {
    console.error("Failed to persist intake session", error);
  }
});

function updateUrlSessionParam() {
  if (!sessionState.id) return;
  const url = new URL(window.location.href);
  if (url.searchParams.get("session_id") === sessionState.id) return;
  url.searchParams.set("session_id", sessionState.id);
  window.history.replaceState({}, "Intake Wizard", url.toString());
}

function updateValidity(stepKey, value) {
  stepValidity[stepKey] = value;
  stepModels.review = buildReviewModel();
  scheduleSave(stepKey);
}

function stepClass(step, index) {
  return {
    active: index === activeStepIndex.value,
    complete: stepValidity[step.key] && index < activeStepIndex.value,
  };
}

function goToStep(index) {
  if (index < 0 || index >= steps.length) return;
  activeStepIndex.value = index;
}

function nextStep() {
  if (!currentStepValid.value) return;
  if (activeStepIndex.value < steps.length - 1) {
    activeStepIndex.value += 1;
  }
}

function prevStep() {
  if (activeStepIndex.value > 0) {
    activeStepIndex.value -= 1;
  }
}

function logTelemetry(event) {
  if (!sessionState.id) return;
  frappe.call({
    method: "repair_portal.intake.api.save_intake_session",
    args: {
      session_id: sessionState.id,
      payload: {},
      last_step: currentStep.value.key,
      status: sessionState.status,
    },
  });
}

function buildReviewModel() {
  return {
    customer: stepModels.customer,
    instrument: stepModels.instrument,
    player: stepModels.player,
    service: stepModels.service,
  };
}

async function fetchCustomers(query) {
  if (!query || query.length < 2) {
    return [];
  }
  loadingStates.customer = true;
  try {
    const response = await frappe.call({
      method: "frappe.client.get_list",
      args: {
        doctype: "Customer",
        txt: query,
        fields: ["name", "customer_name", "customer_type", "email_id", "mobile_no", "phone"],
        limit_page_length: 10,
      },
    });
    return response.message || [];
  } finally {
    loadingStates.customer = false;
  }
}

async function handleCustomerUpsert(data) {
  loadingStates.customer = true;
  try {
    const response = await frappe.call({
      method: "repair_portal.intake.api.upsert_customer",
      args: { payload: data },
    });
    stepModels.customer.name = response.message.customer;
    updateValidity("customer", true);
    return response.message;
  } finally {
    loadingStates.customer = false;
  }
}

async function searchPlayers(query) {
  if (!query || query.length < 2) {
    return [];
  }
  loadingStates.player = true;
  try {
    const response = await frappe.call({
      method: "frappe.client.get_list",
      args: {
        doctype: "Player Profile",
        txt: query,
        fields: ["name", "player_name", "primary_email"],
        limit_page_length: 10,
      },
    });
    return response.message || [];
  } finally {
    loadingStates.player = false;
  }
}

async function handlePlayerUpsert(data) {
  loadingStates.player = true;
  try {
    const response = await frappe.call({
      method: "repair_portal.intake.api.upsert_player_profile",
      args: { payload: data },
    });
    stepModels.player.profile = response.message.player_profile;
    updateValidity("player", true);
    return response.message;
  } finally {
    loadingStates.player = false;
  }
}

async function lookupSerial(serial) {
  if (!serial) {
    return null;
  }
  loadingStates.instrument = true;
  try {
    const response = await frappe.call({
      method: "repair_portal.intake.api.get_instrument_by_serial",
      args: { serial_no: serial },
    });
    return response.message;
  } finally {
    loadingStates.instrument = false;
  }
}

async function loadLoaners(filters = {}) {
  loadingStates.service = true;
  try {
    const response = await frappe.call({
      method: "repair_portal.intake.api.list_available_loaners",
      args: { filters },
    });
    loaners.value = response.message || [];
    return loaners.value;
  } finally {
    loadingStates.service = false;
  }
}

async function submitIntake() {
  submissionState.loading = true;
  submissionState.error = null;
  submissionState.success = false;
  try {
    const payload = {
      intake: {
        ...stepModels.instrument,
        ...stepModels.customer,
        ...stepModels.service.intakeDetails,
        intake_type: stepModels.service.intakeType || "New Inventory",
        manufacturer: stepModels.instrument.manufacturer,
        model: stepModels.instrument.model,
        serial_no: stepModels.instrument.serial_no,
        item_code: stepModels.instrument.item_code || stepModels.instrument.serial_no,
        item_name: stepModels.instrument.item_name || stepModels.instrument.model,
        acquisition_cost: stepModels.service.acquisition_cost || 0,
        store_asking_price: stepModels.service.store_asking_price || 0,
        customers_stated_issue: stepModels.service.issue_description,
        initial_assessment_notes: stepModels.service.condition_notes,
        customer: stepModels.customer.name,
      },
    };
    if (stepModels.service.loanerAgreement) {
      payload.loaner_agreement = stepModels.service.loanerAgreement;
    }
    const response = await frappe.call({
      method: "repair_portal.intake.api.create_intake",
      args: { payload, session_id: sessionState.id },
    });
    submissionState.links = response.message;
    submissionState.success = true;
    sessionState.status = "Submitted";
    await loadSession(sessionState.id);
  } catch (error) {
    submissionState.error = error.message || String(error);
  } finally {
    submissionState.loading = false;
  }
}

async function loadSession(sessionId) {
  if (!sessionId) {
    return;
  }
  try {
    const response = await frappe.call({
      method: "repair_portal.intake.api.load_intake_session",
      args: { session_id: sessionId },
    });
    const message = response.message || {};
    sessionState.id = message.session_id;
    sessionState.status = message.status || "Draft";
    stepModels.customer = message.customer_json || {};
    stepModels.instrument = message.instrument_json || { accessories: [] };
    stepModels.player = message.player_json || { sameAsCustomer: true };
    stepModels.service = (message.intake_json && message.intake_json.service) || { loanerRequired: false };
    stepModels.review = buildReviewModel();
    Object.keys(stepValidity).forEach((key) => {
      stepValidity[key] = !!message.last_step;
    });
  } catch (error) {
    console.warn("Failed to load intake session", error);
  }
}

async function bootstrapSession() {
  const params = new URLSearchParams(window.location.search);
  const providedId = params.get("session_id");
  if (providedId) {
    await loadSession(providedId);
    if (sessionState.id) {
      return;
    }
  }
  const response = await frappe.call({
    method: "repair_portal.intake.api.save_intake_session",
    args: { payload: {}, last_step: "customer" },
  });
  if (response && response.message) {
    sessionState.id = response.message.session_id;
    sessionState.status = response.message.status;
    updateUrlSessionParam();
  }
}

async function fetchSla() {
  try {
    const policyResponse = await frappe.call({
      method: "frappe.client.get_list",
      args: {
        doctype: "SLA Policy",
        filters: { default_policy: 1, enabled: 1 },
        fields: ["name", "warn_threshold_pct", "critical_threshold_pct"],
        limit_page_length: 1,
      },
    });
    const policies = policyResponse.message || [];
    if (!policies.length) {
      sla.message = "No SLA policy configured";
      sla.statusClass = "sla-none";
      return;
    }
    const policy = policies[0];
    const rulesResponse = await frappe.call({
      method: "frappe.client.get_list",
      args: {
        doctype: "SLA Policy Rule",
        filters: { parent: policy.name },
        fields: ["tat_hours"],
        limit_page_length: 1,
      },
    });
    const rule = (rulesResponse.message || [])[0];
    if (!rule) {
      sla.message = "SLA rule missing";
      sla.statusClass = "sla-none";
      return;
    }
    const hours = Number(rule.tat_hours || 0);
    const now = frappe.datetime.now_datetime();
    const due = frappe.datetime.add_hours(now, hours);
    sla.due = due;
    const totalMillis = hours * 60 * 60 * 1000;
    const elapsedMillis = new Date().getTime() - new Date(now).getTime();
    const progress = totalMillis ? (elapsedMillis / totalMillis) * 100 : 0;
    if (progress < policy.warn_threshold_pct) {
      sla.message = `On track – due ${frappe.datetime.str_to_user(due)}`;
      sla.statusClass = "sla-good";
    } else if (progress < policy.critical_threshold_pct) {
      sla.message = `At risk – due ${frappe.datetime.str_to_user(due)}`;
      sla.statusClass = "sla-warning";
    } else {
      sla.message = `Critical – due ${frappe.datetime.str_to_user(due)}`;
      sla.statusClass = "sla-critical";
    }
  } catch (error) {
    sla.message = "SLA unavailable";
    sla.statusClass = "sla-none";
  }
}

onMounted(async () => {
  await bootstrapSession();
  await fetchSla();
  keyHandler = (event) => {
    if (event.key === "ArrowRight") {
      nextStep();
    }
    if (event.key === "ArrowLeft") {
      prevStep();
    }
    if (event.key === "Enter" && currentStepValid.value && !isLastStep.value) {
      nextStep();
    }
  };
  window.addEventListener("keydown", keyHandler);
});

onBeforeUnmount(() => {
  if (keyHandler) {
    window.removeEventListener("keydown", keyHandler);
  }
});

</script>

<style scoped>
.intake-wizard {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1.5rem;
}
.wizard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}
.wizard-header h1 {
  font-size: 1.75rem;
  margin: 0;
}
.wizard-subtitle {
  margin: 0.25rem 0 0;
  color: #555;
}
.sla-indicator {
  border-radius: 999px;
  padding: 0.5rem 1rem;
  font-weight: 600;
  display: flex;
  gap: 0.5rem;
  align-items: center;
}
.sla-label {
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.05em;
}
.sla-text {
  font-size: 0.85rem;
}
.sla-good {
  background: #e6ffed;
  color: #046c4e;
}
.sla-warning {
  background: #fff7e6;
  color: #8a5700;
}
.sla-critical {
  background: #ffe6e6;
  color: #8a1f11;
}
.sla-none, .sla-pending {
  background: #f3f4f6;
  color: #4b5563;
}
.wizard-steps ol {
  list-style: none;
  display: flex;
  gap: 0.75rem;
  padding: 0;
  margin: 0;
}
.step-button {
  border: none;
  background: transparent;
  padding: 0.5rem 0.75rem;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}
.step-index {
  width: 1.75rem;
  height: 1.75rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #e5e7eb;
  color: #111827;
  font-weight: 600;
}
.step-label {
  font-weight: 600;
}
.active .step-button {
  background: #1f2937;
  color: #fff;
}
.active .step-index {
  background: #111827;
  color: #fff;
}
.complete .step-button {
  background: #047857;
  color: #fff;
}
.complete .step-index {
  background: #065f46;
  color: #fff;
}
.wizard-body {
  background: #fff;
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
}
.wizard-footer {
  display: flex;
  justify-content: space-between;
}
.wizard-footer button {
  border-radius: 0.5rem;
  padding: 0.75rem 1.25rem;
  font-size: 0.95rem;
  cursor: pointer;
}
.primary {
  background: #2563eb;
  color: #fff;
  border: none;
}
.primary[disabled] {
  background: #93c5fd;
  cursor: not-allowed;
}
.secondary {
  background: transparent;
  border: 1px solid #d1d5db;
  color: #374151;
}
.submission-summary, .submission-error {
  border-radius: 0.75rem;
  padding: 1rem 1.5rem;
  background: #f9fafb;
}
.submission-error {
  border-left: 4px solid #dc2626;
}
.submission-summary ul {
  list-style: none;
  padding: 0;
  margin: 0.5rem 0 0;
}
.submission-summary li {
  margin-bottom: 0.5rem;
}
.submission-summary a {
  color: #2563eb;
  text-decoration: none;
}
</style>
