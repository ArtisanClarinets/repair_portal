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

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const phonePattern = /^[0-9()+\-\s]{7,}$/;

function defaultCustomer() {
  return {
    name: null,
    customer_name: "",
    email: "",
    phone: "",
    address_line1: "",
    address_line2: "",
    city: "",
    state: "",
    pincode: "",
    country: "United States",
  };
}

function defaultInstrument() {
  return {
    manufacturer: "",
    model: "",
    serial_no: "",
    instrument_category: "",
    clarinet_type: "",
    instrument_type: "",
    body_material: "",
    key_plating: "",
    item_code: "",
    item_name: "",
    accessories: [],
    brand_mapping: null,
  };
}

function defaultPlayer() {
  return {
    sameAsCustomer: true,
    player_name: "",
    preferred_name: "",
    primary_email: "",
    primary_phone: "",
    player_level: "Amateur/Hobbyist",
    profile: null,
  };
}

function defaultService() {
  return {
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
    intakeDetails: {},
  };
}

function normalizeAccessory(item) {
  if (!item) {
    return null;
  }
  if (typeof item === "string") {
    return {
      item_code: "",
      description: item,
      qty: 1,
      uom: "",
      rate: 0,
    };
  }
  const normalized = {
    item_code: item.item_code || "",
    description: item.description || item.label || "",
    qty: Number.isFinite(item.qty) ? Number(item.qty) : 1,
    uom: item.uom || "",
    rate: Number.isFinite(item.rate) ? Number(item.rate) : 0,
  };
  return normalized;
}

function normalizeAccessories(accessories = []) {
  return (Array.isArray(accessories) ? accessories : [])
    .map((item) => normalizeAccessory(item))
    .filter(Boolean);
}

function transformAccessoriesForIntake(accessories = []) {
  return normalizeAccessories(accessories)
    .filter((item) => item.item_code)
    .map((item, index) => ({
      doctype: "Intake Accessory Item",
      idx: index + 1,
      item_code: item.item_code,
      description: item.description || undefined,
      qty: item.qty || 1,
      uom: item.uom || undefined,
      rate: item.rate || 0,
    }));
}

function computeCustomerValidityState(customer) {
  if (!customer) return false;
  return Boolean(
    customer.customer_name &&
      customer.email &&
      emailPattern.test(customer.email) &&
      customer.phone &&
      phonePattern.test(customer.phone)
  );
}

function computeInstrumentValidityState(instrument) {
  if (!instrument) return false;
  return Boolean(
    instrument.manufacturer &&
      instrument.model &&
      instrument.serial_no &&
      instrument.instrument_category &&
      instrument.clarinet_type
  );
}

function computePlayerValidityState(player, customer) {
  if (!player) return false;
  if (player.sameAsCustomer) {
    return computeCustomerValidityState(customer);
  }
  return Boolean(
    player.player_name &&
      player.primary_email &&
      emailPattern.test(player.primary_email) &&
      player.primary_phone &&
      phonePattern.test(player.primary_phone) &&
      player.player_level
  );
}

function computeServiceValidityState(service) {
  if (!service) return false;
  let valid = true;
  if ((service.intakeType || "Repair") !== "New Inventory") {
    valid = Boolean(service.issue_description);
  }
  if (service.loanerRequired) {
    valid =
      valid &&
      Boolean(
        service.loanerInstrument &&
          service.loanerAgreement?.terms_ack &&
          service.loanerAgreement?.borrower_signature &&
          service.loanerAgreement?.staff_signature
      );
  }
  return Boolean(valid);
}

function computeReviewValidityState(customer, instrument, player, service) {
  return (
    computeCustomerValidityState(customer) &&
    computeInstrumentValidityState(instrument) &&
    computePlayerValidityState(player, customer) &&
    computeServiceValidityState(service)
  );
}

const activeStepIndex = ref(0);
const stepValidity = reactive({ customer: false, instrument: false, player: false, service: false, review: false });
const stepModels = reactive({
  customer: defaultCustomer(),
  instrument: defaultInstrument(),
  player: defaultPlayer(),
  service: defaultService(),
  review: {},
});

function refreshValidity(stepKey) {
  if (stepKey === "customer") {
    stepValidity.customer = computeCustomerValidityState(stepModels.customer);
  } else if (stepKey === "instrument") {
    stepValidity.instrument = computeInstrumentValidityState(stepModels.instrument);
  } else if (stepKey === "player") {
    stepValidity.player = computePlayerValidityState(stepModels.player, stepModels.customer);
  } else if (stepKey === "service") {
    stepValidity.service = computeServiceValidityState(stepModels.service);
  } else if (stepKey === "review") {
    stepValidity.review = computeReviewValidityState(
      stepModels.customer,
      stepModels.instrument,
      stepModels.player,
      stepModels.service
    );
  }
  if (stepKey !== "review") {
    stepValidity.review = computeReviewValidityState(
      stepModels.customer,
      stepModels.instrument,
      stepModels.player,
      stepModels.service
    );
  }
}

function recomputeAllStepValidity() {
  refreshValidity("customer");
  refreshValidity("instrument");
  refreshValidity("player");
  refreshValidity("service");
  refreshValidity("review");
}

recomputeAllStepValidity();
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
  if (stepKey !== "review") {
    stepValidity.review = computeReviewValidityState(
      stepModels.customer,
      stepModels.instrument,
      stepModels.player,
      stepModels.service
    );
  }
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
    const payload = {
      ...data,
      primary_phone: data.primary_phone,
    };
    if (stepModels.customer?.name) {
      payload.customer = stepModels.customer.name;
    }
    const response = await frappe.call({
      method: "repair_portal.intake.api.upsert_player_profile",
      args: { payload },
    });
    stepModels.player.profile = response.message.player_profile;
    updateValidity("player", true);
    const linkedName = stepModels.customer?.customer_name || "customer";
    frappe.show_alert({ message: `Player profile synced to ${linkedName}`, indicator: "green" });
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
    const customer = { ...defaultCustomer(), ...stepModels.customer };
    const instrument = { ...defaultInstrument(), ...stepModels.instrument };
    instrument.accessories = normalizeAccessories(instrument.accessories);
    const player = { ...defaultPlayer(), ...stepModels.player };
    const service = { ...defaultService(), ...stepModels.service };
    const customerLink = customer.name;
    if (!customerLink) {
      throw new Error("Customer record must be saved before submission.");
    }
    const intakeAccessories = transformAccessoriesForIntake(instrument.accessories);
    const intakePayload = {
      ...service.intakeDetails,
      intake_type: service.intakeType || service.intakeDetails?.intake_type || "New Inventory",
      instrument_category: instrument.instrument_category,
      manufacturer: instrument.manufacturer,
      model: instrument.model,
      serial_no: instrument.serial_no,
      clarinet_type: instrument.clarinet_type,
      body_material: instrument.body_material,
      key_plating: instrument.key_plating,
      item_code: instrument.item_code || instrument.serial_no || instrument.model,
      item_name: instrument.item_name || instrument.model || instrument.serial_no,
      acquisition_cost: Number.isFinite(service.acquisition_cost) ? Number(service.acquisition_cost) : 0,
      store_asking_price: Number.isFinite(service.store_asking_price) ? Number(service.store_asking_price) : 0,
      customers_stated_issue: service.issue_description,
      initial_assessment_notes: service.condition_notes,
      customer: customerLink,
      customer_full_name: customer.customer_name,
      customer_email: customer.email,
      customer_phone: customer.phone,
      player_profile: player.profile || undefined,
    };
    if (intakeAccessories.length) {
      intakePayload.accessory_id = intakeAccessories;
    }
    const payload = {
      customer,
      instrument,
      player,
      intake: intakePayload,
    };
    if (service.loanerAgreement && (service.loanerAgreement.borrower_signature || service.loanerAgreement.staff_signature)) {
      payload.loaner_agreement = service.loanerAgreement;
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
    const customerPayload = { ...defaultCustomer(), ...(message.customer_json || {}) };
    const instrumentPayload = { ...defaultInstrument(), ...(message.instrument_json || {}) };
    instrumentPayload.accessories = normalizeAccessories(instrumentPayload.accessories);
    const playerPayload = { ...defaultPlayer(), ...(message.player_json || {}) };
    playerPayload.sameAsCustomer = playerPayload.sameAsCustomer !== false;
    const rawService = (message.intake_json && message.intake_json.service) || {};
    const servicePayload = { ...defaultService(), ...rawService };
    servicePayload.loanerAgreement = {
      ...defaultService().loanerAgreement,
      ...(rawService.loanerAgreement || rawService.loaner_agreement || {}),
    };
    servicePayload.intakeDetails = rawService.intakeDetails || servicePayload.intakeDetails || {};
    stepModels.customer = customerPayload;
    stepModels.instrument = instrumentPayload;
    stepModels.player = playerPayload;
    stepModels.service = servicePayload;
    stepModels.review = buildReviewModel();
    recomputeAllStepValidity();
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
  stepModels.customer = defaultCustomer();
  stepModels.instrument = defaultInstrument();
  stepModels.instrument.accessories = [];
  stepModels.player = defaultPlayer();
  stepModels.service = defaultService();
  stepModels.review = buildReviewModel();
  recomputeAllStepValidity();
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
    refreshValidity("customer");
    stepModels.review = buildReviewModel();
    scheduleSave("customer");
  },
  { deep: true }
);

watch(
  () => stepModels.instrument,
  () => {
    if (!Array.isArray(stepModels.instrument.accessories)) {
      stepModels.instrument.accessories = [];
    }
    refreshValidity("instrument");
    stepModels.review = buildReviewModel();
    scheduleSave("instrument");
  },
  { deep: true }
);

watch(
  () => stepModels.player,
  () => {
    refreshValidity("player");
    stepModels.review = buildReviewModel();
    scheduleSave("player");
  },
  { deep: true }
);

watch(
  () => stepModels.service,
  () => {
    refreshValidity("service");
    stepModels.review = buildReviewModel();
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
:root {
  /* Premium Design Tokens (Apple-caliber) */
  --bg: #f5f5f7; /* Apple-like light gray */
  --card-bg: #ffffff;
  --surface: #ffffff;
  --text: #1d1d1f; /* San Francisco optimized black */
  --muted: #86868b;
  --border: #d2d2d7;
  --primary: #0071e3; /* Apple Blue */
  --primary-600: #0077ed;
  --focus: rgba(0, 113, 227, 0.3);
  --success: #34c759;
  --success-surface: #e8fceb;
  --warning: #ff9f0a;
  --warning-surface: #fff5e6;
  --danger: #ff3b30;
  --danger-surface: #ffe5e5;
  --chip-bg: #1d1d1f;
  --chip-text: #f5f5f7;
  --shadow: 0 4px 24px rgba(0, 0, 0, 0.06); /* Softer, deeper shadow */
  --radius: 12px; /* Consistent corner radius */
  --transition-curve: cubic-bezier(0.25, 1, 0.5, 1); /* "Snappy" physics */
}

/* Respect system-level and desk themes */
@media (prefers-color-scheme: dark), .theme-dark, .frappe-dark {
  :root {
    --bg: #000000;
    --card-bg: #1c1c1e;
    --surface: #1c1c1e;
    --text: #f5f5f7;
    --muted: #86868b;
    --border: #424245;
    --primary: #2997ff;
    --primary-600: #0071e3;
    --focus: rgba(41, 151, 255, 0.3);
    --success: #30d158;
    --success-surface: #0a2e12;
    --warning: #ff9f0a;
    --warning-surface: #3d2600;
    --danger: #ff453a;
    --danger-surface: #3d0d0d;
    --chip-bg: #f5f5f7;
    --chip-text: #000000;
    --shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
  }
}

:global(body) {
  background-color: var(--bg);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.intake-wizard {
  display: flex;
  flex-direction: column;
  gap: 2rem; /* Increased gap */
  padding: 2.5rem; /* Increased padding */
  max-width: 1400px; /* Wider max-width for enterprise feel */
  margin: 0 auto;
  color: var(--text);
}

.wizard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2rem;
}

.wizard-title-block h1 {
  font-size: 2.25rem; /* Larger heading */
  font-weight: 700;
  margin: 0;
  color: var(--text);
}

.wizard-eyebrow {
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--primary);
  margin: 0 0 0.5rem;
}

.wizard-subtitle {
  margin: 0.5rem 0 0;
  color: var(--muted);
  max-width: 620px;
  font-size: 1rem;
}

.wizard-hints {
  display: flex;
  gap: 1.5rem;
  font-size: 0.875rem;
  color: var(--muted);
  margin-top: 1rem;
  flex-wrap: wrap;
}

.wizard-meta {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  align-items: flex-end;
  flex-shrink: 0;
}

.session-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background-color: var(--chip-bg);
  color: var(--chip-text);
  padding: 0.5rem 1rem;
  border-radius: 999px;
  font-size: 0.875rem;
  font-weight: 600;
}

.chip-label {
  opacity: 0.6;
}

.autosave-status {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.75rem;
  border-radius: 999px;
  font-size: 0.875rem;
  font-weight: 500;
  background-color: var(--surface);
  color: var(--muted);
  transition: background-color 0.3s ease, color 0.3s ease;
}

.autosave-status .status-dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  background-color: currentColor;
}

.autosave-status.status-saving {
  background-color: var(--warning-surface);
  color: var(--warning);
}
.autosave-status.status-success {
  background-color: var(--success-surface);
  color: var(--success);
}
.autosave-status.status-error {
  background-color: var(--danger-surface);
  color: var(--danger);
}

/* SLA Indicator Styles use theme tokens */
.sla-indicator {
  border-radius: 999px;
  padding: 0.5rem 1rem;
  font-weight: 600;
  display: flex;
  gap: 0.5rem;
  align-items: center;
}
.sla-label { text-transform: uppercase; font-size: 0.75rem; }
.sla-text { font-size: 0.875rem; }
.sla-good { background-color: var(--success-surface); color: var(--success); }
.sla-warning { background-color: var(--warning-surface); color: var(--warning); }
.sla-critical { background-color: var(--danger-surface); color: var(--danger); }
.sla-none, .sla-pending { background-color: var(--surface); color: var(--muted); }


.wizard-layout {
  display: grid;
  grid-template-columns: minmax(280px, 320px) 1fr;
  gap: 2rem;
  align-items: flex-start;
}

.wizard-progress {
  background-color: var(--card-bg);
  border-radius: 0.75rem;
  border: 1px solid var(--border);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  position: sticky;
  top: 2rem;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.progress-label {
  font-size: 0.875rem;
  color: var(--muted);
}

.progress-value {
  font-size: 1.75rem;
  font-weight: 700;
}

.progress-steps {
  font-size: 0.875rem;
  color: var(--muted);
}

.progress-bar {
  height: 0.5rem;
  border-radius: 999px;
  background-color: var(--border);
}

.progress-fill {
  height: 100%;
  background-color: var(--primary);
  border-radius: 999px;
  transition: width 0.4s ease;
}

.step-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.step-button {
  width: 100%;
  border: 1px solid transparent;
  background-color: transparent;
  padding: 1rem;
  border-radius: var(--radius);
  display: flex;
  align-items: center;
  gap: 1rem;
  cursor: pointer;
  text-align: left;
  transition: all 0.3s var(--transition-curve);
  position: relative;
}

.step-button:hover:not(:disabled) {
  background-color: var(--surface);
  transform: scale(1.01);
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}

.step-button:active:not(:disabled) {
  transform: scale(0.98);
}

.step-button:disabled {
  cursor: not-allowed;
  opacity: 0.4;
  filter: grayscale(100%);
}

.step-button:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px var(--focus);
}

.step-index {
  width: 2.5rem;
  height: 2.5rem;
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background-color: var(--border);
  color: var(--muted);
  font-weight: 600;
  font-size: 1rem;
  transition: all 0.3s var(--transition-curve);
}

.step-label {
  font-weight: 600;
  font-size: 1.05rem;
  color: var(--text);
  letter-spacing: -0.01em;
}

.step-description {
  font-size: 0.85rem;
  color: var(--muted);
  line-height: 1.4;
  margin-top: 0.1rem;
}

.step-status {
  margin-left: auto;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--muted);
  background-color: var(--bg);
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
}

.active .step-button {
  background-color: var(--surface);
  border-color: var(--primary);
  box-shadow: 0 4px 12px var(--focus);
}
.active .step-index {
  background-color: var(--primary);
  color: var(--card-bg);
}
.active .step-label {
  color: var(--primary);
}

.complete .step-index {
  background-color: var(--success);
  color: var(--card-bg);
}

.progress-footer {
  border-top: 1px solid var(--border);
  padding-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.progress-help {
  margin: 0;
  font-size: 0.875rem;
  color: var(--muted);
}

.link-button {
  border: none;
  background: none;
  color: var(--primary);
  cursor: pointer;
  font-weight: 600;
  padding: 0;
  text-align: left;
}

.link-button:hover {
  text-decoration: underline;
}

.wizard-content {
  background-color: var(--card-bg);
  border-radius: 0.75rem;
  border: 1px solid var(--border);
  padding: 2.5rem; /* More padding */
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  min-height: 540px;
  outline: none;
}

.step-fade-enter-active,
.step-fade-leave-active {
  transition: opacity 0.4s var(--transition-curve), transform 0.4s var(--transition-curve);
}
.step-fade-enter-from {
  opacity: 0;
  transform: translateY(15px) scale(0.99);
}
.step-fade-leave-to {
  opacity: 0;
  transform: translateY(-15px) scale(0.99);
}

.wizard-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--card-bg);
  border-radius: var(--radius);
  padding: 1.25rem 2rem;
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
  backdrop-filter: blur(10px);
}

.footer-support {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.support-label {
  font-weight: 500;
  color: var(--muted);
}

.footer-actions {
  display: flex;
  gap: 1rem;
}

/* --- Universal Button Styles --- */
.primary,
.secondary {
  border-radius: 0.5rem;
  padding: 0.65rem 1.25rem;
  font-size: 0.95rem;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.primary {
  background-color: var(--primary);
  color: var(--card-bg);
  border: 1px solid var(--primary);
  box-shadow: var(--shadow);
}
.primary:hover {
  background-color: var(--primary-600);
}
.primary[disabled] {
  background-color: color-mix(in srgb, var(--primary) 40%, var(--card-bg));
  border-color: color-mix(in srgb, var(--primary) 40%, var(--card-bg));
  cursor: not-allowed;
  box-shadow: none;
}

.secondary {
  background-color: var(--card-bg);
  border: 1px solid var(--border);
  color: var(--text);
  box-shadow: var(--shadow);
}
.secondary:hover {
  border-color: color-mix(in srgb, var(--border) 30%, var(--primary));
  color: var(--text);
}

/* Submission Summary Styles */
.submission-summary,
.submission-error {
  border-radius: 0.75rem;
  padding: 1.5rem 2rem;
  background-color: var(--bg);
  border: 1px solid var(--border);
}

.submission-summary h2, .submission-error h2 {
    margin: 0 0 0.5rem 0;
}

.submission-error {
  border-left: 4px solid var(--danger);
  background-color: var(--danger-surface);
}

.submission-summary ul {
  list-style: none;
  padding: 0;
  margin: 1rem 0 0;
}

.submission-summary li + li {
    margin-top: 0.5rem;
}

.submission-summary a {
  color: var(--primary);
  text-decoration: none;
  font-weight: 600;
}
.submission-summary a:hover {
    text-decoration: underline;
}

/* Responsive adjustments */
@media (max-width: 1024px) {
  .wizard-layout {
    grid-template-columns: 1fr;
  }
  .wizard-progress {
    order: -1; /* Move progress bar to the top on smaller screens */
    position: static;
  }
  .wizard-header {
    flex-direction: column;
    gap: 1rem;
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
    padding: 1.5rem;
  }
  .wizard-footer {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  .footer-actions {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
