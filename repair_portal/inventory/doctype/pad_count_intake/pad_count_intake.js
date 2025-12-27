// Path: repair_portal/inventory/doctype/pad_count_intake/pad_count_intake.js
// Last Updated: 2025-08-21
// Version: v1.4.0 (Improved UX: rich descriptions for Shooting Kit prompts; clearer field help and guidance.)
// Purpose: Client UX for Pad Count Intake: process image, approve count, update inventory,
//          generate & attach kit (saved doc), and direct-download kit (pre-save) with
//          detailed field explanations so users know exactly what each option means.
// Function List:
//   refresh(frm)                - Adds Download/Generate kit, Process, Approve, Update, and JSON viewer; sets queries.
//   photo(frm)                  - Resets derived fields on new upload.
//   show_quality(frm)           - Shows quality banner when flags_quality_ok is false.
//   fetch_meta(frm)             - Opens detections JSON in dialog.
//   open_kit_dialog(frm, mode)  - Builds a descriptive dialog for kit options (mode: 'download' | 'attach').
//   generate_shooting_kit(...)  - Server attach flow (saved doc).
//   download_shooting_kit(...)  - Direct-download flow (works before save).

frappe.ui.form.on('Pad Count Intake', {
  refresh(frm) {
    // Always available: pre-save Download (no attachment required)
    frm.add_custom_button('Download Shooting Kit (PDF)', () => open_kit_dialog(frm, 'download'));

    // Saved docs: Generate & attach (also sets Photo and appends notes)
    if (!frm.doc.__islocal) {
      frm.add_custom_button('Generate Shooting Kit (PDF)', () => open_kit_dialog(frm, 'attach'));

      frm.add_custom_button('Process Image', () => {
        frappe.call({
          method: 'repair_portal.inventory.doctype.pad_count_intake.pad_count_intake.process_image',
          args: { name: frm.doc.name },
          freeze: true,
          freeze_message: 'Processing image...'
        }).then(() => frm.reload_doc());
      });

      frm.add_custom_button('Approve Count', () => {
        const detected = frm.doc.detected_count || 0;
        frappe.prompt(
          [{ fieldname: 'approved', label: 'Approved Count', fieldtype: 'Int', reqd: 1, default: detected }],
          (v) => {
            frappe.call({
              method: 'repair_portal.inventory.doctype.pad_count_intake.pad_count_intake.approve_count',
              args: { name: frm.doc.name, approved_count: v.approved },
              freeze: true
            }).then(() => frm.reload_doc());
          },
          'Review & Approve',
          'Set'
        );
      });

      frm.add_custom_button('Update Inventory', () => {
        if (frm.doc.review_status !== 'Approved') {
          frappe.msgprint('Review Status must be "Approved" before updating inventory.');
          return;
        }
        frappe.confirm(
          `Proceed to update inventory?\nAction: ${frm.doc.inventory_action}\nDelta: ${frm.doc.inventory_delta}`,
          () => {
            frappe.call({
              method: 'repair_portal.inventory.doctype.pad_count_intake.pad_count_intake.update_inventory',
              args: { name: frm.doc.name },
              freeze: true
            }).then((r) => {
              frm.reload_doc();
              if (r.message && r.message.stock_entry) {
                frappe.msgprint(`Stock Entry: <a href="/app/stock-entry/${r.message.stock_entry}">${r.message.stock_entry}</a>`);
              }
            });
          }
        );
      });

      if (frm.doc.detections_meta) {
        frm.add_custom_button('View Detections JSON', () => fetch_meta(frm));
      }
    }

    // Field queries & conveniences
    frm.set_query('item', () => ({ filters: { is_stock_item: 1 } }));
    frm.set_query('uom', () => ({ filters: { uom_name: ['in', ['Nos', 'Each']] } }));
    if (frm.doc.approved_count && (!frm.doc.inventory_delta || frm.doc.inventory_delta === 0)) {
      frm.set_value('inventory_delta', frm.doc.approved_count);
    }

    show_quality(frm);
  },

  photo(frm) {
    frm.set_value({
      detected_count: 0,
      processed_preview: null,
      detections_meta: null,
      flags_quality_ok: 0,
      review_status: 'Pending Review',
      processed_at: null
    });
  }
});

function show_quality(frm) {
  if (frm.doc.flags_quality_ok === 0) {
    frm.dashboard.clear_headline();
    frm.dashboard.set_headline_alert(
      'Image quality is low (blur/lighting). Please retake with top-down view on a dark, matte background.',
      'red'
    );
  } else {
    frm.dashboard.clear_headline();
  }
}

function fetch_meta(frm) {
  if (!frm.doc.detections_meta) return;
  const url = frm.doc.detections_meta;
  const full = window.location.origin + url;
  const d = new frappe.ui.Dialog({
    title: 'Detections JSON',
    size: 'large'
  });
  d.$body.html(`<div style="height:400px; overflow:auto;"><pre style="white-space:pre-wrap;word-break:break-word;">Loading...</pre></div>`);
  fetch(full, { credentials: 'include' })
    .then(r => r.text())
    .then(t => {
      try {
        const pretty = JSON.stringify(JSON.parse(t), null, 2);
        d.$body.find('pre').text(pretty);
      } catch (e) {
        d.$body.find('pre').text(t);
      }
    })
    .catch(() => d.$body.find('pre').text('Failed to load JSON.'));
  d.show();
}

/**
 * Build the descriptive Shooting Kit dialog.
 * mode: 'download' (works before save) | 'attach' (requires saved doc, attaches files)
 */
function open_kit_dialog(frm, mode) {
  const mm_default = frm.doc.aruco_marker_length_mm || 50;
  const dict_default = frm.doc.aruco_dict || 'DICT_4X4_50';
  const pad_mm_default = frm.doc.pad_diameter_mm || 10;

  // Rich, plain-English descriptions so nobody has to guess
  const intro_html = `
  <div style="margin-bottom: 8px; line-height:1.45">
    <div><b>What is this?</b> The Shooting Kit is a print-ready PDF that includes an ArUco marker (square code) and a 100&nbsp;mm ruler. 
    Place the marker in your photo so the system can auto-calc <i>true size in millimeters</i> and correct perspective.</div>
    <div style="margin-top:6px"><b>How do these fields affect counting?</b></div>
    <ul style="margin:6px 0 0 18px;padding:0;">
      <li><b>Marker Side (mm)</b>: The physical size you will <i>print</i> the marker at. This must match your printout, otherwise scale will be wrong.</li>
      <li><b>ArUco Dictionary</b>: The family of marker patterns. Keep this the same as on the PDF (default DICT_4X4_50). It doesn’t change accuracy—just the pattern.</li>
      <li><b>Pad Diameter (mm)</b>: Typical clarinet pad diameter. We use this to auto-derive the pad <i>pixel radius</i> after reading the marker scale, making detection more reliable.</li>
    </ul>
  </div>`;

  const dialog = new frappe.ui.Dialog({
    title: mode === 'download' ? 'Download Shooting Kit (no save required)' : 'Shooting Kit Options (attach to this document)',
    fields: [
      { fieldtype: 'HTML', fieldname: 'intro', options: intro_html },
      {
        fieldname: 'marker_mm',
        label: 'Marker Side (mm)',
        fieldtype: 'Float',
        reqd: 1,
        default: mm_default,
        description:
          'Print size of the square marker. Example: 50 means the black square is exactly 50 mm on each side. ' +
          'Match this to your printer output; use the built-in 100 mm ruler to verify scaling.'
      },
      {
        fieldname: 'aruco_dict',
        label: 'ArUco Dictionary',
        fieldtype: 'Select',
        reqd: 1,
        options: 'DICT_4X4_50\nDICT_4X4_100\nDICT_5X5_50\nDICT_5X5_100\nDICT_6X6_50\nDICT_6X6_100\nDICT_APRILTAG_36h11',
        default: dict_default,
        description:
          'Marker pattern family. Keep this consistent between the printed PDF and the detector (default DICT_4X4_50). ' +
          'No need to change unless you have a specific standard.'
      },
      {
        fieldname: 'pad_mm',
        label: 'Pad Diameter (mm)',
        fieldtype: 'Float',
        reqd: 1,
        default: pad_mm_default,
        description:
          'Typical pad size (e.g., 9–12 for clarinet). We convert this to pixels using the marker scale to auto-tune detection radius.'
      }
    ],
    primary_action_label: mode === 'download' ? 'Download' : 'Generate & Attach',
    size: 'large',
    primary_action(values) {
      if (mode === 'download') {
        download_shooting_kit(frm, values.marker_mm, values.aruco_dict, values.pad_mm);
      } else {
        if (frm.doc.__islocal) {
          frappe.msgprint('Please save the document first so the PDF and instruction image can be attached here.');
          return;
        }
        generate_shooting_kit(frm, values.marker_mm, values.aruco_dict);
      }
      dialog.hide();
    }
  });

  dialog.show();
}

function generate_shooting_kit(frm, marker_mm, aruco_dict) {
  frappe.call({
    method: 'repair_portal.inventory.doctype.pad_count_intake.pad_count_intake.generate_shooting_kit',
    args: { name: frm.doc.name, marker_mm, aruco_dict },
    freeze: true,
    freeze_message: 'Generating PDF & instructions...'
  }).then((r) => {
    frm.reload_doc().then(() => {
      if (r.message && r.message.pdf_url) {
        frappe.msgprint(
          `Shooting kit attached: <a href="${r.message.pdf_url}" target="_blank" rel="noopener noreferrer">${r.message.pdf_url}</a><br/>` +
          `An instruction image was placed into the Photo field.`
        );
      }
    });
  });
}

function download_shooting_kit(frm, marker_mm, aruco_dict, pad_mm) {
  const base = '/api/method/repair_portal.inventory.doctype.pad_count_intake.pad_count_intake_api.generate_shooting_kit_preview';
  const params = new URLSearchParams({
    aruco_dict: aruco_dict || 'DICT_4X4_50',
    marker_length_mm: String(marker_mm || 50),
    pad_diameter_mm: String(pad_mm || 10),
    docname: frm.doc.name || 'New'
  });
  window.open(`${base}?${params.toString()}`, '_blank');
}
