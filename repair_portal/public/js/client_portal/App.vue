<script setup>
import { onMounted, ref } from 'vue';

const loading = ref(true);
const error = ref(null);
const instruments = ref([]);
const repairs = ref([]);

onMounted(async () => {
  try {
    const instrumentRes = await frappe.call('repair_portal.api.client_portal.get_my_instruments');
    instruments.value = instrumentRes.message || [];

    const repairRes = await frappe.call('repair_portal.api.client_portal.get_my_repairs');
    repairs.value = repairRes.message || [];
  } catch (e) {
    console.error(e);
    error.value = 'Could not load portal data.';
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div class="p-4 space-y-4">
    <div v-if="loading" class="text-muted">Loading your instruments and repairs…</div>
    <div v-else-if="error" class="text-danger">{{ error }}</div>
    <div v-else>
      <div>
        <h4 class="text-lg font-bold mb-2">🎺 My Instruments</h4>
        <ul v-if="instruments.length" class="list-disc list-inside">
          <li v-for="inst in instruments" :key="inst.name">
            {{ inst.instrument_type }} — SN: {{ inst.serial_number }}
          </li>
        </ul>
        <p v-else class="text-muted">No instruments found.</p>
      </div>

      <div>
        <h4 class="text-lg font-bold mt-6 mb-2">🔧 My Repairs</h4>
        <ul v-if="repairs.length" class="list-disc list-inside">
          <li v-for="rep in repairs" :key="rep.name">
            {{ rep.status }} — {{ rep.instrument_name }} ({{ rep.modified }})
          </li>
        </ul>
        <p v-else class="text-muted">No repairs in progress.</p>
      </div>
    </div>
  </div>
</template>