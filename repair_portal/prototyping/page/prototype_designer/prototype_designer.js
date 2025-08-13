frappe.pages['prototype-designer'].on_page_load = function(wrapper) {
  const page = frappe.ui.make_app_page({
    parent: wrapper,
    title: 'Prototype Designer',
    single_column: true
  });

  // minimal UI: SVG box whose size follows parameters Width/Height
  const q = new URLSearchParams(window.location.search);
  const name = q.get('name');

  page.set_primary_action('Back to Prototype', () => {
    frappe.set_route('Form', 'Prototype', name);
  });

  const $container = $(`
    <div class="pt-3">
      <div class="mb-2">Prototype: <b>${frappe.utils.escape_html(name || '')}</b></div>
      <div class="mb-2">
        <button class="btn btn-sm btn-primary" id="reload_params">Reload Parameters</button>
      </div>
      <div class="border p-2">
        <svg id="proto_svg" width="200" height="120" viewBox="0 0 200 120" style="border:1px solid #ccc">
          <rect id="box" x="10" y="10" width="180" height="100" fill="none" stroke="black"></rect>
        </svg>
      </div>
      <div class="text-muted mt-2">Tip: Add parameters "Width" and "Height" in the Prototype table to drive the rectangle.</div>
    </div>
  `).appendTo(page.body);

  async function load_params() {
    if (!name) return;
    const r = await frappe.db.get_doc('Prototype', name);
    const params = {};
    (r.parameters || []).forEach(p => {
      params[(p.param_name || '').toLowerCase()] = p.param_value;
    });
    const w = parseFloat(params['width'] || '180');
    const h = parseFloat(params['height'] || '100');
    const box = document.getElementById('box');
    if (box) {
      box.setAttribute('width', isFinite(w) ? w : 180);
      box.setAttribute('height', isFinite(h) ? h : 100);
    }
  }

  $('#reload_params').on('click', load_params);
  load_params();
};
frappe.provide('frappe.pages.prototype_designer');
frappe.pages.prototype_designer = frappe.pages['prototype-designer'];
