// repair_portal/vue/composables/useWellness.ts
// Updated: 2025-08-30
// Version: 1.0
// Purpose: Provide composition logic for the instrument wellness dashboard.
// Dev notes: Extracted from public/js/wellness_dashboard.js for Vue3 modularity.

import { ref, onMounted } from 'vue';

export function useWellness(score: number, history: any[], dueDays: number | null) {
  const gaugeRef = ref<HTMLCanvasElement | null>(null);
  const serviceListRef = ref<HTMLElement | null>(null);

  const drawGauge = () => {
    if (!gaugeRef.value) return;
    const ctx = (gaugeRef.value as HTMLCanvasElement).getContext('2d');
    if (!ctx) return;
    const color = score > 70 ? '#16a34a' : score > 40 ? '#facc15' : '#dc2626';
    // Chart is globally available via frappe assets
    // @ts-ignore
    new Chart(ctx, {
      type: 'doughnut',
      data: {
        datasets: [
          {
            data: [score, 100 - score],
            backgroundColor: [color, '#e5e7eb'],
            borderWidth: 0,
          },
        ],
      },
      options: {
        circumference: 180,
        rotation: 270,
        cutout: '70%',
        plugins: { tooltip: { enabled: false }, legend: { display: false } },
      },
    });
  };

  const renderHistory = () => {
    if (!serviceListRef.value) return;
    history.forEach((item) => {
      const li = document.createElement('li');
      li.className = 'py-2';
      li.innerHTML = `<strong>${item.repair_type}</strong> <span class="ml-2 text-gray-600">${item.modified}</span>`;
      serviceListRef.value!.appendChild(li);
    });
  };

  onMounted(() => {
    drawGauge();
    renderHistory();
    if (history.length && (window as any).confetti) {
      (window as any).confetti({ particleCount: 40, spread: 60 });
    }
    if (dueDays !== null && dueDays <= 30) {
      const badge = document.getElementById('due-badge');
      badge?.classList.remove('hidden');
      badge?.classList.add('animate-pulse');
    }
  });

  return { gaugeRef, serviceListRef };
}
