// File: repair_portal/repair_portal/instrument_setup/doctype/clarinet_setup_task/clarinet_setup_task.js
// Purpose: Desk UI for individual Tasks (Projects-like).
// - Quick actions: Start, Send to Review, Complete, Reopen
// - Dependency visibility & warnings
// - Safe status transitions (client hints; server enforces)

frappe.ui.form.on('Clarinet Setup Task', {
  refresh(frm) {
    show_status_banner(frm);
    add_status_buttons(frm);
    show_dependency_summary(frm);
  },

  // Quality of life: if opening from parent, auto-fill clarinet_initial_setup via route_options
  onload(frm) {
    if (frappe.route_options && frappe.route_options.clarinet_initial_setup && frm.is_new()) {
      frm.set_value('clarinet_initial_setup', frappe.route_options.clarinet_initial_setup);
    }
  }
});

// ---------- helpers ----------

function show_status_banner(frm) {
  const s = frm.doc.status || 'Open';
  const map = {
    'Completed': { txt: __('Completed'), color: 'green' },
    'Pending Review': { txt: __('Pending Review'), color: 'orange' },
    'Working': { txt: __('Working'), color: 'blue' },
    'Paused': { txt: __('Paused'), color: 'grey' },
    'Canceled': { txt: __('Canceled'), color: 'red' },
    'Open': { txt: __('Open'), color: 'yellow' }
  };
  const info = map[s] || map['Open'];
  frm.dashboard.set_headline(info.txt);
}

function add_status_buttons(frm) {
  if (frm.is_new()) return;

  // Clear duplicates
  if (frm.__clarinet_task_buttons) return;

  // Start Work
  if (['Open', 'Paused'].includes(frm.doc.status)) {
    frm.add_custom_button(__('Start Work'), async () => {
      await set_status(frm, 'Working');
    });
  }

  // Send to Review
  if (['Working'].includes(frm.doc.status)) {
    frm.add_custom_button(__('Send to Review'), async () => {
      await set_status(frm, 'Pending Review');
    });
  }

  // Complete
  if (['Open', 'Working', 'Pending Review'].includes(frm.doc.status)) {
    frm.add_custom_button(__('Complete Task'), async () => {
      await set_status(frm, 'Completed', { progress: 100 });
    }, __('Actions'));
  }

  // Reopen
  if (['Paused', 'Completed', 'Canceled'].includes(frm.doc.status)) {
    frm.add_custom_button(__('Reopen Task'), async () => {
      await set_status(frm, 'Open', { progress: 0 });
    }, __('Actions'));
  }

  // Pause
  if (['Open', 'Working'].includes(frm.doc.status)) {
    frm.add_custom_button(__('Pause Task'), async () => {
      await set_status(frm, 'Paused');
    }, __('Actions'));
  }

  frm.__clarinet_task_buttons = true;
}

async function set_status(frm, new_status, extra = {}) {
  try {
    frappe.dom.freeze(__('Updating status...'));
    await frm.set_value('status', new_status);
    if (extra && typeof extra.progress !== 'undefined') {
      await frm.set_value('progress', extra.progress);
    }
    await frm.save();
    frappe.show_alert({ message: __('Status updated: {0}', [new_status]), indicator: 'green' });
  } catch (e) {
    frappe.msgprint({ message: __(e.message || 'Could not update status.'), indicator: 'red' });
  } finally {
    frappe.dom.unfreeze();
    frm.reload_doc();
  }
}

function show_dependency_summary(frm) {
  if (!frm.doc.depends_on || !frm.doc.depends_on.length) return;
  const tasks = (frm.doc.depends_on || []).map(r => r.task).filter(Boolean);
  if (!tasks.length) return;

  // Check dependency statuses
  frappe.db.get_list('Clarinet Setup Task', {
    fields: ['name', 'status'],
    filters: { name: ['in', tasks] },
    limit: 500
  }).then(rows => {
    const pending = rows.filter(r => r.status !== 'Completed').map(r => `${r.name} (${r.status})`);
    if (pending.length) {
      frm.dashboard.set_badge_count(pending.length);
      frm.dashboard.set_headline(__('Waiting on: {0}', [pending.join(', ')]));
      frappe.show_alert({ message: __('Dependencies not completed: {0}', [pending.join(', ')]), indicator: 'orange' });
    }
  });
}
