// File: repair_portal/repair_portal/instrument_setup/doctype/setup_template/setup_template.js
// Last Updated: 2025-09-16
// Version: v1.6 (minutes-based; idempotent client update)
// Purpose: Smooth authoring + deterministic totals (minutes → hours)
// Features:
//   • Auto-sequence new rows (10, 20, 30…)
//   • Preview schedule with minutes and ~hours
//   • Normalize Sequence
//   • Recalculate Totals (calls doc.recalc and only updates if changed)

frappe.ui.form.on('Setup Template', {
  refresh(frm) {
    if (!frm.is_new()) add_tools(frm);
  }
});

// Child table behavior (Clarinet Template Task)
frappe.ui.form.on('Clarinet Template Task', {
  // Auto-sequence new template tasks and sensible default duration
  template_tasks_add(frm, cdt, cdn) {
    const row = frappe.get_doc(cdt, cdn);
    const all = frm.doc.template_tasks || [];
    const maxSeq = all.reduce((m, r) => Math.max(m, cint(r.sequence || 0)), 0);
    row.sequence = maxSeq ? maxSeq + 10 : 10;       // gaps for reordering
    if (!row.exp_duration_mins) row.exp_duration_mins = 60; // default 60 mins
    frm.refresh_field('template_tasks');
  },

  // Keep minutes sane (no server roundtrip)
  exp_duration_mins(frm, cdt, cdn) {
    const row = frappe.get_doc(cdt, cdn);
    if (cint(row.exp_duration_mins) < 1) {
      row.exp_duration_mins = 1;
      frm.refresh_field('template_tasks');
      frappe.show_alert({ message: __('Minimum duration set to 1 minute.'), indicator: 'yellow' });
    }
  }
});

// ---------- helpers ----------

function add_tools(frm) {
  if (frm.__template_buttons_added) return;

  frm.add_custom_button(__('Preview Task Schedule'), () => preview_schedule_dialog(frm));
  frm.add_custom_button(__('Normalize Sequence'), () => normalize_sequence(frm));
  frm.add_custom_button(__('Recalculate Totals'), () => recalc_totals(frm));

  frm.__template_buttons_added = true;
}

function normalize_sequence(frm) {
  const rows = (frm.doc.template_tasks || []).slice();
  rows.sort((a, b) => cint(a.sequence || 0) - cint(b.sequence || 0));
  let seq = 10;
  rows.forEach(r => { r.sequence = seq; seq += 10; });
  frm.refresh_field('template_tasks');
  frappe.show_alert({ message: __('Sequence normalized.'), indicator: 'green' });
}

async function recalc_totals(frm) {
  // Only update if changed to prevent “flip-flop” on repeated clicks
  const EPS = 0.005; // 0.01/2 for 2dp fields
  const nearEq = (a, b) => Math.abs((parseFloat(a || 0)) - (parseFloat(b || 0))) < EPS;

  try {
    const r = await frm.call('recalc'); // server method on the document (idempotent)
    if (r && r.message) {
      const newHours = r.message.estimated_hours;
      const newCost  = r.message.estimated_cost;
      const oldHours = parseFloat(frm.doc.estimated_hours || 0);
      const oldCost  = parseFloat(frm.doc.estimated_cost || 0);

      let changed = false;
      if (!nearEq(newHours, oldHours)) {
        await frm.set_value('estimated_hours', newHours);
        changed = true;
      }
      if (!nearEq(newCost, oldCost)) {
        await frm.set_value('estimated_cost', newCost);
        changed = true;
      }

      frm.refresh_fields(['estimated_hours', 'estimated_cost']);
      frappe.show_alert({
        message: changed ? __('Recalculated.') : __('No changes. Totals already up to date.'),
        indicator: changed ? 'green' : 'blue'
      });
    }
  } catch (e) {
    console.error(e);
    frappe.msgprint({
      title: __('Recalculation Failed'),
      message: __('Could not recalculate totals. Check server logs.'),
      indicator: 'red'
    });
  }
}

function preview_schedule_dialog(frm) {
  const d = new frappe.ui.Dialog({
    title: __('Preview Task Schedule'),
    fields: [
      {
        fieldname: 'setup_date',
        fieldtype: 'Date',
        label: __('Setup Date'),
        reqd: 1,
        default: frm.doc.setup_date || frappe.datetime.get_today()
      },
      { fieldname: 'html_preview', fieldtype: 'HTML' }
    ],
    size: 'extra-large'
  });

  d.set_primary_action(__('Preview'), () => {
    const setup_date = d.get_value('setup_date');
    const rows = (frm.doc.template_tasks || []).slice()
      .sort((a, b) => cint(a.sequence || 0) - cint(b.sequence || 0));
    const html = render_preview(rows, setup_date);
    d.fields_dict.html_preview.$wrapper.html(html);

    // Bind the footer action inside THIS dialog only (avoid global duplicate handlers)
    d.fields_dict.html_preview.$wrapper
      .find('[data-action="recalc-now"]')
      .off('click.recalc')
      .on('click.recalc', async () => { await recalc_totals(frm); });
  });

  d.show();
  // Auto-run once
  d.get_primary_btn().click();
}

/**
 * Render preview table
 * - Start date = setup_date + exp_start_offset_days
 * - Duration column shows "<mins> mins (~<hours> h)"
 * - End date approximated as start + ceil(mins / (24*60)) days (calendar days)
 */
function render_preview(rows, setup_date) {
  let total_mins = 0;

  const lines = rows.map(r => {
    const seq = cint(r.sequence || 0);
    const minutes = Math.max(1, cint(r.exp_duration_mins || 0));
    total_mins += minutes;

    const start = frappe.datetime.add_days(setup_date, cint(r.exp_start_offset_days || 0));
    const span_days = Math.ceil(minutes / (24 * 60)); // 1440 mins/day
    const end = frappe.datetime.add_days(start, Math.max(0, span_days - 1));

    const hours_float = minutes / 60.0;
    const hours_disp = (Math.round(hours_float * 100) / 100).toFixed(2);

    return `
      <tr>
        <td style="padding:4px;">${seq}</td>
        <td style="padding:4px;">${frappe.utils.escape_html(r.subject || '')}</td>
        <td style="padding:4px;">${frappe.utils.escape_html(r.default_priority || 'Medium')}</td>
        <td style="padding:4px;">${frappe.datetime.str_to_user(start)}</td>
        <td style="padding:4px;">${frappe.datetime.str_to_user(end)}</td>
        <td style="padding:4px; text-align:right;">
          ${minutes.toLocaleString()} ${__('min')}
          <span class="text-muted">(~${hours_disp} ${__('h')})</span>
        </td>
      </tr>`;
  });

  const total_hours = Math.round((total_mins / 60.0) * 100) / 100;

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
            <th class="text-right">${__('Duration')}</th>
          </tr>
        </thead>
        <tbody>${lines.join('')}</tbody>
        <tfoot>
          <tr>
            <th colspan="5" class="text-right">${__('Total')}</th>
            <th class="text-right">
              ${total_mins.toLocaleString()} ${__('min')}
              <span class="text-muted">(~${total_hours.toFixed(2)} ${__('h')})</span>
            </th>
          </tr>
        </tfoot>
      </table>
      <div class="mt-2">
        <button class="btn btn-sm btn-primary" data-action="recalc-now">
          ${__('Apply to Estimated Hours/Cost')}
        </button>
      </div>
    </div>
  `;
}
