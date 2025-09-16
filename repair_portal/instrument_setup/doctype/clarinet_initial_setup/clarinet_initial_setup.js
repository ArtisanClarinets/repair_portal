// File: repair_portal/repair_portal/instrument_setup/doctype/clarinet_initial_setup/clarinet_initial_setup.js
// Last Updated: 2025-09-16
// Purpose: Auto-apply Setup Template on selection, keep buttons after refresh, and streamline project actions.

frappe.ui.form.on('Clarinet Initial Setup', {
  refresh: async function (frm) {
    set_headline(frm);
    show_progress(frm);
    show_project_timeline(frm);

    if (frm.doc.docstatus === 0) {
      add_draft_buttons(frm);      // always re-add; no "added once" guard
    }

    add_nav_buttons(frm);
    add_certificate_button(frm);
    add_project_actions(frm);
  },

  // Auto-apply the template the moment it’s chosen (even on new/unsaved docs).
  setup_template: async function (frm) {
    if (!frm.doc.setup_template) return;
    await apply_setup_template(frm);
  },

  status(frm) {
    update_status_indicators(frm);
  },

  expected_start_date(frm) {
    calculate_expected_end_date(frm);
  },

  labor_hours(frm) {
    calculate_expected_end_date(frm);
    calculate_estimated_costs(frm);
  }
});

// ---------- Template application ----------

async function apply_setup_template(frm) {
  try {
    frappe.dom.freeze(__('Applying setup template...'));

    // 1) Pull the template doc and push its defaults onto the form
    const tpl = await frappe.db.get_doc('Setup Template', frm.doc.setup_template);
    // Always set to the template’s values (explicit template selection is an override)
    await frm.set_value({
      setup_type: tpl.setup_type || frm.doc.setup_type,
      priority: tpl.priority || frm.doc.priority,
      technician: tpl.default_technician || frm.doc.technician,
      labor_hours: tpl.estimated_hours || frm.doc.labor_hours,
      estimated_materials_cost: tpl.estimated_materials_cost || frm.doc.estimated_materials_cost,
      estimated_cost: tpl.estimated_cost || frm.doc.estimated_cost
    });

    // Ensure we have a baseline date for task scheduling
    if (!frm.doc.expected_start_date) {
      await frm.set_value('expected_start_date', frappe.datetime.get_today());
    }

    // 2) We need a real docname for server-side generators → save transparently if needed
    await ensure_saved(frm);

    // 3) Load operations & checklist from template (server appends and saves)
    await frappe.call({ doc: frm.doc, method: 'load_operations_from_template' });

    // 4) Create tasks from template (uses minutes now, server-side)
    await frappe.call({ doc: frm.doc, method: 'create_tasks_from_template' });

    await frm.reload_doc();

    frappe.show_alert({ message: __('Template applied: fields, operations, and tasks created.'), indicator: 'green' });
  } catch (e) {
    console.error(e);
    frappe.msgprint({
      title: __('Template Apply Failed'),
      message: __(e.message || 'Could not apply the setup template. Check server logs.'),
      indicator: 'red'
    });
  } finally {
    frappe.dom.unfreeze();
  }
}

// ---------- Existing helpers (unchanged UI behaviour) ----------

function set_headline(frm) {
  if (frm.doc.status === 'Completed') {
    frm.dashboard.set_headline(__('Setup project completed successfully.'));
  } else if (frm.doc.status === 'QA Review') {
    frm.dashboard.set_headline(__('Setup awaiting quality review.'));
  } else if (frm.doc.status === 'On Hold') {
    frm.dashboard.set_headline(__('Setup project is on hold.'));
  } else if (frm.doc.status === 'Cancelled') {
    frm.dashboard.set_headline(__('Setup project was cancelled.'));
  } else {
    frm.dashboard.set_headline(__('Setup project in progress.'));
  }
}

function show_progress(frm) {
  const pct = cint(frm.doc.progress || 0);
  frm.dashboard.add_progress(__('Overall Progress'), [
    { title: __('Progress'), width: pct + '%', progress_class: (pct === 100 ? 'progress-bar-success' : 'progress-bar-info') }
  ]);
}

function show_project_timeline(frm) {
  if (frm.doc.expected_start_date || frm.doc.expected_end_date) {
    let timeline_html = '<div class="row"><div class="col-sm-6">';
    if (frm.doc.expected_start_date) {
      timeline_html += `<p><strong>${__('Expected Start')}:</strong> ${frappe.datetime.str_to_user(frm.doc.expected_start_date)}</p>`;
    }
    if (frm.doc.expected_end_date) {
      timeline_html += `<p><strong>${__('Expected End')}:</strong> ${frappe.datetime.str_to_user(frm.doc.expected_end_date)}</p>`;
    }
    timeline_html += '</div><div class="col-sm-6">';
    if (frm.doc.actual_start_date) {
      timeline_html += `<p><strong>${__('Actual Start')}:</strong> ${frappe.datetime.str_to_user(frm.doc.actual_start_date)}</p>`;
    }
    if (frm.doc.actual_end_date) {
      timeline_html += `<p><strong>${__('Actual End')}:</strong> ${frappe.datetime.str_to_user(frm.doc.actual_end_date)}</p>`;
    }
    timeline_html += '</div></div>';
    frm.dashboard.add_section(timeline_html, __('Project Timeline'));
  }
}

function calculate_expected_end_date(frm) {
  if (frm.doc.expected_start_date && frm.doc.labor_hours && !frm.doc.expected_end_date) {
    const days_needed = Math.max(1, Math.ceil(frm.doc.labor_hours / 8)); // same heuristic used before
    const end_date = frappe.datetime.add_days(frm.doc.expected_start_date, days_needed);
    frm.set_value('expected_end_date', end_date);
  }
}

function calculate_estimated_costs(frm) {
  if (frm.doc.labor_hours && !frm.doc.estimated_cost) {
    const hourly_rate = 75; // could be pulled from settings
    const labor_cost = frm.doc.labor_hours * hourly_rate;
    const materials_cost = frm.doc.estimated_materials_cost || 0;
    frm.set_value('estimated_cost', labor_cost + materials_cost);
  }
}

function update_status_indicators(frm) {
  if (frm.doc.status === 'In Progress' && !frm.doc.actual_start_date) {
    frm.set_value('actual_start_date', frappe.datetime.now_datetime());
  } else if (['Completed', 'QA Review'].includes(frm.doc.status) && !frm.doc.actual_end_date) {
    frm.set_value('actual_end_date', frappe.datetime.now_datetime());
  }
}

// ---------- Buttons ----------

function add_draft_buttons(frm) {
  // No "added once" guard — custom buttons disappear on refresh, so re-add every time.
  frm.add_custom_button(__('Load Operations from Template'), async () => {
    await ensure_saved(frm);
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
    await ensure_saved(frm);
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
}

function add_nav_buttons(frm) {
  frm.add_custom_button(__('View Tasks'), () => {
    if (!frm.doc.name) return;
    frappe.route_options = { 'clarinet_initial_setup': frm.doc.name };
    frappe.set_route('List', 'Clarinet Setup Task');
  }, __('Navigate'));

  frm.add_custom_button(__('Open Gantt'), () => {
    if (!frm.doc.name) return;
    frappe.route_options = { 'clarinet_initial_setup': frm.doc.name };
    frappe.set_route('List', 'Clarinet Setup Task', 'Gantt');
  }, __('Navigate'));
}

// “Generate Certificate (PDF)”
function add_certificate_button(frm) {
  if (frm.is_new()) return;
  if (frm.__clarinet_cert_button_added) return;

  frm.add_custom_button(__('Generate Certificate (PDF)'), async () => {
    try {
      frappe.dom.freeze(__('Generating certificate...'));
      const r = await frappe.call({
        doc: frm.doc,
        method: 'generate_certificate',
        args: { print_format: 'Clarinet Setup Certificate', attach: 1, return_file_url: 1 }
      });
      const url = r && r.message && r.message.file_url;
      if (url) {
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

// Save helper (auto-saves silently if needed)
async function ensure_saved(frm) {
  if (frm.is_new() || frm.is_dirty()) {
    await frm.save();
  }
  return true;
}
