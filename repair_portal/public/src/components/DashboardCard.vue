<script setup>
defineProps({
  title: String
});
</script>

<template>
  <div class="card">
    <h2 v-if="title" class="card-title">{{ title }}</h2>
    <slot></slot> </div>
</template>

<style>
.card {
  background-color: white;
  border-radius: 0.5rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
}
.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  margin-top: 0;
  margin-bottom: 1rem;
  color: #374151;
}
</style>