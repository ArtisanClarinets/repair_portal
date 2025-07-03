<script setup>
import { onMounted, ref } from "vue";
import DashboardCard from '../../src/components/DashboardCard.vue'; // Import the new component

const dashboardData = ref(null);
const loading = ref(true);
const error = ref(null);

const fetchData = () => {
  // ... (fetchData function remains the same as before)
};

onMounted(() => {
  // ... (onMounted function remains the same as before)
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
            </ul>
        </DashboardCard>
        <DashboardCard title="Open Tasks">
          <ul class="list-group">
            </ul>
        </DashboardCard>
      </div>
    </div>
  </div>
</template>

<style>
/* You can keep or move these styles as needed */
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