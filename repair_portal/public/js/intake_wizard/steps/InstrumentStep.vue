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
          <label :class="{ 'has-error': errors.instrument_category }">
            <span>Instrument Category</span>
            <select v-model="local.instrument_category" @change="onChange" :disabled="categoryLoading">
              <option value="">Select category</option>
              <option v-for="category in categoryOptions" :key="category.name" :value="category.name">
                {{ category.title }}
              </option>
              <option v-if="local.instrument_category && !categoryExists" :value="local.instrument_category">
                {{ local.instrument_category }}
              </option>
            </select>
            <small class="field-hint">Aligns with Instrument Category records for reporting.</small>
            <p v-if="errors.instrument_category" class="field-error">{{ errors.instrument_category }}</p>
          </label>
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
          <label :class="{ 'has-error': errors.clarinet_type }">
            <span>Clarinet Type</span>
            <select v-model="local.clarinet_type" @change="onChange">
              <option value="">Select type</option>
              <option>B♭ Clarinet</option>
              <option>A Clarinet</option>
              <option>E♭ Clarinet</option>
              <option>Bass Clarinet</option>
              <option>Alto Clarinet</option>
              <option>Contrabass Clarinet</option>
              <option>Other</option>
            </select>
            <p v-if="errors.clarinet_type" class="field-error">{{ errors.clarinet_type }}</p>
          </label>
          <label>
            <span>Instrument Type</span>
            <select v-model="local.instrument_type" @change="onChange">
              <option value="">Select type</option>
              <option>B♭ Clarinet</option>
              <option>A Clarinet</option>
              <option>E♭ Clarinet</option>
              <option>Bass Clarinet</option>
              <option>Alto Clarinet</option>
              <option>Contrabass Clarinet</option>
              <option>Other</option>
            </select>
            <small class="field-hint">Feeds Instrument master data for automation.</small>
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
        <p class="mapping-guidance" v-if="serialState.brandMapping">
          Manufacturer updated using catalog rules. Review the mapped brand before submission.
        </p>
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
        <div class="accessory-fields">
          <div class="accessory-field">
            <label>
              <span>Item Code</span>
              <input
                v-model.trim="accessoryForm.item_code"
                type="text"
                placeholder="Search item code"
                @input="onAccessoryCodeInput"
              />
            </label>
            <ul v-if="itemResults.length" class="lookup-list" role="listbox">
              <li v-for="item in itemResults" :key="item.name">
                <button type="button" @click="selectAccessoryItem(item)">
                  <span class="lookup-primary">{{ item.name }}</span>
                  <span class="lookup-secondary">{{ item.item_name || item.description || '—' }}</span>
                </button>
              </li>
            </ul>
          </div>
          <div class="accessory-field">
            <label>
              <span>Description</span>
              <input v-model.trim="accessoryForm.description" type="text" placeholder="Case, mouthpiece, etc." />
            </label>
          </div>
          <div class="accessory-field accessory-field--compact">
            <label>
              <span>Qty</span>
              <input v-model.number="accessoryForm.qty" type="number" min="1" step="1" />
            </label>
          </div>
          <div class="accessory-field accessory-field--compact">
            <label>
              <span>UOM</span>
              <input v-model.trim="accessoryForm.uom" type="text" placeholder="Each" />
            </label>
          </div>
          <button type="submit" class="secondary">Add</button>
        </div>
        <p v-if="accessoryError" class="field-error">{{ accessoryError }}</p>
      </form>
      <table v-if="local.accessories.length" class="accessory-table">
        <thead>
          <tr>
            <th scope="col">Item Code</th>
            <th scope="col">Description</th>
            <th scope="col">Qty</th>
            <th scope="col">UOM</th>
            <th scope="col" class="actions">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in local.accessories" :key="`${item.item_code}-${index}`">
            <td>{{ item.item_code }}</td>
            <td>{{ item.description || '—' }}</td>
            <td>{{ item.qty }}</td>
            <td>{{ item.uom || '—' }}</td>
            <td class="actions">
              <button type="button" class="link-button" @click="removeAccessory(index)">Remove</button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else class="lookup-empty">No accessories recorded yet.</p>
    </article>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from "vue";

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
  instrument_category: "",
  instrument_type: "",
  body_material: "",
  key_plating: "",
  accessories: [],
  item_code: "",
  item_name: "",
  brand_mapping: null,
});

const errors = reactive({ manufacturer: null, model: null, serial_no: null, instrument_category: null, clarinet_type: null });
const categoryOptions = ref([]);
const categoryExists = computed(() =>
  categoryOptions.value.some((category) => category.name === local.instrument_category)
);
const categoryLoading = ref(false);
const accessoryForm = reactive({ item_code: "", description: "", qty: 1, uom: "" });
const accessoryError = ref("");
const itemResults = ref([]);
let accessorySearchTimer = null;
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

function normalizeAccessoryList(list = []) {
  if (!Array.isArray(list)) {
    return [];
  }
  return list
    .map((item) => {
      if (!item) return null;
      if (typeof item === "string") {
        return { item_code: "", description: item, qty: 1, uom: "" };
      }
      return {
        item_code: item.item_code || "",
        description: item.description || item.label || "",
        qty: Number.isFinite(item.qty) ? Number(item.qty) : 1,
        uom: item.uom || "",
      };
    })
    .filter(Boolean);
}

watch(
  () => props.modelValue,
  (value) => {
    const incoming = { accessories: [], brand_mapping: null, ...value };
    Object.assign(local, incoming);
    local.accessories = normalizeAccessoryList(incoming.accessories);
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
  if (!local.instrument_category) {
    errors.instrument_category = "Instrument category is required.";
  }
  if (!local.manufacturer) {
    errors.manufacturer = "Manufacturer is required.";
  }
  if (!local.model) {
    errors.model = "Model is required.";
  }
  if (!local.serial_no) {
    errors.serial_no = "Serial number is required.";
  }
  if (!local.clarinet_type) {
    errors.clarinet_type = "Clarinet type is required.";
  }
  const valid =
    !errors.instrument_category && !errors.manufacturer && !errors.model && !errors.serial_no && !errors.clarinet_type;
  if (show) {
    emit("validity-change", valid);
  } else {
    emit("validity-change", valid);
  }
  return valid;
}

async function loadCategories() {
  categoryLoading.value = true;
  try {
    const response = await frappe.call({
      method: "frappe.client.get_list",
      args: {
        doctype: "Instrument Category",
        fields: ["name", "title"],
        filters: { is_active: 1 },
        limit_page_length: 50,
        order_by: "title asc",
      },
    });
    categoryOptions.value = (response.message || []).map((row) => ({
      name: row.name,
      title: row.title || row.name,
    }));
  } catch (error) {
    console.warn("Failed to load instrument categories", error);
  } finally {
    categoryLoading.value = false;
  }
}

async function fetchAccessoryItems(query) {
  try {
    const response = await frappe.call({
      method: "frappe.client.get_list",
      args: {
        doctype: "Item",
        txt: query,
        fields: ["name", "item_name", "description", "stock_uom"],
        limit_page_length: 8,
      },
    });
    return response.message || [];
  } catch (error) {
    console.warn("Failed to search items", error);
    return [];
  }
}

function onAccessoryCodeInput() {
  accessoryError.value = "";
  if (accessorySearchTimer) {
    clearTimeout(accessorySearchTimer);
  }
  if (!accessoryForm.item_code || accessoryForm.item_code.length < 2) {
    itemResults.value = [];
    return;
  }
  accessorySearchTimer = setTimeout(async () => {
    itemResults.value = await fetchAccessoryItems(accessoryForm.item_code);
  }, 250);
}

function selectAccessoryItem(item) {
  accessoryForm.item_code = item.name;
  accessoryForm.description = item.item_name || item.description || accessoryForm.description;
  accessoryForm.uom = item.stock_uom || accessoryForm.uom;
  itemResults.value = [];
}

function resetAccessoryForm() {
  accessoryForm.item_code = "";
  accessoryForm.description = "";
  accessoryForm.qty = 1;
  accessoryForm.uom = "";
  itemResults.value = [];
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
  accessoryError.value = "";
  if (!accessoryForm.item_code) {
    accessoryError.value = "Item code is required.";
    return;
  }
  const entry = {
    item_code: accessoryForm.item_code,
    description: accessoryForm.description,
    qty: accessoryForm.qty > 0 ? accessoryForm.qty : 1,
    uom: accessoryForm.uom,
  };
  local.accessories = [...local.accessories, entry];
  resetAccessoryForm();
  emitUpdate();
}

function removeAccessory(index) {
  local.accessories = local.accessories.filter((_, i) => i !== index);
  emitUpdate();
}

watch(
  () => local.clarinet_type,
  (value) => {
    if (!local.instrument_type && value) {
      local.instrument_type = value;
    }
  }
);

onMounted(() => {
  loadCategories();
});

onBeforeUnmount(() => {
  if (accessorySearchTimer) {
    clearTimeout(accessorySearchTimer);
  }
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

.status-cluster {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.section-header h2 { margin: 0; font-size: 1.5rem; color: var(--text); }

.section-hint {
  margin: 0.25rem 0 0;
  color: var(--muted);
  max-width: 620px;
}

.card {
  background-color: var(--card-bg);
  border-radius: 0.75rem;
  border: 1px solid var(--border);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.card h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text);
}

.content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr; /* Prioritize the main form */
  gap: 1.5rem;
}

.field-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.25rem;
}

/* --- Form Element Styles --- */
label {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  font-weight: 500;
  font-size: 0.875rem;
  color: var(--text);
}

input,
select {
  padding: 0.65rem 0.875rem;
  border-radius: 0.5rem;
  border: 1px solid var(--border);
  background-color: var(--card-bg);
  font-size: 1rem;
  color: var(--text);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

input:focus-visible,
select:focus-visible {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--focus);
}

.field-hint { font-weight: 400; font-size: 0.875rem; color: var(--muted); }
.field-error { margin: 0; font-size: 0.875rem; color: var(--danger); }
.has-error input, .has-error select { border-color: color-mix(in srgb, var(--danger) 30%, var(--border)); }

/* --- Status Pill Styles --- */
.status-pill {
  border-radius: 999px;
  padding: 0.375rem 0.875rem;
  font-size: 0.875rem;
  font-weight: 500;
}
.status-pill--success { background-color: var(--success-surface); color: var(--success); }
.status-pill--info { background-color: color-mix(in srgb, var(--primary) 12%, var(--surface)); color: var(--primary); }
.status-pill--neutral { background-color: color-mix(in srgb, var(--primary) 8%, var(--surface)); color: var(--primary-600); }
.status-pill--muted { background-color: var(--surface); color: var(--muted); }

/* --- Insight Card --- */
.insight-card {
  background-color: var(--bg); /* Subtle background */
  position: sticky;
  top: 2rem;
}

.insight-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.insight-label {
  display: block;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--muted);
}

.insight-value {
  font-weight: 600;
  color: var(--text);
  font-size: 1.125rem;
}

.mapping-guidance {
  margin: 0;
  font-size: 0.875rem;
  color: var(--primary);
  display: inline-flex;
  font-size: 1rem;
  align-items: center;
  gap: 0.35rem;
  background-color: color-mix(in srgb, var(--surface) 85%, var(--primary));
  color: var(--primary-600);
  padding: 0.25rem 0.65rem;
  border-radius: 999px;
}

/* --- Accessories Section --- */
.accessory-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border);
}

.accessory-fields {
  display: grid;
  grid-template-columns: 2fr 2fr 1fr 1fr auto;
  gap: 1rem;
  align-items: flex-end;
}

.accessory-field { position: relative; }

.lookup-list {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background-color: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 0.5rem;
  box-shadow: var(--shadow);
  list-style: none;
  margin-top: 0.25rem;
  padding: 0.25rem 0;
  max-height: 200px;
  overflow-y: auto;
  z-index: 10;
}

.lookup-list li + li { border-top: 1px solid var(--border); }

.lookup-list button {
  width: 100%;
  background-color: transparent;
  border: none;
  text-align: left;
  padding: 0.5rem 0.75rem;
  cursor: pointer;
}
.lookup-list button:hover { background-color: var(--bg); }
.lookup-primary { font-weight: 500; color: var(--text); }
.lookup-secondary { font-size: 0.8rem; color: var(--muted); }

.accessory-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

.accessory-table th, .accessory-table td {
  padding: 0.75rem;
  border-bottom: 1px solid var(--border);
  text-align: left;
}

.accessory-table th {
  background-color: var(--bg);
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--muted);
}

.accessory-table td.actions, .accessory-table th.actions { text-align: right; }

.link-button {
  border: none;
  background: none;
  color: var(--primary);
  cursor: pointer;
  font-weight: 600;
}
.link-button:hover { text-decoration: underline; }

.lookup-empty {
  margin: 1rem 0 0;
  font-size: 0.875rem;
  color: var(--muted);
  text-align: center;
  padding: 1rem;
  background-color: var(--bg);
  border-radius: 0.5rem;
}

/* --- Shared Button Styles --- */
.secondary {
  border: 1px solid var(--border);
  padding: 0.65rem 1rem;
  border-radius: 0.5rem;
  background-color: var(--card-bg);
  cursor: pointer;
  font-weight: 600;
  color: var(--text);
  box-shadow: var(--shadow);
}
.secondary:disabled { opacity: 0.6; cursor: not-allowed; }
</style>
