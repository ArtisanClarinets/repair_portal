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
        /* (unchanged) */
      },
      renderHistory() {
        const list = document.getElementById('service-history');
        this.history.forEach((item) => {
          const li = document.createElement('li');
          li.className = 'py-2';

         li.innerHTML = `<strong>${item.repair_type}</strong> <span class="ml-2 text-gray-600">${item.modified}</span>`;
        const typeEl = document.createElement('strong');
         typeEl.textContent = item.repair_type || '';

         const modEl = document.createElement('span');
         modEl.className = 'ml-2 text-gray-600';
         modEl.textContent = item.modified || '';

         li.append(typeEl, ' ', modEl);

          list.appendChild(li);
        });
      },
    },
  }).mount('#wellness-app');
});
