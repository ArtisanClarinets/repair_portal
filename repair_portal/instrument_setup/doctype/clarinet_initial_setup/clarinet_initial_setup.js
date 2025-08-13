// File: repair_portal/repair_portal/instrument_setup/doctype/clarinet_initial_setup/clarinet_initial_setup.js

frappe.ui.form.on('Clarinet Initial Setup', {
  refresh(frm) {
    set_headline(frm);
    show_progress(frm);

    if (frm.doc.docstatus === 0) {
      add_draft_buttons(frm);
    }

    add_nav_buttons(frm);
    add_certificate_button(frm);   // <— NEW
  },

  setup_template(frm) {
    if (!frm.is_new() && frm.doc.setup_template) {
      frappe.show_alert({
        message: __('Template selected. Use the buttons to load operations and create tasks.'),
        indicator: 'blue'
      });
    }
  }
});

// ---------- helpers ----------

function set_headline(frm) {
  if (frm.doc.status === 'Pass') {
    frm.dashboard.set_headline(__('Setup passed QA.'));
  } else if (frm.doc.status === 'Fail') {
    frm.dashboard.set_headline(__('Setup requires rework.'));
  } else {
    frm.dashboard.set_headline(__('Setup in progress.'));
  }
}

function show_progress(frm) {
  const pct = cint(frm.doc.progress || 0);
  frm.dashboard.add_progress(__('Overall Progress'), [
    { title: __('Progress'), width: pct + '%', progress_class: (pct === 100 ? 'progress-bar-success' : 'progress-bar-info') }
  ]);
}

function add_draft_buttons(frm) {
  if (frm.__clarinet_buttons_added) return;

  frm.add_custom_button(__('Load Operations from Template'), async () => {
    if (!ensure_saved(frm)) return;
    if (!frm.doc.setup_template) {
      frappe.msgprint({ message: __('Please select a Setup Template first.'), indicator: 'red' });
      return;
    }
    try {
      frappe.dom.freeze(__('Loading operations...'));
      await frappe.call({ doc: frm.doc, method: 'load_operations_from_template' });
      await frm.reload_doc();
      frappe.show_alert({ message: __('Operations loaded.'), indicator: 'green' });
    } catch (e) {
      frappe.msgprint({ message: __(e.message || 'Failed to load operations.'), indicator: 'red' });
    } finally {
      frappe.dom.unfreeze();
    }
  });

  frm.add_custom_button(__('Create Tasks from Template'), async () => {
    if (!ensure_saved(frm)) return;
    if (!frm.doc.setup_template) {
      frappe.msgprint({ message: __('Please select a Setup Template first.'), indicator: 'red' });
      return;
    }
    try {
      frappe.dom.freeze(__('Creating tasks...'));
      const r = await frappe.call({ doc: frm.doc, method: 'create_tasks_from_template' });
      const count = (r && r.message && r.message.count) ? r.message.count : 0;
      frappe.show_alert({ message: __('Created {0} task(s).', [count]), indicator: 'green' });
    } catch (e) {
      frappe.msgprint({ message: __(e.message || 'Failed to create tasks.'), indicator: 'red' });
    } finally {
      frappe.dom.unfreeze();
    }
  });

  frm.__clarinet_buttons_added = true;
}

function add_nav_buttons(frm) {
  frm.add_custom_button(__('View Tasks'), () => {
    if (!ensure_saved(frm)) return;
    frappe.route_options = { 'clarinet_initial_setup': frm.doc.name };
    frappe.set_route('List', 'Clarinet Setup Task');
  }, __('Navigate'));

  frm.add_custom_button(__('Open Gantt'), () => {
    if (!ensure_saved(frm)) return;
    frappe.route_options = { 'clarinet_initial_setup': frm.doc.name };
    frappe.set_route('List', 'Clarinet Setup Task', 'Gantt');
  }, __('Navigate'));
}

// NEW: “Generate Certificate (PDF)” button
function add_certificate_button(frm) {
  if (frm.is_new()) return;
  if (frm.__clarinet_cert_button_added) return;

  frm.add_custom_button(__('Generate Certificate (PDF)'), async () => {
    try {
      frappe.dom.freeze(__('Generating certificate...'));
      const r = await frappe.call({
        doc: frm.doc,
        method: 'generate_certificate',
        args: {
          print_format: 'Clarinet Setup Certificate',
          attach: 1,
          return_file_url: 1
        }
      });

      const url = r && r.message && r.message.file_url;
      if (url) {
        // Open the private file (user must be logged in)
        window.open(url, '_blank');
        frappe.show_alert({ message: __('Certificate generated.'), indicator: 'green' });
      } else {
        frappe.msgprint({ message: __('Certificate created but no file URL returned.'), indicator: 'orange' });
      }
    } catch (e) {
      frappe.msgprint({ message: __(e.message || 'Failed to generate certificate.'), indicator: 'red' });
    } finally {
      frappe.dom.unfreeze();
    }
  }, __('Actions'));

  frm.__clarinet_cert_button_added = true;
}

function ensure_saved(frm) {
  if (frm.is_new()) {
    frappe.msgprint({ message: __('Please save this document first.'), indicator: 'orange' });
    return false;
  }
  return true;
}
