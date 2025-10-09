<template>
  <section aria-labelledby="review-heading" class="wizard-section">
    <h2 id="review-heading">Review &amp; Submit</h2>
    <p class="section-hint">Confirm that all details look accurate before submitting the intake.</p>

    <div class="summary-grid">
      <article class="summary-card">
        <h3>Customer</h3>
        <p><strong>{{ customer.customer_name || '—' }}</strong></p>
        <p>{{ customer.email }}</p>
        <p>{{ customer.phone }}</p>
      </article>
      <article class="summary-card">
        <h3>Instrument</h3>
        <p><strong>{{ instrument.manufacturer || '—' }} {{ instrument.model || '' }}</strong></p>
        <p>Serial: {{ instrument.serial_no || '—' }}</p>
        <ul>
          <li v-for="item in instrument.accessories || []" :key="item">Accessory: {{ item }}</li>
        </ul>
      </article>
      <article class="summary-card">
        <h3>Player</h3>
        <p><strong>{{ player.player_name || customer.customer_name || '—' }}</strong></p>
        <p>{{ player.primary_email || customer.email }}</p>
        <p>{{ player.player_level || '—' }}</p>
      </article>
    </div>

    <article class="summary-card">
      <h3>Service</h3>
      <p>Intake Type: {{ service.intakeType }}</p>
      <p v-if="service.issue_description">Issue: {{ service.issue_description }}</p>
      <p v-if="service.condition_notes">Notes: {{ service.condition_notes }}</p>
      <p v-if="service.loanerRequired">Loaner: {{ service.loanerInstrument || 'Pending selection' }}</p>
      <p v-if="service.loanerAgreement?.terms_ack">Loaner agreement acknowledged.</p>
    </article>

    <div class="alert" v-if="!isComplete" role="alert">
      <strong>Incomplete:</strong> Some required fields are missing. Please review earlier steps.
    </div>
  </section>
</template>

<script setup>
import { computed, watch } from "vue";

const props = defineProps({
  modelValue: { type: Object, default: () => ({}) },
  customer: { type: Object, default: () => ({}) },
  instrument: { type: Object, default: () => ({}) },
  player: { type: Object, default: () => ({}) },
  service: { type: Object, default: () => ({}) },
});

const emit = defineEmits(["validity-change"]);

const isComplete = computed(() => {
  const customerOk = Boolean(props.customer.customer_name && props.customer.email && props.customer.phone);
  const instrumentOk = Boolean(props.instrument.manufacturer && props.instrument.model && props.instrument.serial_no);
  const playerOk = Boolean((props.player.sameAsCustomer && customerOk) || (props.player.player_name && props.player.primary_email));
  let serviceOk = true;
  if (props.service.intakeType === "New Inventory") {
    serviceOk = props.service.acquisition_cost >= 0 && props.service.store_asking_price >= 0;
  } else {
    serviceOk = Boolean(props.service.issue_description);
  }
  if (props.service.loanerRequired) {
    serviceOk =
      serviceOk &&
      Boolean(
        props.service.loanerInstrument &&
          props.service.loanerAgreement?.terms_ack &&
          props.service.loanerAgreement?.borrower_signature &&
          props.service.loanerAgreement?.staff_signature
      );
  }
  return customerOk && instrumentOk && playerOk && serviceOk;
});

watch(
  () => isComplete.value,
  (value) => {
    emit("validity-change", value);
  },
  { immediate: true }
);
</script>

<style scoped>
.wizard-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}
.summary-card {
  background: #f9fafb;
  border-radius: 0.75rem;
  padding: 1rem;
  box-shadow: inset 0 1px 0 #fff;
}
.summary-card h3 {
  margin-top: 0;
  font-size: 1rem;
}
.alert {
  background: #fef3c7;
  border-left: 4px solid #f59e0b;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
}
.section-hint {
  margin: 0;
  color: #6b7280;
}
</style>
