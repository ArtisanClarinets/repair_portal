<template>
  <div class="intake-wizard" role="application" aria-label="Intake wizard">
    <header class="wizard-header">
      <div class="wizard-title-block">
        <p class="wizard-eyebrow">Clarinet Operations Command Center</p>
        <h1 tabindex="0">Intake Wizard</h1>
        <p class="wizard-subtitle">
          Capture customer, instrument, player, and service insights with concierge-level guidance and auto-save safeguards.
        </p>
        <div class="wizard-hints" role="note">
          <span>Keyboard: ← Previous · → Next · Enter confirms.</span>
          <span>All activity is secured under your intake coordinator permissions.</span>
        </div>
      </div>
      <div class="wizard-meta">
        <div v-if="sessionState.id" class="session-chip" aria-live="polite">
          <span class="chip-label">Session</span>
          <span class="chip-value">{{ sessionState.id }}</span>
        </div>
        <div class="autosave-status" :class="autosaveClass" role="status" aria-live="polite">
          <span class="status-dot"></span>
          <span>{{ autosaveState.message }}</span>
        </div>
        <div class="sla-indicator" :class="sla.statusClass" role="status" aria-live="polite">
          <span class="sla-label">SLA</span>
          <span class="sla-text">{{ sla.message }}</span>
        </div>
      </div>
    </header>

    <div class="wizard-layout">
      <aside class="wizard-progress" role="navigation" aria-label="Wizard progress">
        <div class="progress-header">
          <div>
            <span class="progress-label">Progress</span>
            <span class="progress-value">{{ progressPercent }}%</span>
          </div>
          <span class="progress-steps">Step {{ activeStepIndex + 1 }} of {{ steps.length }}</span>
        </div>
        <div class="progress-bar" role="presentation">
          <div
            class="progress-fill"
            role="progressbar"
            :aria-valuemin="0"
            :aria-valuemax="100"
            :aria-valuenow="progressPercent"
            :style="{ width: `${progressPercent}%` }"
          ></div>
        </div>
        <ol class="step-list">
          <li v-for="(step, index) in steps" :key="step.key" :class="stepClass(step, index)">
            <button
              type="button"
              class="step-button"
              :aria-current="index === activeStepIndex ? 'step' : undefined"
              :disabled="index > furthestUnlockedIndex"
              @click="goToStep(index)"
            >
              <span class="step-index">{{ index + 1 }}</span>
              <div class="step-meta">
                <span class="step-label">{{ step.label }}</span>
                <span class="step-description">{{ step.description }}</span>
              </div>
              <span v-if="stepValidity[step.key]" class="step-status">Complete</span>
              <span v-else-if="index === activeStepIndex" class="step-status">In Progress</span>
              <span v-else class="step-status muted">Pending</span>
            </button>
          </li>
        </ol>
        <div class="progress-footer">
          <p class="progress-help">Need playbook guidance?</p>
          <button type="button" class="link-button" @click="openKnowledgeBase">Open Intake SOP</button>
        </div>
      </aside>

      <section class="wizard-content" ref="wizardContent" tabindex="-1" aria-live="polite">
        <transition name="step-fade" mode="out-in">
          <component
            :is="currentStep.component"
            :key="currentStep.key"
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
        </transition>
      </section>
    </div>

    <footer class="wizard-footer">
      <div class="footer-support">
        <span class="support-label">Questions?</span>
        <button type="button" class="link-button" @click="startSupportChat">Message workshop lead</button>
      </div>
      <div class="footer-actions">
        <button type="button" class="secondary" @click="prevStep" :disabled="activeStepIndex === 0">← Previous</button>
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
      </div>
    </footer>

    <transition name="summary-fade">
      <section v-if="submissionState.success" class="submission-summary" aria-live="polite">
        <h2>Intake Created</h2>
        <p>Your intake has been logged and routed to inspection.</p>
        <ul>
          <li><a :href="submissionState.links.intake_form_route">Open Intake Record</a></li>
          <li v-if="submissionState.links.intake_receipt_print"><a :href="submissionState.links.intake_receipt_print" target="_blank">Print Intake Receipt</a></li>
          <li v-if="submissionState.links.instrument_tag_print"><a :href="submissionState.links.instrument_tag_print" target="_blank">Print Instrument Tag</a></li>
          <li v-if="submissionState.links.instrument_qr_print"><a :href="submissionState.links.instrument_qr_print" target="_blank">Print Instrument QR</a></li>
          <li><a :href="submissionState.links.create_repair_request_route" target="_blank">Create Repair Request</a></li>
        </ul>
      </section>
    </transition>

    <transition name="summary-fade">
      <section v-if="submissionState.error" class="submission-error" role="alert">
        <h2>Submission Failed</h2>
        <p>{{ submissionState.error }}</p>
        <p class="suggestion">Your progress is still saved. Resolve the error and try again.</p>
      </section>
    </transition>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from "vue";

import CustomerStep from "./steps/CustomerStep.vue";
import InstrumentStep from "./steps/InstrumentStep.vue";
import PlayerStep from "./steps/PlayerStep.vue";
import ServiceStep from "./steps/ServiceStep.vue";
import ReviewStep from "./steps/ReviewStep.vue";

const steps = [
  {
    key: "customer",
    label: "Customer",
    description: "Primary contact and billing preferences",
    component: CustomerStep,
  },
  {
    key: "instrument",
    label: "Instrument",
    description: "Serial verification and spec capture",
    component: InstrumentStep,
  },
  {
    key: "player",
    label: "Player",
    description: "Ownership and performance context",
    component: PlayerStep,
  },
  {
    key: "service",
    label: "Service",
    description: "Issue triage and loaner planning",
    component: ServiceStep,
  },
  {
    key: "review",
    label: "Review",
    description: "Final audit before submission",
    component: ReviewStep,
  },
];

const activeStepIndex = ref(0);
const stepValidity = reactive({ customer: false, instrument: false, player: true, service: false, review: false });
const stepModels = reactive({
  customer: {},
  instrument: { accessories: [], brand_mapping: null },
  player: { sameAsCustomer: true },
  service: { loanerRequired: false, accessories: [] },
  review: {},
});
const sessionState = reactive({ id: null, status: "Draft" });
const autosaveState = reactive({ status: "idle", message: "Idle", timestamp: null });
const loadingStates = reactive({ customer: false, instrument: false, player: false, service: false, review: false });
const loaners = ref([]);
const submissionState = reactive({ loading: false, success: false, error: null, links: {} });
const sla = reactive({ message: "Loading SLA…", statusClass: "sla-pending", due: null });
const wizardContent = ref(null);
const isBootstrapped = ref(false);

const currentStep = computed(() => steps[activeStepIndex.value]);
const currentStepValid = computed(() => !!stepValidity[currentStep.value.key]);
const isLastStep = computed(() => activeStepIndex.value === steps.length - 1);
const completedSteps = computed(() => steps.filter((step) => stepValidity[step.key]).length);
const canSubmit = computed(() => steps.every((step) => stepValidity[step.key]));
const furthestUnlockedIndex = computed(() => {
  const completedIndex = steps.findIndex((step) => !stepValidity[step.key]);
  if (completedIndex === -1) {
    return steps.length - 1;
  }
  return Math.max(completedIndex, activeStepIndex.value);
});
const progressPercent = computed(() => {
  const base = (completedSteps.value / steps.length) * 100;
  if (!stepValidity[currentStep.value.key]) {
    const incremental = (activeStepIndex.value / steps.length) * 100;
    return Math.max(Math.round(incremental), Math.round(base));
  }
  return Math.round(Math.max(base, ((activeStepIndex.value + 1) / steps.length) * 100));
});
const autosaveClass = computed(() => ({
  "status-idle": autosaveState.status === "idle",
  "status-saving": autosaveState.status === "saving",
  "status-success": autosaveState.status === "saved",
  "status-error": autosaveState.status === "error",
}));

let debounceTimer = null;
let keyHandler = null;
let autosaveResetTimer = null;

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

function setAutosaveStatus(status, message) {
  autosaveState.status = status;
  autosaveState.message = message;
  if (status === "saved" && autosaveState.timestamp) {
    autosaveState.message = `Saved ${formatTimestamp(autosaveState.timestamp)}`;
  }
}

const scheduleSave = debounceSave(async function saveSession(stepKey) {
  if (!isBootstrapped.value) {
    return;
  }
  try {
    setAutosaveStatus("saving", "Saving…");
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
      autosaveState.timestamp = new Date();
      setAutosaveStatus("saved", "Changes saved");
      if (autosaveResetTimer) {
        clearTimeout(autosaveResetTimer);
      }
      autosaveResetTimer = setTimeout(() => {
        setAutosaveStatus("idle", "All changes saved");
      }, 3000);
    }
  } catch (error) {
    console.error("Failed to persist intake session", error);
    setAutosaveStatus("error", "Auto-save failed. Changes stored locally.");
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
    locked: index > furthestUnlockedIndex.value,
  };
}

function goToStep(index) {
  if (index < 0 || index >= steps.length) return;
  if (index > furthestUnlockedIndex.value) return;
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
    frappe.show_alert({ message: "Customer linked", indicator: "green" });
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
    frappe.show_alert({ message: "Player profile saved", indicator: "green" });
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
      customer: stepModels.customer,
      instrument: stepModels.instrument,
      player: stepModels.player,
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
    frappe.show_alert({ message: "Intake created", indicator: "green" });
  } catch (error) {
    submissionState.error = error.message || String(error);
    frappe.show_alert({ message: "Submission failed", indicator: "red" });
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
    stepModels.instrument = message.instrument_json || { accessories: [], brand_mapping: null };
    stepModels.player = message.player_json || { sameAsCustomer: true };
    const servicePayload = (message.intake_json && message.intake_json.service) || { loanerRequired: false };
    stepModels.service = { ...stepModels.service, ...servicePayload };
    stepModels.review = buildReviewModel();
    Object.keys(stepValidity).forEach((key) => {
      stepValidity[key] = key === "player" ? true : Boolean(message.last_step);
    });
    isBootstrapped.value = true;
  } catch (error) {
    console.warn("Failed to load intake session", error);
    isBootstrapped.value = true;
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
  isBootstrapped.value = true;
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
    sla.message = `Warn at ${policy.warn_threshold_pct}% · Critical at ${policy.critical_threshold_pct}%`;
    sla.statusClass = "sla-good";
  } catch (error) {
    console.warn("Failed to fetch SLA policy", error);
    sla.message = "SLA unavailable";
    sla.statusClass = "sla-none";
  }
}

function openKnowledgeBase() {
  window.open("https://artisanclarinets.notion.site/intake-sop", "_blank");
}

function startSupportChat() {
  frappe.show_alert({ message: "Ping sent to workshop lead via desk notifications.", indicator: "blue" });
}

function formatTimestamp(timestamp) {
  if (!timestamp) return "recently";
  try {
    return new Intl.DateTimeFormat("en", { hour: "numeric", minute: "2-digit" }).format(timestamp);
  } catch (error) {
    return "recently";
  }
}

watch(
  () => activeStepIndex.value,
  async () => {
    await nextTick();
    if (wizardContent.value) {
      wizardContent.value.focus({ preventScroll: false });
    }
  }
);

watch(
  () => stepModels.customer,
  () => {
    scheduleSave("customer");
  },
  { deep: true }
);

watch(
  () => stepModels.instrument,
  () => {
    scheduleSave("instrument");
  },
  { deep: true }
);

watch(
  () => stepModels.player,
  () => {
    scheduleSave("player");
  },
  { deep: true }
);

watch(
  () => stepModels.service,
  () => {
    scheduleSave("service");
  },
  { deep: true }
);

steps.forEach((step) => {
  watch(
    () => stepValidity[step.key],
    (value, oldValue) => {
      if (value && !oldValue && step.key !== "review") {
        frappe.show_alert({ message: `${step.label} complete`, indicator: "green" });
      }
    }
  );
});

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
  if (autosaveResetTimer) {
    clearTimeout(autosaveResetTimer);
  }
});
</script>

<style scoped>
:global(body) {
  background: #f3f4f6;
}

.intake-wizard {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  color: #0f172a;
}

.wizard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1.5rem;
}

.wizard-title-block h1 {
  font-size: 2rem;
  margin: 0;
}

.wizard-eyebrow {
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #64748b;
  margin: 0 0 0.25rem;
}

.wizard-subtitle {
  margin: 0.5rem 0 0;
  color: #475569;
  max-width: 620px;
}

.wizard-hints {
  display: flex;
  gap: 1rem;
  font-size: 0.85rem;
  color: #64748b;
  margin-top: 0.75rem;
  flex-wrap: wrap;
}

.wizard-meta {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  align-items: flex-end;
}

.session-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, #0f172a, #1e293b);
  color: #fff;
  padding: 0.5rem 0.9rem;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 600;
}

.chip-label {
  opacity: 0.7;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.autosave-status {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 600;
  background: #e2e8f0;
  color: #334155;
}

.autosave-status .status-dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  background: currentColor;
}

.autosave-status.status-saving {
  background: #e0f2fe;
  color: #0369a1;
}

.autosave-status.status-success {
  background: #dcfce7;
  color: #166534;
}

.autosave-status.status-error {
  background: #fee2e2;
  color: #b91c1c;
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

.sla-none,
.sla-pending {
  background: #f1f5f9;
  color: #475569;
}

.wizard-layout {
  display: grid;
  grid-template-columns: minmax(260px, 300px) 1fr;
  gap: 1.75rem;
}

.wizard-progress {
  background: #fff;
  border-radius: 1rem;
  padding: 1.25rem;
  box-shadow: 0 18px 35px rgba(15, 23, 42, 0.12);
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.progress-label {
  display: block;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #64748b;
}

.progress-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
}

.progress-steps {
  font-size: 0.85rem;
  color: #64748b;
}

.progress-bar {
  height: 0.5rem;
  border-radius: 999px;
  background: #e2e8f0;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  transition: width 0.3s ease;
}

.step-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 0;
  margin: 0;
}

.step-button {
  width: 100%;
  border: none;
  background: #f8fafc;
  padding: 0.75rem;
  border-radius: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  text-align: left;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.step-button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.step-button:focus-visible {
  outline: 2px solid #2563eb;
  outline-offset: 2px;
}

.step-index {
  width: 2rem;
  height: 2rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #e2e8f0;
  color: #0f172a;
  font-weight: 600;
}

.step-meta {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.step-label {
  font-weight: 600;
}

.step-description {
  font-size: 0.8rem;
  color: #64748b;
}

.step-status {
  margin-left: auto;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.muted {
  color: #94a3b8;
}

.active .step-button {
  background: #1f2937;
  color: #fff;
  box-shadow: 0 12px 24px rgba(30, 64, 175, 0.25);
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

.locked .step-button {
  box-shadow: none;
}

.progress-footer {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.progress-help {
  margin: 0;
  font-size: 0.85rem;
  color: #64748b;
}

.link-button {
  border: none;
  background: none;
  color: #2563eb;
  cursor: pointer;
  font-weight: 600;
  padding: 0;
}

.link-button:hover {
  text-decoration: underline;
}

.wizard-content {
  background: #fff;
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 25px 55px rgba(15, 23, 42, 0.15);
  min-height: 540px;
  outline: none;
}

.step-fade-enter-active,
.step-fade-leave-active {
  transition: opacity 0.2s ease;
}

.step-fade-enter-from,
.step-fade-leave-to {
  opacity: 0;
}

.wizard-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  border-radius: 1rem;
  padding: 1rem 1.5rem;
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.1);
}

.footer-support {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.support-label {
  font-weight: 600;
  color: #475569;
}

.footer-actions {
  display: flex;
  gap: 1rem;
}

.primary,
.secondary {
  border-radius: 0.75rem;
  padding: 0.85rem 1.6rem;
  font-size: 0.95rem;
  cursor: pointer;
  font-weight: 600;
}

.primary {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: #fff;
  border: none;
  box-shadow: 0 18px 30px rgba(37, 99, 235, 0.25);
}

.primary[disabled] {
  background: #93c5fd;
  cursor: not-allowed;
  box-shadow: none;
}

.secondary {
  background: transparent;
  border: 1px solid #cbd5f5;
  color: #1e3a8a;
}

.submission-summary,
.submission-error {
  border-radius: 1rem;
  padding: 1.25rem 1.75rem;
  background: #f8fafc;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.5), 0 10px 20px rgba(15, 23, 42, 0.08);
}

.summary-fade-enter-active,
.summary-fade-leave-active {
  transition: opacity 0.3s ease;
}

.summary-fade-enter-from,
.summary-fade-leave-to {
  opacity: 0;
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
  font-weight: 600;
}

.suggestion {
  margin-top: 0.75rem;
  color: #64748b;
}

@media (max-width: 960px) {
  .wizard-layout {
    grid-template-columns: 1fr;
  }

  .wizard-progress {
    order: 2;
  }

  .wizard-content {
    order: 1;
  }

  .wizard-header {
    flex-direction: column;
  }

  .wizard-meta {
    align-items: flex-start;
  }
}

@media (max-width: 640px) {
  .intake-wizard {
    padding: 1rem;
  }

  .wizard-content {
    padding: 1.25rem;
  }

  .wizard-footer {
    flex-direction: column;
    gap: 1rem;
  }

  .footer-actions {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
