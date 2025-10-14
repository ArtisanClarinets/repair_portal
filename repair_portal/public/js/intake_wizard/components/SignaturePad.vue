<template>
  <div class="signature-pad" :class="{ 'is-disabled': disabled }">
    <div class="signature-header">
      <span class="signature-label">{{ label }}</span>
      <span class="signature-instruction">Sign directly or upload an image.</span>
    </div>
    <div class="pad-wrapper" :class="{ 'pad-wrapper--empty': isEmpty }">
      <canvas
        ref="canvas"
        class="pad-canvas"
        role="img"
        :aria-label="`${label} capture area`"
        :tabindex="disabled ? -1 : 0"
        @pointerdown="beginStroke"
        @pointermove="drawStroke"
        @pointerup="endStroke"
        @pointerleave="endStroke"
        @pointercancel="endStroke"
      ></canvas>
      <div v-if="isEmpty" class="pad-placeholder" aria-hidden="true">
        <span>Sign here</span>
      </div>
    </div>
    <div class="pad-controls">
      <button type="button" class="secondary" @click="clearPad" :disabled="disabled || isEmpty">Clear</button>
      <label class="upload-label">
        <span>Upload signature</span>
        <input
          ref="fileInput"
          type="file"
          accept="image/*"
          :disabled="disabled"
          @change="handleUpload"
        />
      </label>
      <span class="size-hint">Max {{ readableLimit }}</span>
    </div>
    <p v-if="error" class="signature-error" role="alert">{{ error }}</p>
    <figure v-if="modelValue" class="signature-preview">
      <img :src="modelValue" :alt="`${label} preview`" />
      <figcaption>Preview</figcaption>
    </figure>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";

const props = defineProps({
  modelValue: { type: String, default: "" },
  label: { type: String, default: "Signature" },
  disabled: { type: Boolean, default: false },
  maxBytes: { type: Number, default: 128 * 1024 },
});

const emit = defineEmits(["update:modelValue", "invalid"]);

const canvas = ref(null);
const fileInput = ref(null);
const context = ref(null);
const drawing = ref(false);
const isEmpty = ref(true);
const error = ref("");
const deviceRatio = ref(window.devicePixelRatio || 1);
const blankSnapshot = ref("");
let resizeObserver = null;

const readableLimit = computed(() => {
  if (props.maxBytes >= 1024 * 1024) {
    return `${(props.maxBytes / (1024 * 1024)).toFixed(1)} MB`;
  }
  if (props.maxBytes >= 1024) {
    return `${Math.round(props.maxBytes / 1024)} KB`;
  }
  return `${props.maxBytes} bytes`;
});

function setError(message) {
  error.value = message;
  emit("invalid", message);
}

function clearError() {
  if (error.value) {
    error.value = "";
    emit("invalid", null);
  }
}

function ensureContext() {
  if (!canvas.value) return null;
  if (context.value) return context.value;
  const ctx = canvas.value.getContext("2d");
  if (!ctx) return null;
  context.value = ctx;
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  ctx.lineWidth = 2.2;
  ctx.strokeStyle = "#111827";
  return ctx;
}

function dataUrlBytes(dataUrl) {
  if (!dataUrl) return 0;
  const parts = dataUrl.split(",");
  if (parts.length < 2) {
    return dataUrl.length;
  }
  const base64 = parts[1];
  return Math.floor((base64.length * 3) / 4);
}

function syncValueFromCanvas() {
  if (!canvas.value) return;
  const dataUrl = canvas.value.toDataURL("image/png");
  if (dataUrlBytes(dataUrl) > props.maxBytes) {
    setError(`Signature is too large. Please keep it under ${readableLimit.value}.`);
    return;
  }
  if (blankSnapshot.value && dataUrl === blankSnapshot.value) {
    emit("update:modelValue", "");
    isEmpty.value = true;
    clearError();
    return;
  }
  clearError();
  emit("update:modelValue", dataUrl);
  isEmpty.value = false;
}

function renderDataUrl(value) {
  const ctx = ensureContext();
  if (!ctx || !canvas.value) return;
  const ratio = deviceRatio.value;
  ctx.save();
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.clearRect(0, 0, canvas.value.width, canvas.value.height);
  ctx.restore();
  if (!value) {
    ctx.fillStyle = "#fff";
    ctx.fillRect(0, 0, canvas.value.width, canvas.value.height);
    isEmpty.value = true;
    blankSnapshot.value = canvas.value.toDataURL("image/png");
    return;
  }
  const image = new Image();
  image.onload = () => {
    ctx.save();
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    ctx.drawImage(image, 0, 0, canvas.value.width / ratio, canvas.value.height / ratio);
    ctx.restore();
    isEmpty.value = false;
  };
  image.src = value;
}

function resizeCanvas() {
  const canvasEl = canvas.value;
  if (!canvasEl) return;
  const parent = canvasEl.parentElement;
  if (!parent) return;
  const rect = parent.getBoundingClientRect();
  const ratio = window.devicePixelRatio || 1;
  deviceRatio.value = ratio;
  canvasEl.width = rect.width * ratio;
  canvasEl.height = rect.height * ratio;
  canvasEl.style.width = `${rect.width}px`;
  canvasEl.style.height = `${rect.height}px`;
  const ctx = ensureContext();
  if (!ctx) return;
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  ctx.fillStyle = "#fff";
  ctx.fillRect(0, 0, canvasEl.width, canvasEl.height);
  blankSnapshot.value = canvasEl.toDataURL("image/png");
  if (props.modelValue) {
    renderDataUrl(props.modelValue);
  } else {
    isEmpty.value = true;
  }
}

function pointerPosition(event) {
  const canvasEl = canvas.value;
  if (!canvasEl) return { x: 0, y: 0 };
  const rect = canvasEl.getBoundingClientRect();
  return {
    x: event.clientX - rect.left,
    y: event.clientY - rect.top,
  };
}

function beginStroke(event) {
  if (props.disabled) return;
  const ctx = ensureContext();
  if (!ctx) return;
  drawing.value = true;
  const point = pointerPosition(event);
  ctx.beginPath();
  ctx.moveTo(point.x, point.y);
  event.preventDefault();
}

function drawStroke(event) {
  if (!drawing.value || props.disabled) return;
  const ctx = ensureContext();
  if (!ctx) return;
  const point = pointerPosition(event);
  ctx.lineTo(point.x, point.y);
  ctx.stroke();
  event.preventDefault();
}

function endStroke(event) {
  if (!drawing.value) return;
  drawing.value = false;
  event.preventDefault();
  syncValueFromCanvas();
}

function clearPad() {
  if (!canvas.value) return;
  const ctx = ensureContext();
  if (!ctx) return;
  ctx.save();
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.clearRect(0, 0, canvas.value.width, canvas.value.height);
  ctx.restore();
  ctx.fillStyle = "#fff";
  ctx.fillRect(0, 0, canvas.value.width, canvas.value.height);
  blankSnapshot.value = canvas.value.toDataURL("image/png");
  emit("update:modelValue", "");
  clearError();
  isEmpty.value = true;
  if (fileInput.value) {
    fileInput.value.value = "";
  }
}

function handleUpload(event) {
  const [file] = event.target.files || [];
  if (!file) return;
  if (file.size > props.maxBytes) {
    setError(`Signature file is too large. Please keep it under ${readableLimit.value}.`);
    if (fileInput.value) {
      fileInput.value.value = "";
    }
    return;
  }
  const reader = new FileReader();
  reader.onload = (loadEvent) => {
    const value = loadEvent.target?.result;
    if (typeof value === "string") {
      clearError();
      emit("update:modelValue", value);
      renderDataUrl(value);
      isEmpty.value = false;
    }
  };
  reader.readAsDataURL(file);
}

watch(
  () => props.modelValue,
  (value) => {
    if (!canvas.value) return;
    if (!value) {
      renderDataUrl("");
      return;
    }
    renderDataUrl(value);
  }
);

onMounted(() => {
  resizeCanvas();
  resizeObserver = new ResizeObserver(() => {
    resizeCanvas();
  });
  if (canvas.value?.parentElement) {
    resizeObserver.observe(canvas.value.parentElement);
  }
  window.addEventListener("resize", resizeCanvas);
  if (props.modelValue) {
    renderDataUrl(props.modelValue);
  }
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", resizeCanvas);
  if (resizeObserver && canvas.value?.parentElement) {
    resizeObserver.unobserve(canvas.value.parentElement);
  }
});
</script>

<style scoped>
.signature-pad {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.signature-header {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.signature-label {
  font-weight: 600;
  font-size: 0.95rem;
}

.signature-instruction {
  font-size: 0.8rem;
  color: #64748b;
}

.pad-wrapper {
  position: relative;
  border: 1px dashed #cbd5f5;
  border-radius: 0.75rem;
  background: #fff;
  height: 200px;
  overflow: hidden;
}

.pad-wrapper--empty {
  background: #f8fafc;
}

.pad-canvas {
  width: 100%;
  height: 100%;
  touch-action: none;
  cursor: crosshair;
}

.pad-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  font-size: 0.9rem;
  pointer-events: none;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.pad-controls {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.pad-controls .secondary {
  border: 1px solid #cbd5f5;
  background: #fff;
  color: #1d4ed8;
  padding: 0.5rem 1rem;
  border-radius: 0.65rem;
  cursor: pointer;
}

.pad-controls .secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.upload-label {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: 1px solid #cbd5f5;
  border-radius: 0.65rem;
  background: #f8fafc;
  color: #334155;
  cursor: pointer;
}

.upload-label input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}

.size-hint {
  font-size: 0.75rem;
  color: #94a3b8;
}

.signature-error {
  margin: 0;
  font-size: 0.85rem;
  color: #b91c1c;
}

.signature-preview {
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: flex-start;
}

.signature-preview img {
  max-width: 320px;
  max-height: 120px;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  background: #fff;
  padding: 0.5rem;
}

.signature-preview figcaption {
  font-size: 0.75rem;
  color: #94a3b8;
}

.is-disabled {
  opacity: 0.6;
  pointer-events: none;
}
</style>
