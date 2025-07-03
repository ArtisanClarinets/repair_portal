<script setup>
import { onMounted, ref } from "vue";
import DashboardCard from '../../src/components/DashboardCard.vue'; // Import the reusable card component

const dashboardData = ref(null);
const loading = ref(true);
const error = ref(null);

const fetchData = () => {
  loading.value = true;
  frappe.call({
    method: "repair_portal.api.technician_dashboard.get_technician_dashboard_counts",
    callback: (r) => {
      if (r.message) {
        dashboardData.value = r.message;
        error.value = null;
      } else {
        error.value = "Failed to fetch dashboard data.";
      }
      loading.value = false;
    },
    error: (err) => {
      error.value = err.message || "An unknown error occurred.";
      loading.value = false;
    }
  });
};

onMounted(() => {
  fetchData();

  // Set up the listener for the refresh button from the bundle file
  const appElement = document.getElementById("__technician_app__");
  if (appElement) {
    appElement.addEventListener("reloadDashboard", fetchData);
  }
});
</script>

<template>
  <div class="p-4" style="background-color: #f3f4f6; min-height: 100vh;">
    <h1 style="font-size: 1.875rem; font-weight: bold; color: #1f2937; margin-bottom: 1.5rem;">
      Technician Dashboard
    </h1>

    <div v-if="loading" style="text-align: center; color: #6b7280;">Loading...</div>
    <div v-if="error" style="text-align: center; color: #ef4444;">{{ error }}</div>

    <div v-if="dashboardData">
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin-bottom: 1.5rem;">
        <DashboardCard title="Completed Repairs (Month)">
          <div class="kpi-value" style="color: #10b981;">{{ dashboardData.kpis.completed_repairs_this_month }}</div>
        </DashboardCard>
        <DashboardCard title="Avg. Completion Time (Days)">
          <div class="kpi-value" style="color: #3b82f6;">{{ dashboardData.kpis.avg_completion_time_days }}</div>
        </DashboardCard>
        <DashboardCard title="Pending QA Inspections">
          <div class="kpi-value" style="color: #f59e0b;">{{ dashboardData.kpis.pending_qa_inspections }}</div>
        </DashboardCard>
      </div>

      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 1.5rem;">
        <DashboardCard title="Assigned Repairs">
          <ul class="list-group">
            <li v-for="repair in dashboardData.assigned_repairs" :key="repair.name" class="list-item">
              <div style="display: flex; justify-content: space-between;">
                <span style="font-weight: 600;">{{ repair.instrument }}</span>
                <span style="font-size: 0.875rem; color: #4b5563;">Due: {{ repair.estimated_completion }}</span>
              </div>
              <div style="font-size: 0.875rem; color: #6b7280;">{{ repair.status }}</div>
            </li>
            <li v-if="!dashboardData.assigned_repairs.length" class="list-item">
              No assigned repairs.
            </li>
          </ul>
        </DashboardCard>

        <DashboardCard title="Open Tasks">
          <ul class="list-group">
            <li v-for="task in dashboardData.open_tasks" :key="task.name" class="list-item">
              <div style="font-weight: 600;">{{ task.task_type }}</div>
              <div style="font-size: 0.875rem; color: #6b7280;">{{ task.description }}</div>
            </li>
             <li v-if="!dashboardData.open_tasks.length" class="list-item">
              No open tasks.
            </li>
          </ul>
        </DashboardCard>
      </div>
    </div>
  </div>
</template>

<style>
/* Scoped styles can be added here, or you can use a global stylesheet */
.kpi-value {
  font-size: 2.25rem;
  font-weight: 700;
  text-align: center;
}
.list-group {
  list-style: none;
  padding: 0;
  margin: 0;
}
.list-item {
  padding: 1rem 0;
  border-bottom: 1px solid #e5e7eb;
}
.list-item:last-child {
  border-bottom: none;
}
</style>