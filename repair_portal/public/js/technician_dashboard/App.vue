<template>
  <div class="technician-dashboard p-4">
    <div v-if="loading" class="text-center text-muted" role="status" aria-live="polite">Loading dashboard...</div>
    <div v-if="error" class="alert alert-danger" role="alert" aria-live="assertive">{{ error }}</div>

    <div v-if="!loading && !error">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <div class="kpi-card bg-white p-4 rounded-lg shadow">
          <h3 class="text-lg font-semibold text-gray-600">Open Repairs</h3>
          <p class="text-3xl font-bold">{{ kpis.open_repairs || 0 }}</p>
        </div>
        <div class="kpi-card bg-white p-4 rounded-lg shadow">
          <h3 class="text-lg font-semibold text-gray-600">In Progress</h3>
          <p class="text-3xl font-bold">{{ kpis.in_progress_repairs || 0 }}</p>
        </div>
        <div class="kpi-card bg-white p-4 rounded-lg shadow" :class="{ 'text-red-600': kpis.overdue_repairs > 0 }">
          <h3 class="text-lg font-semibold">Overdue</h3>
          <p class="text-3xl font-bold">{{ kpis.overdue_repairs || 0 }}</p>
        </div>
      </div>

      <div class="assigned-repairs-section mb-4">
        <h2 class="text-xl font-bold mb-2">My Active Assignments</h2>
        <div v-if="!assigned_repairs.length" class="text-center text-muted p-4 bg-white rounded-lg">
          No active repairs assigned.
        </div>
        <ul v-else class="list-group">
          <li v-for="repair in assigned_repairs" :key="repair.name" class="list-group-item d-flex justify-content-between align-items-center">
            <div>
              <a :href="`/app/repair-request/${repair.name}`" class="font-bold text-primary">{{ repair.name }}</a>: {{ repair.instrument_category }}
              <p class="text-muted text-sm">{{ repair.issue_description }}</p>
            </div>
            <span :class="getStatusClass(repair.status)" class="badge">{{ repair.status }}</span>
          </li>
        </ul>
      </div>

      <div class="recent-activity-section">
        <h2 class="text-xl font-bold mb-2">Recent Activity</h2>
         <div v-if="!recent_activity.length" class="text-center text-muted p-4 bg-white rounded-lg">
          No recent activity.
        </div>
        <ul v-else class="list-group">
          <li v-for="activity in recent_activity" :key="activity.timestamp" class="list-group-item">
            <p>
              <strong>{{ activity.repair_order }}</strong> status changed to <strong>{{ activity.status }}</strong>
              <span class="text-muted text-sm float-end">{{ formatTimestamp(activity.timestamp) }}</span>
            </p>
            <p v-if="activity.note" class="text-sm pl-3 border-left">- "{{ activity.note }}"</p>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      loading: true,
      error: null,
      kpis: {},
      assigned_repairs: [],
      recent_activity: [],
    };
  },
  mounted() {
    this.fetchData();
    // Listen for realtime updates
    frappe.realtime.on('technician_dashboard_update', (data) => {
        // A simple refetch is often the most reliable way to update
        frappe.show_alert({message: `Dashboard updated: ${data.message}`, indicator: 'green'});
        this.fetchData();
    });
  },
  methods: {
    fetchData() {
      this.loading = true;
      frappe.call({
        method: "repair_portal.api.technician_dashboard.get_dashboard_data",
        args: {
            technician: frappe.session.user
        }
      }).then(r => {
        if (r.message) {
          this.kpis = r.message.kpis;
          this.assigned_repairs = r.message.assigned_repairs;
          this.recent_activity = r.message.recent_activity;
        }
        this.loading = false; // Moved from finally
      }).catch(err => {
        this.error = "Failed to load dashboard data. " + err.message;
        frappe.msgprint(this.error);
        this.loading = false; // Moved from finally
      })
    },
    getStatusClass(status) {
      const classes = {
        'Open': 'bg-danger',
        'In Progress': 'bg-warning',
        'Resolved': 'bg-success',
      };
      return classes[status] || 'bg-secondary';
    },
    formatTimestamp(ts) {
        return frappe.datetime.comment_when(ts);
    }
  }
};
</script>

<style>
.kpi-card {
  transition: transform 0.2s;
}
.kpi-card:hover {
  transform: translateY(-5px);
}
</style>