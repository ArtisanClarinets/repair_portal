<!-- File: client_portal/App.vue -->
<!-- Last Updated: 2025-07-18 -->
<template>
  <LayoutShell :active="view">
    <component :is="activeComponent" />
  </LayoutShell>
</template>

<script setup>
import { computed } from 'vue';
import LayoutShell from './LayoutShell.vue';
import Customer from './customer/Customer.vue';
import NotFound from './NotFound.vue';

const view = new URL(window.location.href).searchParams.get('view') || 'customer';

const views = {
  customer: Customer
};

const activeComponent = computed(() => views[view] || NotFound);
</script>