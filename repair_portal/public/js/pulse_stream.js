frappe.ready(() => {
  const updatesEl = document.querySelector('#pulse-updates');
  if (!updatesEl) return;
  const channel = updatesEl.dataset.channel;

  function addRow(data) {
    const li = document.createElement('li');
    li.className = 'py-2 border-t';

    const strong = document.createElement('strong');
    strong.textContent = data.status || '';

    const span = document.createElement('span');
    span.className = 'ml-2 text-gray-600';
    span.textContent = data.update_time || '';

    li.appendChild(strong);
    li.appendChild(span);

    if (data.details) {
      const p = document.createElement('p');
      p.className = 'text-sm';
      p.textContent = data.details;
      li.appendChild(p);
    }
    if (data.percent_complete) {
      const pc = document.createElement('p');
      pc.className = 'text-xs text-green-700';
      pc.textContent = `${data.percent_complete}%`;
      li.appendChild(pc);
      if (Number(data.percent_complete) === 100 && window.confetti) {
        window.confetti();
      }
    }
    updatesEl.appendChild(li);
  }

  (window.initialUpdates || []).forEach(addRow);
  frappe.realtime.on(channel, addRow);
});