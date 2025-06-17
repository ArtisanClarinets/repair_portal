// File: repair_portal/instrument_profile/doctype/repair_log/repair_log.js
// Updated: 2025-06-16
// Version: 1.0
// Purpose: Technician UI logic for SVG pad map interactivity in Repair Log

frappe.ui.form.on('Repair Log', {
  refresh(frm) {
    const MASTER_PAD_LIST = {
      'pad_register_key': 'Register Key',
      'pad_c_sharp': 'C#',
      'pad_a_key': 'A Key',
      'pad_g_sharp': 'G# Key'
      // Extend with all SVG pad IDs and names as needed
    };

    if (frm.is_new() && (!frm.doc.pad_conditions || !frm.doc.pad_conditions.length)) {
      Object.entries(MASTER_PAD_LIST).forEach(([id, name]) => {
        frm.add_child('pad_conditions', {
          pad_id: id,
          pad_name: name,
          status: 'OK'
        });
      });
      frm.refresh_field('pad_conditions');
    }

    render_pad_map(frm, MASTER_PAD_LIST);
  }
});

async function render_pad_map(frm, masterList) {
  const status_colors = {
    'OK': '#4CAF50',
    'Leaking': '#FFC107',
    'Replaced': '#F44336',
    'Adjusted': '#2196F3',
    'Requires Shim': '#9C27B0'
  };

  const response = await fetch('/assets/repair_portal/images/svg_pad_maps/clarinet_upper_joint.svg');
  const svg_data = await response.text();
  const $wrapper = $(frm.fields_dict.pad_map_view.wrapper);
  $wrapper.html(svg_data);

  function sync_colors() {
    frm.doc.pad_conditions.forEach(pad => {
      const color = status_colors[pad.status] || '#E0E0E0';
      $wrapper.find(`#${pad.pad_id}`).css('fill', color);
    });
  }

  $wrapper.find('circle[id^="pad_"], path[id^="pad_"]').each((_, el) => {
    const pad_id = $(el).attr('id');
    const row = frm.doc.pad_conditions.find(p => p.pad_id === pad_id);

    if (!row) return;

    $(el).on('click', () => {
      frappe.prompt([
        { fieldname: 'status', label: 'Status', fieldtype: 'Select', options: ['OK', 'Leaking', 'Replaced', 'Adjusted', 'Requires Shim'], default: row.status },
        { fieldname: 'notes', label: 'Technician Notes', fieldtype: 'Text', default: row.technician_notes }
      ], (values) => {
        frappe.model.set_value(row.doctype, row.name, 'status', values.status);
        frappe.model.set_value(row.doctype, row.name, 'technician_notes', values.notes);
        sync_colors();
      }, `Update: ${row.pad_name}`);
    });
  });

  sync_colors();
}