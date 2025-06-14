// File: repair_portal/repair_portal/intake/doctype/clarinet_intake/clarinet_intake.js
// Updated: 2025-06-12
// Purpose: Implements real-time intake timer and tag escalation logic

let intakeStartTime = null;

frappe.ui.form.on('Clarinet Intake', {
  onload(frm) {
    intakeStartTime = new Date();
    frm.dashboard.set_headline_alert('⏱ Intake started', 'blue');
  },

  before_save(frm) {
    if (intakeStartTime) {
      const now = new Date();
      const diffSec = Math.floor((now - intakeStartTime) / 1000);
      frm.set_value('intake_duration', diffSec);
    }
  },

  workflow_state(frm) {
    if (frm.doc.workflow_state === 'Escalated') {
      frm.add_tag('Follow-Up');
    }
  }
});