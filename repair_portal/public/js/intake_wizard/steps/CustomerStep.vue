<template>
  <section aria-labelledby="customer-heading" class="wizard-section">
    <h2 id="customer-heading">Customer Details</h2>
    <p class="section-hint">Search for an existing customer or add a new profile.</p>

    <div class="form-grid">
      <label>
        Customer Name
        <input v-model.trim="local.customer_name" type="text" required @input="onChange" />
      </label>
      <label>
        Email
        <input v-model.trim="local.email" type="email" required @input="onChange" />
      </label>
      <label>
        Phone
        <input v-model.trim="local.phone" type="tel" required @input="onChange" />
      </label>
      <label>
        Address Line 1
        <input v-model.trim="local.address_line1" type="text" @input="onChange" />
      </label>
      <label>
        City
        <input v-model.trim="local.city" type="text" @input="onChange" />
      </label>
      <label>
        State
        <input v-model.trim="local.state" type="text" @input="onChange" />
      </label>
      <label>
        Country
        <input v-model.trim="local.country" type="text" @input="onChange" />
      </label>
    </div>

    <div class="search-panel">
      <label class="search-label">
        Search Existing Customer
        <input
          v-model="searchTerm.value"
          type="search"
          placeholder="Type at least 2 characters"
          @input="debouncedSearch"
          aria-label="Search existing customers"
        />
      </label>
      <ul v-if="customerResults.length" class="search-results" role="listbox">
        <li v-for="row in customerResults" :key="row.name">
          <button type="button" @click="selectCustomer(row)" class="result-button">
            <span class="result-name">{{ row.customer_name }}</span>
            <span class="result-meta">{{ row.customer_type }}</span>
          </button>
        </li>
      </ul>
    </div>

    <div class="actions">
      <button type="button" class="primary" @click="createOrUpdateCustomer" :disabled="!isValid">
        Save Customer
      </button>
      <span v-if="local.name" class="saved-pill" aria-live="polite">Linked to {{ local.name }}</span>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from "vue";

const props = defineProps({
  modelValue: { type: Object, default: () => ({}) },
  fetchCustomers: { type: Function, required: true },
  upsertCustomer: { type: Function, required: true },
  loading: { type: Boolean, default: false },
});

const emit = defineEmits(["update:modelValue", "validity-change", "log"]);

const isValid = computed(() => Boolean(local.customer_name && local.email && local.phone));

const local = reactive({
  name: null,
  customer_name: "",
  email: "",
  phone: "",
  address_line1: "",
  city: "",
  state: "",
  country: "United States",
});

const customerResults = reactive([]);
const searchTerm = ref("");
let debounceTimer = null;

watch(
  () => props.modelValue,
  (value) => {
    Object.assign(local, { ...local, ...value });
    validate();
  },
  { immediate: true, deep: true }
);

function emitUpdate() {
  emit("update:modelValue", { ...local });
}

function onChange() {
  emitUpdate();
  validate();
}

function validate() {
  const valid = isValid.value;
  emit("validity-change", valid);
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
  emit("validity-change", true);
}

async function createOrUpdateCustomer() {
  if (!validate()) {
    return;
  }
  const response = await props.upsertCustomer({ ...local });
  if (response && response.customer) {
    local.name = response.customer;
    emitUpdate();
    emit("log", { type: "customer_saved" });
  }
}

const debouncedSearch = () => {
  if (debounceTimer) {
    clearTimeout(debounceTimer);
  }
  debounceTimer = setTimeout(async () => {
    if (searchTerm.value.length < 2) {
      customerResults.splice(0, customerResults.length);
      return;
    }
    const rows = (await props.fetchCustomers(searchTerm.value)) || [];
    customerResults.splice(0, customerResults.length, ...rows);
  }, 300);
};

onMounted(() => {
  validate();
});
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
input {
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  border: 1px solid #d1d5db;
  font-size: 0.95rem;
}
.search-panel {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.search-results {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.5rem;
}
.result-button {
  width: 100%;
  display: flex;
  justify-content: space-between;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: #fff;
  cursor: pointer;
}
.result-name {
  font-weight: 600;
}
.result-meta {
  color: #6b7280;
  font-size: 0.8rem;
}
.actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.primary {
  background: #2563eb;
  border: none;
  color: #fff;
  padding: 0.65rem 1.25rem;
  border-radius: 0.5rem;
  cursor: pointer;
}
.primary[disabled] {
  background: #93c5fd;
  cursor: not-allowed;
}
.saved-pill {
  background: #e6ffed;
  color: #065f46;
  padding: 0.4rem 0.75rem;
  border-radius: 999px;
  font-size: 0.85rem;
}
.section-hint {
  margin: 0;
  color: #6b7280;
}
</style>
