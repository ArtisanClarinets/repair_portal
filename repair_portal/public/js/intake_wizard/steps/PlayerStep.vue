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
          <label :class="{ 'has-error': errors.primary_phone }">
            <span>Primary Phone</span>
            <input
              v-model.trim="local.primary_phone"
              type="tel"
              required
              @input="update"
              :readonly="local.sameAsCustomer"
              :aria-invalid="Boolean(errors.primary_phone)"
            />
            <small class="field-hint">Direct line for urgent setup updates.</small>
            <p v-if="errors.primary_phone" class="field-error">{{ errors.primary_phone }}</p>
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
        <label>
          <span>Primary Phone</span>
          <input v-model.trim="local.primary_phone" type="tel" readonly />
        </label>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, reactive, ref, watch } from "vue";

const phonePattern = /^[0-9()+\-\s]{7,}$/;

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
  primary_phone: "",
  player_level: "Amateur/Hobbyist",
  profile: null,
});
const searchTerm = ref("");
const results = reactive([]);
const loading = ref(false);
let debounceTimer = null;

const errors = reactive({ player_name: null, primary_email: null, primary_phone: null, player_level: null });

const isValid = computed(() => {
  if (local.sameAsCustomer) {
    return Boolean(local.player_name && local.primary_email && local.primary_phone && phonePattern.test(local.primary_phone));
  }
  return Boolean(
    local.player_name &&
      local.primary_email &&
      local.primary_phone &&
      phonePattern.test(local.primary_phone) &&
      local.player_level
  );
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
    local.primary_phone = props.customer.phone || props.customer.mobile_no || "";
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
    primary_phone: row.primary_phone || local.primary_phone,
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
  if (!local.primary_phone) {
    errors.primary_phone = "Primary phone is required.";
  } else if (!phonePattern.test(local.primary_phone)) {
    errors.primary_phone = "Include only digits, spaces, +, or - characters.";
  }
  if (!local.sameAsCustomer && !local.player_level) {
    errors.player_level = "Select a player level.";
  }
  const valid = local.sameAsCustomer
    ? Boolean(local.player_name && local.primary_email && local.primary_phone && !errors.primary_phone)
    : Boolean(
        local.player_name &&
          local.primary_email &&
          local.primary_phone &&
          !errors.primary_phone &&
          local.player_level
      );
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
.status-cluster {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}
.section-header h2 { margin: 0; font-size: 1.5rem; color: var(--text); }
.section-hint { margin: 0.25rem 0 0; color: var(--muted); max-width: 620px; }

.card {
  background-color: var(--card-bg);
  border-radius: 0.75rem;
  border: 1px solid var(--border);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}
.card h3 { margin: 0; font-size: 1.125rem; font-weight: 600; color: var(--text); }

.content-grid {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 1.5rem;
}

.field-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.25rem;
}

/* --- Status Pill Styles --- */
.status-pill { border-radius: 999px; padding: 0.375rem 0.875rem; font-size: 0.875rem; font-weight: 500; }
.status-pill--success { background-color: var(--success-surface); color: var(--success); }
.status-pill--neutral { background-color: color-mix(in srgb, var(--primary) 8%, var(--surface)); color: var(--primary-600); }
.status-pill--muted { background-color: var(--surface); color: var(--muted); }

/* --- Checkbox Switch --- */
.checkbox {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 500;
  background-color: var(--bg);
  padding: 0.75rem 1.25rem;
  border-radius: 0.5rem;
  border: 1px solid var(--border);
}
.checkbox input { width: 1.25rem; height: 1.25rem; }

/* --- Form Element Styles --- */
label { display: flex; flex-direction: column; gap: 0.5rem; font-weight: 500; font-size: 0.875rem; color: color-mix(in srgb, var(--text) 92%, var(--muted)); }
input, select { padding: 0.65rem 0.875rem; border-radius: 0.5rem; border: 1px solid var(--border); background-color: var(--card-bg); font-size: 1rem; color: var(--text); }
input:focus-visible, select:focus-visible { outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px var(--focus); }
.field-hint { font-weight: 400; font-size: 0.875rem; color: var(--muted); }
.field-error { margin: 0; font-size: 0.875rem; color: var(--danger); }
.has-error input, .has-error select { border-color: color-mix(in srgb, var(--danger) 30%, var(--border)); }

/* --- Lookup Card --- */
.lookup-card { background-color: var(--bg); }
.search-control { position: relative; }
.loader { position: absolute; right: 0.875rem; top: 50%; width: 1.125rem; height: 1.125rem; margin-top: -0.5625rem; border-radius: 50%; border: 2px solid var(--border); border-top-color: var(--primary); animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.search-results { list-style: none; padding: 0; margin: 0.5rem 0 0; display: flex; flex-direction: column; gap: 0.5rem; }
.result-button { border: 1px solid var(--border); border-radius: 0.5rem; padding: 0.75rem; background-color: var(--card-bg); cursor: pointer; display: flex; justify-content: space-between; align-items: center; }
.result-name { font-weight: 600; color: var(--text); }
.result-email { display: block; font-size: 0.875rem; color: var(--muted); }
.result-meta { font-size: 0.8rem; color: var(--muted); }
.lookup-empty { margin: 0; color: var(--muted); }

/* --- Actions --- */
.actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  margin-top: auto; /* Push actions to the bottom of the card */
  padding-top: 1.5rem;
  border-top: 1px solid var(--border);
}

.primary, .secondary { border-radius: 0.5rem; padding: 0.65rem 1.25rem; font-size: 0.95rem; cursor: pointer; font-weight: 600; }
.primary { background-color: var(--primary); border: 1px solid var(--primary); color: var(--card-bg); }
.primary[disabled] { background-color: color-mix(in srgb, var(--primary) 40%, var(--card-bg)); border-color: color-mix(in srgb, var(--primary) 40%, var(--card-bg)); cursor: not-allowed; }
.secondary { background-color: var(--card-bg); border: 1px solid var(--border); color: var(--text); }

.saved-pill { background-color: var(--success-surface); color: var(--success); padding: 0.375rem 0.75rem; border-radius: 999px; font-size: 0.875rem; font-weight: 500;}

.same-as-customer { background-color: var(--bg); }
</style>
