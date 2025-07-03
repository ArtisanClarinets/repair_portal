/* Pulse-stream real-time updates (XSS-safe version)  */

frappe.ready(() => {
  const updatesEl = document.querySelector('#pulse-updates');
  if (!updatesEl) return;

  const channel = updatesEl.dataset.channel;

  function addRow(data) {
    const li = document.createElement('li');
    li.className = 'py-2 border-t';

    // <strong>{status}</strong> <span class="ml-2 text-gray-600">{timestamp}</span>
    const statusEl = document.createElement('strong');
    statusEl.textContent = data.status || '';

    const tsEl = document.createElement('span');
    tsEl.className = 'ml-2 text-gray-600';
    tsEl.textContent = data.update_time || '';

    li.append(statusEl, ' ', tsEl);

    // Optional details paragraph
    if (data.details) {
      const p = document.createElement('p');
      p.className = 'text-sm';
      p.textContent = data.details;
      li.appendChild(p);
    }

    // Optional percent-complete indicator
    if (data.percent_complete) {
      const pc = document.createElement('p');
      pc.className = 'text-xs text-green-700';
      pc.textContent = `${data.percent_complete}%`;
      li.appendChild(pc);

      // Celebrate 100 % with confetti if available
      if (Number(data.percent_complete) === 100 && window.confetti) {
        window.confetti();
      }
    }

    updatesEl.appendChild(li);
  }

  // Render server-side bootstrapped updates first
  (window.initialUpdates || []).forEach(addRow);

  // Listen for real-time pushes
  frappe.realtime.on(channel, addRow);
});
