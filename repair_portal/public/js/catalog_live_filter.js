// ClarinetFest live filter – v2.1  (2025-07-12)
frappe.ready(() => {
  const input        = document.getElementById('liveFilter');
  if (!input) return;

  // helper – debounce
  const debounce = (fn, ms = 250) => {
    let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); };
  };

  // main filter routine
  const run = () => {
    const q = input.value.trim().toLowerCase();
    let visibleCards = 0;

    // toggle cards
    document.querySelectorAll('.item-card-link').forEach(wrap => {
      const txt = wrap.textContent.toLowerCase();
      const show = txt.includes(q);
      wrap.style.display = show ? '' : 'none';
      if (show) visibleCards++;
    });

    // toggle whole buckets (grid + <h2>)
    document.querySelectorAll('.item-grid').forEach(grid => {
      const cardsVisible = grid.querySelectorAll('.item-card-link:not([style*="display: none"])').length;
      const h2  = grid.previousElementSibling;
      grid.style.display = h2.style.display = cardsVisible ? '' : 'none';
    });

    // empty-state message
    let msg = document.getElementById('noResultsMessage');
    if (!msg) {
      msg = document.createElement('p');
      msg.id = 'noResultsMessage';
      msg.className = 'no-data';
      input.after(msg);
    }
    msg.textContent = visibleCards ? '' : `No results found for “${q}”.`;
    msg.style.display = visibleCards ? 'none' : 'block';
  };

  input.addEventListener('input', debounce(run));
});