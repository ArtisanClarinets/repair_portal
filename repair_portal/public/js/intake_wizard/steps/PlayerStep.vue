<template>
  <section aria-labelledby="player-heading" class="wizard-section">
    <h2 id="player-heading">Player Profile</h2>
    <p class="section-hint">Link the instrument to a player profile or reuse the customer information.</p>

    <label class="checkbox">
      <input type="checkbox" v-model="local.sameAsCustomer" @change="syncWithCustomer" />
      Player is the same as the customer
    </label>

    <div v-if="!local.sameAsCustomer" class="search-panel">
      <label class="search-label">
        Search Player Profiles
        <input v-model="searchTerm" type="search" placeholder="Search players" @input="debouncedSearch" />
      </label>
      <ul v-if="results.length" class="search-results">
        <li v-for="row in results" :key="row.name">
          <button type="button" class="result-button" @click="selectPlayer(row)">
            <span>{{ row.player_name }}</span>
            <span class="muted">{{ row.primary_email }}</span>
          </button>
        </li>
      </ul>
    </div>

    <div class="form-grid">
      <label>
        Player Name
        <input v-model.trim="local.player_name" type="text" required @input="update" :readonly="local.sameAsCustomer" />
      </label>
      <label>
        Preferred Name
        <input v-model.trim="local.preferred_name" type="text" @input="update" :readonly="local.sameAsCustomer" />
      </label>
      <label>
        Primary Email
        <input v-model.trim="local.primary_email" type="email" required @input="update" :readonly="local.sameAsCustomer" />
      </label>
      <label>
        Player Level
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
      </label>
    </div>

    <div class="actions" v-if="!local.sameAsCustomer">
      <button type="button" class="primary" @click="savePlayer" :disabled="!isValid">Save Player Profile</button>
      <span v-if="local.profile" class="saved-pill">Linked to {{ local.profile }}</span>
    </div>
  </section>
</template>

<script setup>
import { reactive, ref, watch, computed } from "vue";

const props = defineProps({
  modelValue: { type: Object, default: () => ({ sameAsCustomer: true }) },
  customer: { type: Object, default: () => ({}) },
  searchPlayer: { type: Function, required: true },
  upsertPlayer: { type: Function, required: true },
});

const emit = defineEmits(["update:modelValue", "validity-change", "log"]);


const isValid = computed(() => {
  if (local.sameAsCustomer) {
    return Boolean(local.player_name && local.primary_email);
  }
  return Boolean(local.player_name && local.primary_email && local.player_level);
});
const local = reactive({
  sameAsCustomer: true,
  player_name: "",
  preferred_name: "",
  primary_email: "",
  player_level: "",
  profile: null,
});
const searchTerm = ref("");
const results = reactive([]);
let debounceTimer = null;

watch(
  () => props.modelValue,
  (value) => {
    Object.assign(local, { ...local, ...value });
    if (local.sameAsCustomer) {
      syncWithCustomer();
    }
    validate();
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
    local.primary_email = props.customer.email || "";
    local.player_level = local.player_level || "Amateur/Hobbyist";
  }
  update();
}

function update() {
  emit("update:modelValue", { ...local });
  validate();
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
    const rows = (await props.searchPlayer(searchTerm.value)) || [];
    results.splice(0, results.length, ...rows);
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

function validate() {
  if (local.sameAsCustomer) {
    emit("validity-change", Boolean(local.player_name && local.primary_email));
    return true;
  }
  const valid = isValid.value;
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
select, input {
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  border: 1px solid #d1d5db;
}
.checkbox {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 600;
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
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.result-button {
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  padding: 0.5rem 0.75rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  cursor: pointer;
}
.muted {
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
