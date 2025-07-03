import { createApp, ref, onMounted } from "vue";

const IntakeDashboard = {
	setup() {
		const counts = ref({});
		const recent = ref([]);
		const loading = ref(true);

		const load = async () => {
			loading.value = true;

			const [c, r] = await Promise.all([
				frappe.call("repair_portal.api.intake_dashboard.get_intake_counts"),
				frappe.call("repair_portal.api.intake_dashboard.get_recent_intakes"),
			]);

			counts.value = c.message || {};
			recent.value = r.message || [];
			loading.value = false;
		};

		onMounted(load);

		return { counts, recent, loading, load };
	},
	template: `
  <div class="p-6">
    <h2 class="text-xl font-bold mb-4">Intake Dashboard</h2>
    <div v-if="loading">Loading…</div>
    <div v-else>
      <div class="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
        <div v-for="(v, k) in counts" :key="k" class="border p-4 rounded">
          <div class="text-gray-500">{{ k }}</div>
          <div class="text-2xl">{{ v }}</div>
        </div>
      </div>
      <h3 class="text-lg font-semibold mb-2">Recent Intakes</h3>
      <table class="w-full table-auto">
        <thead><tr>
          <th class="text-left">Intake</th>
          <th>Client</th>
          <th>Player</th>
          <th>Status</th>
          <th>Modified</th>
        </tr></thead>
        <tbody>
          <tr v-for="i in recent" :key="i.name">
            <td>{{ i.name }}</td>
            <td>{{ i.client }}</td>
            <td>{{ i.player }}</td>
            <td>{{ i.workflow_state }}</td>
            <td>{{ i.modified }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
  `
};

frappe.pages["intake-dashboard"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: "Intake Dashboard",
		single_column: true
	});

	const mount = document.createElement("div");
	page.body.appendChild(mount);
	createApp(IntakeDashboard).mount(mount);
};

frappe.provide("frappe.ui");
frappe.ui.IntakeDashboard = IntakeDashboard;
export default IntakeDashboard;