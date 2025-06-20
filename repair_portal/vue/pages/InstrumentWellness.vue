<!-- repair_portal/vue/pages/InstrumentWellness.vue -->
<!-- Updated: 2025-08-30 -->
<!-- Version: 1.0 -->
<!-- Purpose: SSR friendly wellness dashboard for a single instrument. -->
<!-- Dev notes: Migrated from templates/pages/instrument_wellness.html -->
<template>
  <div class="container my-8">
    <h1 class="text-3xl font-semibold mb-6">{{ instrument.instrument_name }}</h1>
    <div id="wellness-app" :data-score="wellness_score" :data-history="historyJson" :data-due-days="due_days">
      <canvas ref="gaugeRef" id="gauge" width="300" height="150"></canvas>
      <div class="mt-4">
        <button id="schedule-btn" class="btn btn-primary" @click="goToRequest">
          {{ __('Schedule Next Service') }}
        </button>
        <span id="due-badge" class="badge bg-warning ml-2 hidden">{{ __('Service Due Soon') }}</span>
      </div>
      <ul ref="serviceListRef" id="service-history" class="mt-6 divide-y"></ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useWellness } from '../composables/useWellness';
import { onMounted } from 'vue';

const props = defineProps<{ instrument: any; wellness_score: number; historyJson: string; due_days: number | null }>();

const history = JSON.parse(props.historyJson || '[]');
const { gaugeRef, serviceListRef } = useWellness(props.wellness_score, history, props.due_days);

function goToRequest() {
  window.location.href = `/repair_request?instrument=${props.instrument.name}`;
}
</script>
