<!-- repair_portal/vue/pages/CustomerSignOff.vue -->
<!-- Updated: 2025-09-01 -->
<!-- Version: 0.1 -->
<!-- Purpose: Capture digital signature for customer approval. -->
<template>
  <div class="container my-8">
    <h1 class="text-2xl font-bold mb-4">Customer Sign-Off</h1>
    <p class="mb-4">Please sign below to approve the repair.</p>
    <div class="border p-4">
      <canvas ref="pad" class="w-full h-40 border"></canvas>
      <button class="btn btn-secondary mt-2" @click="clearPad">Clear</button>
    </div>
    <button class="btn btn-primary mt-4" @click="submit">Confirm Sign-Off</button>
  </div>
</template>

<script setup lang="ts">
import axios from 'axios';
import SignaturePad from 'signature_pad';
import { onMounted, ref } from 'vue';

const props = defineProps<{ repair: string }>();

const pad = ref<HTMLCanvasElement | null>(null);
let signaturePad: SignaturePad;

onMounted(() => {
  if (pad.value) {
    signaturePad = new SignaturePad(pad.value);
  }
});

function clearPad() {
  signaturePad.clear();
}

async function submit() {
  const data = signaturePad.toDataURL();
  await axios.post('/api/method/repair_portal.qa.api.submit_customer_sign_off', {
    repair: props.repair,
    signature: data,
  });
  window.location.href = `/repair_request?name=${props.repair}`;
}
</script>
