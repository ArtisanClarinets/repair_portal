// File: repair_portal/repair_portal/instrument_setup/doctype/setup_template/setup_template.js
// Purpose: Smooth authoring of Template Tasks
// - Auto-sequence new rows
// - Preview schedule based on a hypothetical Setup Date
// - Normalize Sequence tool

frappe.ui.form.on('Setup Template', {
  refresh(frm) {
    if (!frm.is_new()) {
      add_tools(frm);
    }
  }
});

frappe.ui.form.on('Clarinet Template Task', {
  // Auto-sequence new template tasks
  template_tasks_add(frm, cdt, cdn) {
    const row = frappe.get_doc(cdt, cdn);
    const all = frm.doc.template_tasks || [];
    const maxSeq = all.reduce((m, r) => Math.max(m, cint(r.sequence || 0)), 0);
    row.sequence = maxSeq ? maxSeq + 10 : 10; // gaps for reordering
    frm.refresh_field('template_tasks');
  }
});

// ---------- helpers ----------

function add_tools(frm) {
  if (frm.__template_buttons_added) return;

  frm.add_custom_button(__('Preview Task Schedule'), () => preview_schedule_dialog(frm));
  frm.add_custom_button(__('Normalize Sequence'), () => normalize_sequence(frm));

  frm.__template_buttons_added = true;
}

function normalize_sequence(frm) {
  const rows = frm.doc.template_tasks || [];
  rows.sort((a, b) => cint(a.sequence || 0) - cint(b.sequence || 0));
  let seq = 10;
  rows.forEach(r => { r.sequence = seq; seq += 10; });
  frm.refresh_field('template_tasks');
  frappe.show_alert({ message: __('Sequence normalized.'), indicator: 'green' });
}

function preview_schedule_dialog(frm) {
  const d = new frappe.ui.Dialog({
    title: __('Preview Task Schedule'),
    fields: [
      { fieldname: 'setup_date', fieldtype: 'Date', label: __('Setup Date'), reqd: 1, default: frm.doc.setup_date || frappe.datetime.get_today() },
      { fieldname: 'html_preview', fieldtype: 'HTML' }
    ],
    size: 'extra-large'
  });

  d.set_primary_action(__('Preview'), () => {
    const setup_date = d.get_value('setup_date');
    const rows = (frm.doc.template_tasks || []).slice().sort((a, b) => cint(a.sequence || 0) - cint(b.sequence || 0));
    const html = render_preview(rows, setup_date);
    d.fields_dict.html_preview.$wrapper.html(html);
  });

  d.show();
  // Auto-run once
  d.get_primary_btn().click();
}

function render_preview(rows, setup_date) {
  const lines = rows.map(r => {
    const start = frappe.datetime.add_days(setup_date, cint(r.exp_start_offset_days || 0));
    const end = frappe.datetime.add_days(start, Math.max(0, cint(r.exp_duration_days || 1) - 1));
    return `
      <tr>
        <td style="padding:4px;">${cint(r.sequence || 0)}</td>
        <td style="padding:4px;">${frappe.utils.escape_html(r.subject || '')}</td>
        <td style="padding:4px;">${frappe.utils.escape_html(r.default_priority || 'Medium')}</td>
        <td style="padding:4px;">${frappe.datetime.str_to_user(start)}</td>
        <td style="padding:4px;">${frappe.datetime.str_to_user(end)}</td>
        <td style="padding:4px;">${cint(r.exp_duration_days || 1)} ${__('day(s)')}</td>
      </tr>`;
  });

  return `
    <div class="mt-3">
      <table class="table table-bordered">
        <thead>
          <tr>
            <th>${__('Seq')}</th>
            <th>${__('Subject')}</th>
            <th>${__('Priority')}</th>
            <th>${__('Expected Start')}</th>
            <th>${__('Expected End')}</th>
            <th>${__('Duration')}</th>
          </tr>
        </thead>
        <tbody>${lines.join('')}</tbody>
      </table>
    </div>`;
}
