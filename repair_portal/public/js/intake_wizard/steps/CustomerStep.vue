<template>
  <section aria-labelledby="customer-heading" class="wizard-section">
    <header class="section-header">
      <div>
        <h2 id="customer-heading">Customer Details</h2>
        <p class="section-hint">
          Capture the primary point of contact, billing email, and best phone number. We validate entries in real time so the
          service team can reach the client without delays.
        </p>
      </div>
      <div class="status-cluster" aria-live="polite">
        <span v-if="local.name" class="status-pill success">Linked to {{ local.name }}</span>
        <span v-else class="status-pill neutral">New customer</span>
      </div>
    </header>

    <div class="content-grid">
      <article class="card">
        <h3>Contact Essentials</h3>
        <div class="field-grid">
          <label :class="{ 'has-error': errors.customer_name }">
            <span>Customer Name</span>
            <input
              v-model.trim="local.customer_name"
              type="text"
              required
              autocomplete="name"
              :aria-invalid="Boolean(errors.customer_name)"
              @input="onChange"
              @blur="validate"
            />
            <small class="field-hint">Use the legal name for contracts. Nicknames can be stored in player profile.</small>
            <p v-if="errors.customer_name" class="field-error">{{ errors.customer_name }}</p>
          </label>
          <label :class="{ 'has-error': errors.email }">
            <span>Email</span>
            <input
              v-model.trim="local.email"
              type="email"
              required
              autocomplete="email"
              :aria-invalid="Boolean(errors.email)"
              @input="onChange"
              @blur="validate"
            />
            <small class="field-hint">Confirmation receipts and repair updates will route here.</small>
            <p v-if="errors.email" class="field-error">{{ errors.email }}</p>
          </label>
          <label :class="{ 'has-error': errors.phone }">
            <span>Phone</span>
            <input
              v-model.trim="local.phone"
              type="tel"
              required
              autocomplete="tel"
              :aria-invalid="Boolean(errors.phone)"
              @input="onChange"
              @blur="validate"
            />
            <small class="field-hint">Include country code for international clients.</small>
            <p v-if="errors.phone" class="field-error">{{ errors.phone }}</p>
          </label>
        </div>
      </article>

      <article class="card lookup-card">
        <h3>Find Existing Customer</h3>
        <p class="lookup-hint">Type at least two characters to search name, email, or phone.</p>
        <div class="search-control">
          <input
            v-model="searchTerm"
            type="search"
            placeholder="Search customer directory"
            @input="debouncedSearch"
            aria-label="Search existing customers"
          />
          <span v-if="searchLoading" class="loader" aria-hidden="true"></span>
        </div>
        <ul v-if="customerResults.length" class="search-results" role="listbox">
          <li v-for="row in customerResults" :key="row.name">
            <button type="button" class="result-button" @click="selectCustomer(row)">
              <div class="result-main">
                <span class="result-name">{{ row.customer_name }}</span>
                <span class="result-meta">{{ row.customer_type }}</span>
              </div>
              <div class="result-secondary">
                <span>{{ row.email_id || 'No email on file' }}</span>
                <span>{{ row.mobile_no || row.phone || '—' }}</span>
              </div>
            </button>
          </li>
        </ul>
        <p v-else class="lookup-empty">No recent matches. Continue with a new customer.</p>
      </article>
    </div>

    <article class="card address-card">
      <h3>Billing Address</h3>
      <div class="field-grid">
        <label>
          <span>Address Line 1</span>
          <input v-model.trim="local.address_line1" type="text" autocomplete="address-line1" @input="onChange" />
        </label>
        <label>
          <span>Address Line 2</span>
          <input v-model.trim="local.address_line2" type="text" autocomplete="address-line2" @input="onChange" />
        </label>
        <label>
          <span>City</span>
          <input v-model.trim="local.city" type="text" autocomplete="address-level2" @input="onChange" />
        </label>
        <label>
          <span>State / Region</span>
          <input v-model.trim="local.state" type="text" autocomplete="address-level1" @input="onChange" />
        </label>
        <label>
          <span>Postal Code</span>
          <input v-model.trim="local.pincode" type="text" autocomplete="postal-code" @input="onChange" />
        </label>
        <label>
          <span>Country</span>
          <input v-model.trim="local.country" type="text" autocomplete="country" @input="onChange" />
        </label>
      </div>
    </article>

    <footer class="actions">
      <div class="action-left">
        <button type="button" class="secondary" @click="resetForm">Reset</button>
      </div>
      <div class="action-right">
        <button type="button" class="primary" @click="createOrUpdateCustomer" :disabled="!isValid">Save Customer</button>
      </div>
    </footer>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from "vue";

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const phonePattern = /^[0-9()+\-\s]{7,}$/;

const props = defineProps({
  modelValue: { type: Object, default: () => ({}) },
  fetchCustomers: { type: Function, required: true },
  upsertCustomer: { type: Function, required: true },
  loading: { type: Boolean, default: false },
});

const emit = defineEmits(["update:modelValue", "validity-change", "log"]);

const local = reactive({
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
});

const errors = reactive({ customer_name: null, email: null, phone: null });
const customerResults = reactive([]);
const searchTerm = ref("");
const searchLoading = ref(false);
let debounceTimer = null;

const isValid = computed(() => validate(false));

watch(
  () => props.modelValue,
  (value) => {
    Object.assign(local, { ...local, ...value });
    validate(false);
  },
  { immediate: true, deep: true }
);

function emitUpdate() {
  emit("update:modelValue", { ...local });
}

function onChange() {
  emitUpdate();
  validate(false);
}

function clearErrors() {
  Object.keys(errors).forEach((key) => {
    errors[key] = null;
  });
}

function validate(show = true) {
  clearErrors();
  if (!local.customer_name) {
    errors.customer_name = "Customer name is required.";
  }
  if (!local.email) {
    errors.email = "Email is required.";
  } else if (!emailPattern.test(local.email)) {
    errors.email = "Enter a valid email address.";
  }
  if (!local.phone) {
    errors.phone = "Phone number is required.";
  } else if (!phonePattern.test(local.phone)) {
    errors.phone = "Include only digits, spaces, +, or - characters.";
  }
  const valid = !errors.customer_name && !errors.email && !errors.phone;
  if (show) {
    emit("validity-change", valid);
  } else {
    emit("validity-change", valid);
  }
  return valid;
}

function selectCustomer(row) {
  Object.assign(local, {
    name: row.name,
    customer_name: row.customer_name,
    email: row.email_id || local.email,
    phone: row.mobile_no || row.phone || local.phone,
  });
  emitUpdate();
  validate();
  emit("log", { type: "customer_selected", customer: row.name });
}

async function createOrUpdateCustomer() {
  if (!validate()) {
    return;
  }
  const response = await props.upsertCustomer({ ...local });
  if (response && response.customer) {
    local.name = response.customer;
    emitUpdate();
    emit("log", { type: "customer_saved", customer: response.customer });
  }
}

function resetForm() {
  Object.assign(local, {
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
  });
  emitUpdate();
  validate();
}

const debouncedSearch = () => {
  if (debounceTimer) {
    clearTimeout(debounceTimer);
  }
  debounceTimer = setTimeout(async () => {
    if (!searchTerm.value || searchTerm.value.length < 2) {
      customerResults.splice(0, customerResults.length);
      return;
    }
    searchLoading.value = true;
    try {
      const rows = (await props.fetchCustomers(searchTerm.value)) || [];
      customerResults.splice(0, customerResults.length, ...rows);
    } finally {
      searchLoading.value = false;
    }
  }, 300);
};

onMounted(() => {
  validate(false);
});
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
  color: #1e293b;
}

.section-hint {
  margin: 0.25rem 0 0;
  color: #64748b;
  max-width: 620px;
}

.card {
  background-color: #ffffff;
  border-radius: 0.75rem;
  border: 1px solid #e2e8f0;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.card h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.field-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.25rem;
}

/* --- Form Element Styles --- */
label {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  font-weight: 500;
  font-size: 0.875rem;
  color: #334155;
}

input {
  padding: 0.65rem 0.875rem;
  border-radius: 0.5rem;
  border: 1px solid #cbd5e1;
  background-color: #ffffff;
  font-size: 1rem;
  color: #1e293b;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

input:focus-visible {
  outline: none;
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.2);
}

.field-hint {
  font-weight: 400;
  font-size: 0.875rem;
  color: #64748b;
}

.field-error {
  margin: 0;
  font-size: 0.875rem;
  color: #dc2626;
}

.has-error input {
  border-color: #fca5a5;
  background-color: #fef2f2;
}
.has-error input:focus-visible {
  border-color: #dc2626;
  box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.2);
}

/* --- Status & Lookup Styles --- */
.status-pill {
  border-radius: 999px;
  padding: 0.375rem 0.875rem;
  font-size: 0.875rem;
  font-weight: 500;
}
.status-pill.success {
  background-color: #dcfce7;
  color: #166534;
}
.status-pill.neutral {
  background-color: #f1f5f9;
  color: #475569;
}

.lookup-card {
  background-color: #f8fafc; /* Subtle background for lookup */
}

.lookup-hint {
  margin: 0;
  color: #64748b;
  font-size: 0.875rem;
}

.search-control {
  position: relative;
}

.search-control input[type="search"] {
  width: 100%;
}

.loader {
  position: absolute;
  right: 0.875rem;
  top: 50%;
  width: 1.125rem;
  height: 1.125rem;
  margin-top: -0.5625rem;
  border-radius: 50%;
  border: 2px solid #cbd5e1;
  border-top-color: #4f46e5;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.search-results {
  list-style: none;
  padding: 0;
  margin: 0.5rem 0 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.result-button {
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  padding: 0.875rem;
  background-color: #ffffff;
  cursor: pointer;
  width: 100%;
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.25rem;
  text-align: left;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.result-button:hover {
  border-color: #4f46e5;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}

.result-main {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.result-name {
  font-weight: 600;
  color: #1e293b;
}

.result-meta {
  color: #64748b;
  font-size: 0.8rem;
  background-color: #f1f5f9;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
}

.result-secondary {
  display: flex;
  flex-direction: column;
  font-size: 0.875rem;
  color: #475569;
}

.lookup-empty {
  margin: 0;
  font-size: 0.875rem;
  color: #64748b;
  text-align: center;
  padding: 1rem;
  background-color: #f1f5f9;
  border-radius: 0.5rem;
}

/* --- Actions Footer --- */
.actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-top: 1rem; /* Add some space above actions */
  padding-top: 1.5rem;
  border-top: 1px solid #e2e8f0;
}

/* --- Shared Button Styles from App.vue are assumed --- */
.primary,
.secondary {
  border-radius: 0.5rem;
  padding: 0.65rem 1.25rem;
  font-size: 0.95rem;
  cursor: pointer;
  font-weight: 600;
}

.primary {
  background-color: #4f46e5;
  color: #ffffff;
  border: 1px solid #4f46e5;
}
.primary[disabled] {
  background-color: #a5b4fc;
  border-color: #a5b4fc;
  cursor: not-allowed;
}

.secondary {
  background-color: #ffffff;
  border: 1px solid #cbd5e1;
  color: #334155;
}
</style>
