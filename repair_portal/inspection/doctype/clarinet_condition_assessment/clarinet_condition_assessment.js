// File: repair_portal/repair_portal/inspection/doctype/clarinet_condition_assessment/clarinet_condition_assessment.js
// Updated: 2025-06-12
// Purpose: Enhance form UX with color and conditional visibility + timer

let startTime = null, interval = null;

frappe.ui.form.on('Clarinet Condition Assessment', {
  refresh(frm) {
    // Color-coded condition banner
    frm.dashboard.set_headline_alert(frm.doc.instrument_condition, get_color(frm.doc.instrument_condition));
  },

  onload(frm) {
    startTime = new Date();
    interval = setInterval(() => {
      const now = new Date();
      const diffSec = Math.floor((now - startTime) / 1000);
      const mins = Math.floor(diffSec / 60);
      const secs = diffSec % 60;
      const display = `${mins}m ${secs}s elapsed`;
      frm.dashboard.set_headline_alert(display, 'blue');
    }, 1000);
  },

  before_save(frm) {
    if (startTime) {
      const now = new Date();
      const diffSec = Math.floor((now - startTime) / 1000);
      frm.set_value('inspection_duration', diffSec);
      clearInterval(interval);
    }
  },

  instrument_condition(frm) {
    frm.toggle_display('notes', frm.doc.instrument_condition === 'Poor');
  }
});

function get_color(condition) {
  switch (condition) {
    case 'Good': return 'green';
    case 'Fair': return 'orange';
    case 'Poor': return 'red';
    default: return 'blue';
  }
}