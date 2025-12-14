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
        <p>Category: {{ instrument.instrument_category || '—' }}</p>
        <p>Type: {{ instrument.clarinet_type || '—' }}</p>
        <ul class="accessory-list">
          <li v-for="(item, index) in normalizedAccessories" :key="`${item.item_code}-${index}`">
            <span class="accessory-label">Accessory</span>
            <span class="accessory-value">
              {{ item.item_code }}
              <template v-if="item.description">— {{ item.description }}</template>
              <template v-if="item.qty">×{{ item.qty }}</template>
            </span>
          </li>
          <li v-if="!normalizedAccessories.length">No accessories recorded</li>
        </ul>
      </article>
      <article class="summary-card" role="listitem">
        <header>
          <h3>Player</h3>
          <span :class="badgeClass(playerOk)">{{ playerOk ? 'Complete' : 'Missing' }}</span>
        </header>
        <p><strong>{{ player.player_name || customer.customer_name || '—' }}</strong></p>
        <p>{{ player.primary_email || customer.email || '—' }}</p>
        <p>{{ player.primary_phone || customer.phone || '—' }}</p>
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
const normalizedAccessories = computed(() => {
  if (!Array.isArray(props.instrument.accessories)) {
    return [];
  }
  return props.instrument.accessories
    .map((item) =>
      item && typeof item === "object"
        ? {
            item_code: item.item_code || "",
            description: item.description || "",
            qty: item.qty || "",
          }
        : {
            item_code: typeof item === "string" ? item : "",
            description: "",
            qty: "",
          }
    )
    .filter((entry) => entry.item_code || entry.description);
});
const playerOk = computed(
  () =>
    Boolean(
      (props.player.sameAsCustomer && customerOk.value) ||
        (props.player.player_name && props.player.primary_email && props.player.primary_phone)
    )
);
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
/* --- Core Section & Card Styles --- */
.wizard-section { display: flex; flex-direction: column; gap: 2rem; }
.section-header { display: flex; justify-content: space-between; align-items: center; }
.section-header h2 { margin: 0; font-size: 1.5rem; color: var(--text); }
.section-hint { margin: 0.25rem 0 0; color: var(--muted); }

/* --- Status & Badge Styles --- */
.status-pill { border-radius: 999px; padding: 0.375rem 0.875rem; font-size: 0.875rem; font-weight: 500; }
.status-pill--ready { background-color: var(--success-surface); color: var(--success); }
.status-pill--warning { background-color: var(--warning-surface); color: var(--warning); }
.badge { border-radius: 999px; padding: 0.25rem 0.65rem; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; }
.badge--ok { background-color: var(--success-surface); color: var(--success); }
.badge--warn { background-color: var(--danger-surface); color: var(--danger); }

/* --- Summary Layout --- */
.summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; }
.summary-card { background-color: var(--bg); border: 1px solid var(--border); border-radius: 0.75rem; padding: 1.5rem; display: flex; flex-direction: column; gap: 0.75rem; }
.summary-card header { display: flex; justify-content: space-between; align-items: baseline; padding-bottom: 0.75rem; border-bottom: 1px solid var(--border); }
.summary-card h3 { margin: 0; font-size: 1.125rem; font-weight: 600; color: var(--text); }
.summary-card p { margin: 0; color: color-mix(in srgb, var(--text) 70%, var(--muted)); line-height: 1.6; }
.summary-card p strong { color: var(--text); font-weight: 600; }

/* --- Accessory List in Review --- */
.accessory-list { list-style: none; margin: 0.5rem 0 0; padding-top: 0.75rem; border-top: 1px dashed var(--border); display: flex; flex-direction: column; gap: 0.5rem; }
.accessory-label { font-size: 0.8rem; text-transform: uppercase; color: var(--muted); font-weight: 500; }
.accessory-value { display: block; font-weight: 500; color: var(--text); }

/* --- Alert Box --- */
.alert { background-color: var(--warning-surface); border-left: 4px solid var(--warning); padding: 1rem 1.25rem; border-radius: 0.5rem; color: color-mix(in srgb, var(--warning) 60%, var(--muted)); }
</style>
