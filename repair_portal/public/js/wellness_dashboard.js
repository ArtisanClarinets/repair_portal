frappe.ready(() => {
  const root = document.getElementById('wellness-app');
  if (!root) return;
  const { createApp } = Vue;

  createApp({
    data() {
      return {
        score: Number(root.dataset.score || 0),
        history: JSON.parse(root.dataset.history || '[]'),
        dueDays: root.dataset.dueDays ? Number(root.dataset.dueDays) : null,
      };
    },
    mounted() {
      this.drawGauge();
      this.renderHistory();
      if (this.history.length && window.confetti) {
        window.confetti({ particleCount: 40, spread: 60 });
      }
      if (this.dueDays !== null && this.dueDays <= 30) {
        const badge = document.getElementById('due-badge');
        badge?.classList.remove('hidden');
        badge?.classList.add('animate-pulse');
      }
    },
    methods: {
      drawGauge() {
        const ctx = document.getElementById('gauge').getContext('2d');
        const color = this.score > 70 ? '#16a34a' : this.score > 40 ? '#facc15' : '#dc2626';
        new Chart(ctx, {
          type: 'doughnut',
          data: {
            datasets: [
              {
                data: [this.score, 100 - this.score],
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
      },
      renderHistory() {
        const list = document.getElementById('service-history');
        this.history.forEach((item) => {
          const li = document.createElement('li');
          li.className = 'py-2';
          li.innerHTML = `<strong>${item.repair_type}</strong> <span class="ml-2 text-gray-600">${item.modified}</span>`;
          list.appendChild(li);
        });
      },
    },
  }).mount('#wellness-app');
});
