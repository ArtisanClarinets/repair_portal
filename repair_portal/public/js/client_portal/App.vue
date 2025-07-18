<!-- File: client_portal/App.vue -->
<!-- Last Updated: 2025-07-16 -->
<template>
  <LayoutShell>
    <component :is="activeComponent" />
  </LayoutShell>
</template>

<script setup>
import { ref, computed } from 'vue';
import LayoutShell from './LayoutShell.vue';
import ClientProfile from './client_profile/ClientProfile.vue';

const view = new URLSearchParams(window.location.search).get('view') || 'client_profile';

const views = {
  client_profile: ClientProfile
};

const activeComponent = computed(() => views[view] || ClientProfile);
</script>