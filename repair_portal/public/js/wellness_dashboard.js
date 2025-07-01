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
        if (badge) {
          badge.classList.remove('hidden');
          badge.classList.add('animate-pulse');
        }
      }
    },
    methods: {
      drawGauge() {
        const canvas = document.getElementById('score-gauge');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;
        ctx.clearRect(0, 0, width, height);

        // Background arc
        ctx.beginPath();
        ctx.arc(width / 2, height / 2, width / 2 - 10, Math.PI, 0);
        ctx.strokeStyle = '#eee';
        ctx.lineWidth = 12;
        ctx.stroke();

        // Score arc
        const endAngle = Math.PI + (Math.PI * (this.score / 100));
        ctx.beginPath();
        ctx.arc(width / 2, height / 2, width / 2 - 10, Math.PI, endAngle);
        ctx.strokeStyle = this.score > 80 ? '#16a34a' : this.score > 50 ? '#facc15' : '#dc2626';
        ctx.lineWidth = 12;
        ctx.stroke();

        // Score label
        ctx.font = '24px sans-serif';
        ctx.fillStyle = '#333';
        ctx.textAlign = 'center';
        ctx.fillText(`${this.score}%`, width / 2, height / 2 + 10);
      },
      renderHistory() {
        const list = document.getElementById('service-history');
        if (!list) return;

        this.history.forEach((item) => {
          const li = document.createElement('li');
          li.className = 'py-2 flex items-center justify-between';

          const left = document.createElement('strong');
          left.textContent = item.repair_type || 'Unknown';

          const right = document.createElement('span');
          right.className = 'text-gray-600';
          right.textContent = item.modified || '';

          li.append(left, right);
          list.appendChild(li);
        });
      },
    },
  }).mount('#wellness-app');
});
