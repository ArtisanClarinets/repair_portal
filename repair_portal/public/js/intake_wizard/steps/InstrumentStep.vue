<template>
  <section aria-labelledby="instrument-heading" class="wizard-section">
    <header class="section-header">
      <div>
        <h2 id="instrument-heading">Instrument Identity</h2>
        <p class="section-hint">
          Verify the instrument lineage, normalize the serial number, and confirm any brand mapping before service begins.
        </p>
      </div>
      <div class="status-cluster" aria-live="polite">
        <span class="status-pill" :class="serialStatusClass">{{ serialState.message }}</span>
      </div>
    </header>

    <div class="content-grid">
      <article class="card">
        <h3>Core Specifications</h3>
        <div class="field-grid">
          <label :class="{ 'has-error': errors.manufacturer }">
            <span>Manufacturer</span>
            <input
              v-model.trim="local.manufacturer"
              type="text"
              required
              @input="onChange"
              @blur="validate"
              :aria-invalid="Boolean(errors.manufacturer)"
            />
            <small class="field-hint">Apply the mapped brand if presented by the serial lookup.</small>
            <p v-if="errors.manufacturer" class="field-error">{{ errors.manufacturer }}</p>
          </label>
          <label :class="{ 'has-error': errors.model }">
            <span>Model</span>
            <input
              v-model.trim="local.model"
              type="text"
              required
              @input="onChange"
              @blur="validate"
              :aria-invalid="Boolean(errors.model)"
            />
            <small class="field-hint">Use the exact stamp or workshop naming convention.</small>
            <p v-if="errors.model" class="field-error">{{ errors.model }}</p>
          </label>
          <label :class="{ 'has-error': errors.serial_no }">
            <span>Serial Number</span>
            <input
              v-model.trim="local.serial_no"
              type="text"
              required
              autocomplete="off"
              @input="onChange"
              @blur="handleSerialLookup"
              :aria-invalid="Boolean(errors.serial_no)"
            />
            <small class="field-hint">Blur to run a duplicate check and normalization.</small>
            <p v-if="errors.serial_no" class="field-error">{{ errors.serial_no }}</p>
          </label>
          <label>
            <span>Clarinet Type</span>
            <select v-model="local.clarinet_type" @change="onChange">
              <option value="">Select type</option>
              <option>Soprano (Bb)</option>
              <option>Soprano (A)</option>
              <option>Soprano (Eb)</option>
              <option>Bass Clarinet</option>
              <option>Contra Alto</option>
              <option>Contra Bass</option>
              <option>Other</option>
            </select>
          </label>
          <label>
            <span>Body Material</span>
            <input v-model.trim="local.body_material" type="text" @input="onChange" />
          </label>
          <label>
            <span>Key Plating</span>
            <input v-model.trim="local.key_plating" type="text" @input="onChange" />
          </label>
        </div>
      </article>

      <article class="card insight-card">
        <h3>Serial Intelligence</h3>
        <ul class="insight-list">
          <li>
            <span class="insight-label">Normalized Serial</span>
            <span class="insight-value">{{ serialState.normalized || 'Pending lookup' }}</span>
          </li>
          <li>
            <span class="insight-label">Existing Instrument</span>
            <span class="insight-value">
              <template v-if="serialState.matched">
                Linked to {{ serialState.instrument?.manufacturer || 'instrument' }} {{ serialState.instrument?.model || '' }}
              </template>
              <template v-else>New instrument record</template>
            </span>
          </li>
          <li v-if="serialState.brandMapping">
            <span class="insight-label">Brand Mapping</span>
            <span class="insight-value mapping-pill">
              {{ serialState.brandMapping.input }} → {{ serialState.brandMapping.mapped }}
            </span>
          </li>
        </ul>
        <button type="button" class="secondary" @click="handleSerialLookup" :disabled="serialState.loading">
          {{ serialState.loading ? 'Checking…' : 'Re-run Serial Check' }}
        </button>
      </article>
    </div>

    <article class="card accessories-card">
      <div class="accessories-header">
        <h3>Accessories &amp; Extras</h3>
        <p class="section-hint">
          Document cases, mouthpieces, or bespoke components to ensure everything returns with the instrument.
        </p>
      </div>
      <form class="accessory-form" @submit.prevent="addAccessory">
        <input v-model.trim="accessoryInput" type="text" placeholder="Add accessory" />
        <button type="submit" class="secondary">Add</button>
      </form>
      <ul class="chip-list" role="list">
        <li v-for="(item, index) in local.accessories" :key="`${item}-${index}`" class="chip">
          <span>{{ item }}</span>
          <button type="button" aria-label="Remove accessory" @click="removeAccessory(index)">×</button>
        </li>
      </ul>
    </article>
  </section>
</template>

<script setup>
import { computed, reactive, ref, watch } from "vue";

const props = defineProps({
  modelValue: { type: Object, default: () => ({ accessories: [] }) },
  serialLookup: { type: Function, required: true },
});

const emit = defineEmits(["update:modelValue", "validity-change", "log"]);

const local = reactive({
  manufacturer: "",
  model: "",
  serial_no: "",
  clarinet_type: "",
  body_material: "",
  key_plating: "",
  accessories: [],
  item_code: "",
  item_name: "",
  brand_mapping: null,
});

const errors = reactive({ manufacturer: null, model: null, serial_no: null });
const accessoryInput = ref("");
const serialState = reactive({
  loading: false,
  message: "Serial not checked yet",
  normalized: "",
  matched: false,
  instrument: null,
  brandMapping: null,
});

const serialStatusClass = computed(() => {
  if (serialState.loading) return "status-pill--info";
  if (serialState.matched) return "status-pill--success";
  if (serialState.normalized) return "status-pill--neutral";
  return "status-pill--muted";
});

watch(
  () => props.modelValue,
  (value) => {
    const incoming = { accessories: [], brand_mapping: null, ...value };
    Object.assign(local, incoming);
    if (!Array.isArray(local.accessories)) {
      local.accessories = [];
    }
    validate(false);
  },
  { immediate: true, deep: true }
);

function emitUpdate() {
  emit("update:modelValue", { ...local, accessories: [...local.accessories], brand_mapping: local.brand_mapping });
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
  if (!local.manufacturer) {
    errors.manufacturer = "Manufacturer is required.";
  }
  if (!local.model) {
    errors.model = "Model is required.";
  }
  if (!local.serial_no) {
    errors.serial_no = "Serial number is required.";
  }
  const valid = !errors.manufacturer && !errors.model && !errors.serial_no;
  if (show) {
    emit("validity-change", valid);
  } else {
    emit("validity-change", valid);
  }
  return valid;
}

async function handleSerialLookup() {
  if (!local.serial_no) {
    validate();
    return;
  }
  serialState.loading = true;
  serialState.message = "Checking serial…";
  try {
    const response = await props.serialLookup(local.serial_no);
    serialState.normalized = response?.normalized_serial || local.serial_no;
    serialState.matched = Boolean(response?.match);
    serialState.instrument = response?.instrument || null;
    serialState.brandMapping = response?.brand_mapping || null;
    if (serialState.brandMapping) {
      local.manufacturer = serialState.brandMapping.mapped || local.manufacturer;
      local.brand_mapping = serialState.brandMapping;
    }
    if (serialState.matched) {
      serialState.message = "Linked to existing instrument";
    } else {
      serialState.message = "New instrument will be created";
    }
    emit("log", {
      type: "serial_lookup",
      match: serialState.matched,
      normalized: serialState.normalized,
    });
    emitUpdate();
    validate();
  } catch (error) {
    serialState.message = "Serial lookup failed";
  } finally {
    serialState.loading = false;
  }
}

function addAccessory() {
  if (!accessoryInput.value) {
    return;
  }
  local.accessories = [...local.accessories, accessoryInput.value];
  accessoryInput.value = "";
  emitUpdate();
}

function removeAccessory(index) {
  local.accessories = local.accessories.filter((_, i) => i !== index);
  emitUpdate();
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

.status-pill--info {
  background: #e0f2fe;
  color: #0369a1;
}

.status-pill--neutral {
  background: #ede9fe;
  color: #5b21b6;
}

.status-pill--muted {
  background: #e2e8f0;
  color: #475569;
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

.has-error input {
  border-color: #f87171;
}

.insight-card {
  background: #eef2ff;
}

.insight-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.insight-label {
  display: block;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #6366f1;
}

.insight-value {
  font-weight: 600;
  color: #312e81;
}

.mapping-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background: #dbeafe;
  padding: 0.25rem 0.5rem;
  border-radius: 999px;
}

.secondary {
  align-self: flex-start;
  border: 1px solid #93c5fd;
  padding: 0.5rem 1rem;
  border-radius: 0.75rem;
  background: #fff;
  cursor: pointer;
  font-weight: 600;
  color: #1d4ed8;
}

.secondary[disabled] {
  opacity: 0.6;
  cursor: not-allowed;
}

.accessories-card {
  background: #fff;
}

.accessories-header {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.accessory-form {
  display: flex;
  gap: 0.75rem;
}

.accessory-form input {
  flex: 1;
}

.chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  list-style: none;
  padding: 0;
  margin: 0;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background: #e2e8f0;
  border-radius: 999px;
  padding: 0.35rem 0.75rem;
}

.chip button {
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
}
</style>
