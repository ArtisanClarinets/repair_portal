<template>
  <section aria-labelledby="player-heading" class="wizard-section">
    <header class="section-header">
      <div>
        <h2 id="player-heading">Player Profile</h2>
        <p class="section-hint">
          Clarify who plays the instrument so service notes, resistance preferences, and tonal requests stay personal.
        </p>
      </div>
      <div class="status-cluster" aria-live="polite">
        <span class="status-pill" :class="statusClass">{{ statusMessage }}</span>
      </div>
    </header>

    <label class="checkbox" role="switch" :aria-checked="local.sameAsCustomer">
      <input type="checkbox" v-model="local.sameAsCustomer" @change="syncWithCustomer" />
      Player is the same as the customer
    </label>

    <div v-if="!local.sameAsCustomer" class="content-grid">
      <article class="card lookup-card">
        <h3>Search Player Directory</h3>
        <p class="section-hint">Match existing Player Profiles by name or email.</p>
        <div class="search-control">
          <input v-model="searchTerm" type="search" placeholder="Search players" @input="debouncedSearch" />
          <span v-if="loading" class="loader" aria-hidden="true"></span>
        </div>
        <ul v-if="results.length" class="search-results" role="listbox">
          <li v-for="row in results" :key="row.name">
            <button type="button" class="result-button" @click="selectPlayer(row)">
              <div>
                <span class="result-name">{{ row.player_name }}</span>
                <span class="result-email">{{ row.primary_email }}</span>
              </div>
              <span class="result-meta">{{ row.name }}</span>
            </button>
          </li>
        </ul>
        <p v-else class="lookup-empty">No matches yet. Enter details below to create a new profile.</p>
      </article>

      <article class="card">
        <h3>Player Insights</h3>
        <div class="field-grid">
          <label :class="{ 'has-error': errors.player_name }">
            <span>Player Name</span>
            <input
              v-model.trim="local.player_name"
              type="text"
              required
              @input="update"
              :readonly="local.sameAsCustomer"
              :aria-invalid="Boolean(errors.player_name)"
            />
            <small class="field-hint">Full name for certificates and personalization.</small>
            <p v-if="errors.player_name" class="field-error">{{ errors.player_name }}</p>
          </label>
          <label>
            <span>Preferred Name</span>
            <input v-model.trim="local.preferred_name" type="text" @input="update" :readonly="local.sameAsCustomer" />
          </label>
          <label :class="{ 'has-error': errors.primary_email }">
            <span>Primary Email</span>
            <input
              v-model.trim="local.primary_email"
              type="email"
              required
              @input="update"
              :readonly="local.sameAsCustomer"
              :aria-invalid="Boolean(errors.primary_email)"
            />
            <small class="field-hint">Used for practice feedback and tonal reports.</small>
            <p v-if="errors.primary_email" class="field-error">{{ errors.primary_email }}</p>
          </label>
          <label :class="{ 'has-error': errors.player_level }">
            <span>Player Level</span>
            <select v-model="local.player_level" @change="update" :disabled="local.sameAsCustomer">
              <option disabled value="">Select level</option>
              <option>Student (Beginner)</option>
              <option>Student (Advanced)</option>
              <option>Amateur/Hobbyist</option>
              <option>University Student</option>
              <option>Professional (Orchestral)</option>
              <option>Professional (Jazz/Commercial)</option>
              <option>Educator</option>
              <option>Collector</option>
            </select>
            <p v-if="errors.player_level" class="field-error">{{ errors.player_level }}</p>
          </label>
        </div>
        <div class="actions">
          <button type="button" class="secondary" @click="clearPlayer" :disabled="!local.profile">Clear selection</button>
          <button type="button" class="primary" @click="savePlayer" :disabled="!isValid">Save Player Profile</button>
          <span v-if="local.profile" class="saved-pill">Linked to {{ local.profile }}</span>
        </div>
      </article>
    </div>

    <div v-else class="same-as-customer card">
      <p>The player details will mirror the customer record. You can still adjust level or preferred name if needed.</p>
      <div class="field-grid">
        <label>
          <span>Player Level</span>
          <select v-model="local.player_level" @change="update">
            <option>Student (Beginner)</option>
            <option>Student (Advanced)</option>
            <option>Amateur/Hobbyist</option>
            <option>University Student</option>
            <option>Professional (Orchestral)</option>
            <option>Professional (Jazz/Commercial)</option>
            <option>Educator</option>
            <option>Collector</option>
          </select>
        </label>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, reactive, ref, watch } from "vue";

const props = defineProps({
  modelValue: { type: Object, default: () => ({ sameAsCustomer: true }) },
  customer: { type: Object, default: () => ({}) },
  searchPlayer: { type: Function, required: true },
  upsertPlayer: { type: Function, required: true },
});

const emit = defineEmits(["update:modelValue", "validity-change", "log"]);

const local = reactive({
  sameAsCustomer: true,
  player_name: "",
  preferred_name: "",
  primary_email: "",
  player_level: "Amateur/Hobbyist",
  profile: null,
});
const searchTerm = ref("");
const results = reactive([]);
const loading = ref(false);
let debounceTimer = null;

const errors = reactive({ player_name: null, primary_email: null, player_level: null });

const isValid = computed(() => {
  if (local.sameAsCustomer) {
    return Boolean(local.player_name && local.primary_email);
  }
  return Boolean(local.player_name && local.primary_email && local.player_level);
});

const statusMessage = computed(() => {
  if (local.sameAsCustomer) {
    return "Mirroring customer details";
  }
  if (local.profile) {
    return `Linked to ${local.profile}`;
  }
  return "New player profile";
});

const statusClass = computed(() => {
  if (local.profile) return "status-pill--success";
  if (local.sameAsCustomer) return "status-pill--neutral";
  return "status-pill--muted";
});

watch(
  () => props.modelValue,
  (value) => {
    Object.assign(local, { ...local, ...value });
    if (local.sameAsCustomer) {
      syncWithCustomer();
    }
    validate(false);
  },
  { immediate: true, deep: true }
);

watch(
  () => props.customer,
  () => {
    if (local.sameAsCustomer) {
      syncWithCustomer();
    }
  },
  { deep: true }
);

function syncWithCustomer() {
  if (local.sameAsCustomer) {
    local.player_name = props.customer.customer_name || "";
    local.primary_email = props.customer.email || props.customer.email_id || "";
  }
  update();
}

function update() {
  emit("update:modelValue", { ...local });
  validate(false);
}

const debouncedSearch = () => {
  if (debounceTimer) {
    clearTimeout(debounceTimer);
  }
  debounceTimer = setTimeout(async () => {
    if (!searchTerm.value || searchTerm.value.length < 2) {
      results.splice(0, results.length);
      return;
    }
    loading.value = true;
    try {
      const rows = (await props.searchPlayer(searchTerm.value)) || [];
      results.splice(0, results.length, ...rows);
    } finally {
      loading.value = false;
    }
  }, 300);
};

function selectPlayer(row) {
  Object.assign(local, {
    profile: row.name,
    player_name: row.player_name,
    primary_email: row.primary_email,
    sameAsCustomer: false,
  });
  update();
  emit("log", { type: "player_selected", profile: row.name });
}

async function savePlayer() {
  if (!validate()) return;
  const response = await props.upsertPlayer({ ...local });
  if (response && response.player_profile) {
    local.profile = response.player_profile;
    emit("log", { type: "player_saved", profile: response.player_profile });
    update();
  }
}

function clearPlayer() {
  local.profile = null;
  update();
}

function clearErrors() {
  Object.keys(errors).forEach((key) => {
    errors[key] = null;
  });
}

function validate(show = true) {
  clearErrors();
  if (!local.player_name) {
    errors.player_name = "Player name is required.";
  }
  if (!local.primary_email) {
    errors.primary_email = "Primary email is required.";
  }
  if (!local.sameAsCustomer && !local.player_level) {
    errors.player_level = "Select a player level.";
  }
  const valid = local.sameAsCustomer
    ? Boolean(local.player_name && local.primary_email)
    : Boolean(local.player_name && local.primary_email && local.player_level);
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

.status-pill--neutral {
  background: #fef3c7;
  color: #92400e;
}

.status-pill--muted {
  background: #e2e8f0;
  color: #475569;
}

.checkbox {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 600;
  background: #f1f5f9;
  padding: 0.65rem 1rem;
  border-radius: 0.75rem;
}

.checkbox input {
  width: 1.25rem;
  height: 1.25rem;
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
select {
  padding: 0.6rem 0.85rem;
  border-radius: 0.75rem;
  border: 1px solid #cbd5f5;
  font-size: 0.95rem;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

input:focus-visible,
select:focus-visible {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2);
}

.field-hint {
  font-weight: 400;
  color: #94a3b8;
}

.field-error {
  margin: 0;
  font-size: 0.8rem;
  color: #b91c1c;
}

.has-error input,
.has-error select {
  border-color: #f87171;
}

.actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.primary,
.secondary {
  border-radius: 0.75rem;
  padding: 0.65rem 1.25rem;
  font-size: 0.95rem;
  cursor: pointer;
  font-weight: 600;
}

.primary {
  background: #2563eb;
  border: none;
  color: #fff;
}

.primary[disabled] {
  background: #93c5fd;
  cursor: not-allowed;
}

.secondary {
  background: transparent;
  border: 1px solid #cbd5f5;
  color: #1e3a8a;
}

.saved-pill {
  background: #dcfce7;
  color: #166534;
  padding: 0.4rem 0.75rem;
  border-radius: 999px;
  font-size: 0.85rem;
}

.lookup-card {
  position: relative;
}

.search-control {
  position: relative;
}

.search-control input {
  width: 100%;
}

.loader {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  width: 1rem;
  height: 1rem;
  margin-top: -0.5rem;
  border-radius: 50%;
  border: 2px solid #cbd5f5;
  border-top-color: #2563eb;
  animation: spin 0.9s linear infinite;
}

.search-results {
  list-style: none;
  padding: 0;
  margin: 1rem 0 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.result-button {
  border: 1px solid #cbd5f5;
  border-radius: 0.75rem;
  padding: 0.75rem;
  background: #fff;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-name {
  font-weight: 600;
}

.result-email {
  display: block;
  font-size: 0.85rem;
  color: #64748b;
}

.result-meta {
  font-size: 0.75rem;
  color: #94a3b8;
}

.lookup-empty {
  margin: 0;
  color: #94a3b8;
}

.same-as-customer {
  background: #f8fafc;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
