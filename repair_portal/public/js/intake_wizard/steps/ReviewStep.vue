<template>
  <section aria-labelledby="review-heading" class="wizard-section">
    <header class="section-header">
      <div>
        <h2 id="review-heading">Review &amp; Submit</h2>
        <p class="section-hint">Confirm that every pillar of the intake is complete before we route it to inspection.</p>
      </div>
      <span class="status-pill" :class="{ 'status-pill--ready': isComplete, 'status-pill--warning': !isComplete }">
        {{ isComplete ? 'Ready to submit' : 'Needs attention' }}
      </span>
    </header>

    <div class="summary-grid" role="list">
      <article class="summary-card" role="listitem">
        <header>
          <h3>Customer</h3>
          <span :class="badgeClass(customerOk)">{{ customerOk ? 'Complete' : 'Missing' }}</span>
        </header>
        <p><strong>{{ customer.customer_name || '—' }}</strong></p>
        <p>{{ customer.email || '—' }}</p>
        <p>{{ customer.phone || '—' }}</p>
      </article>
      <article class="summary-card" role="listitem">
        <header>
          <h3>Instrument</h3>
          <span :class="badgeClass(instrumentOk)">{{ instrumentOk ? 'Complete' : 'Missing' }}</span>
        </header>
        <p><strong>{{ instrument.manufacturer || '—' }} {{ instrument.model || '' }}</strong></p>
        <p>Serial: {{ instrument.serial_no || '—' }}</p>
        <ul>
          <li v-for="item in instrument.accessories || []" :key="item">Accessory: {{ item }}</li>
          <li v-if="!(instrument.accessories || []).length">No accessories recorded</li>
        </ul>
      </article>
      <article class="summary-card" role="listitem">
        <header>
          <h3>Player</h3>
          <span :class="badgeClass(playerOk)">{{ playerOk ? 'Complete' : 'Missing' }}</span>
        </header>
        <p><strong>{{ player.player_name || customer.customer_name || '—' }}</strong></p>
        <p>{{ player.primary_email || customer.email || '—' }}</p>
        <p>{{ player.player_level || '—' }}</p>
      </article>
    </div>

    <article class="summary-card">
      <header>
        <h3>Service Plan</h3>
        <span :class="badgeClass(serviceOk)">{{ serviceOk ? 'Complete' : 'Missing' }}</span>
      </header>
      <p>Intake Type: {{ service.intakeType }}</p>
      <p v-if="service.issue_description">Issue: {{ service.issue_description }}</p>
      <p v-if="service.condition_notes">Notes: {{ service.condition_notes }}</p>
      <p v-if="service.loanerRequired">Loaner: {{ service.loanerInstrument || 'Pending selection' }}</p>
      <p v-if="service.loanerAgreement?.terms_ack">Loaner agreement acknowledged.</p>
    </article>

    <div class="alert" v-if="!isComplete" role="alert">
      <strong>Incomplete:</strong> Some required fields are missing. Return to the highlighted steps and fill in the details.
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

const customerOk = computed(() => Boolean(props.customer.customer_name && props.customer.email && props.customer.phone));
const instrumentOk = computed(() => Boolean(props.instrument.manufacturer && props.instrument.model && props.instrument.serial_no));
const playerOk = computed(() => Boolean((props.player.sameAsCustomer && customerOk.value) || (props.player.player_name && props.player.primary_email)));
const serviceOk = computed(() => {
  let valid = true;
  if (props.service.intakeType === "New Inventory") {
    valid = props.service.acquisition_cost >= 0 && props.service.store_asking_price >= 0;
  } else {
    valid = Boolean(props.service.issue_description);
  }
  if (props.service.loanerRequired) {
    valid =
      valid &&
      Boolean(
        props.service.loanerInstrument &&
          props.service.loanerAgreement?.terms_ack &&
          props.service.loanerAgreement?.borrower_signature &&
          props.service.loanerAgreement?.staff_signature
      );
  }
  return valid;
});

const isComplete = computed(() => customerOk.value && instrumentOk.value && playerOk.value && serviceOk.value);

function badgeClass(valid) {
  return {
    badge: true,
    "badge--ok": valid,
    "badge--warn": !valid,
  };
}

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

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-hint {
  margin: 0.25rem 0 0;
  color: #64748b;
}

.status-pill {
  border-radius: 999px;
  padding: 0.4rem 0.75rem;
  font-size: 0.8rem;
  font-weight: 600;
  background: #fef3c7;
  color: #92400e;
}

.status-pill--ready {
  background: #dcfce7;
  color: #166534;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}

.summary-card {
  background: #f8fafc;
  border-radius: 0.75rem;
  padding: 1rem;
  box-shadow: inset 0 1px 0 #fff;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.summary-card header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.summary-card h3 {
  margin: 0;
  font-size: 1rem;
}

.badge {
  border-radius: 999px;
  padding: 0.25rem 0.6rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.badge--ok {
  background: #dcfce7;
  color: #166534;
}

.badge--warn {
  background: #fee2e2;
  color: #b91c1c;
}

.alert {
  background: #fef3c7;
  border-left: 4px solid #f59e0b;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
}

.section-hint,
.summary-card p,
.summary-card ul {
  color: #475569;
}

.summary-card ul {
  list-style: none;
  padding: 0;
  margin: 0;
  font-size: 0.9rem;
}
</style>
