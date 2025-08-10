// File Header Template
// Relative Path: repair_portal/instrument_setup/doctype/clarinet_pad_map/clarinet_pad_map.js
// Last Updated: 2025-08-09
// Version: v2.3
// Purpose: Robust client logic:
//  - Auto-populate via server whether the doc is saved or not.
//  - If unsaved, send doc_json and patch rows locally (no reload needed).
//  - If saved, send docname and reload.
//  - Enforce is_open_key on child edits for soprano & bass.

frappe.ui.form.on('Clarinet Pad Map', {
    instrument_category(frm) {
        if (should_autopopulate(frm)) {
            call_server_populate(frm);
        }
    },

    refresh(frm) {
        frm.add_custom_button('Auto-Populate Pads', function () {
            if (!should_autopopulate(frm)) {
                frappe.msgprint({
                    title: __('Nothing to do'),
                    message: __('Auto-populate runs only when both pad tables are empty and the category is recognized (Soprano or Bass).'),
                    indicator: 'blue'
                });
                return;
            }
            call_server_populate(frm);
        }, 'Actions');
    }
});

// Client hints; server does authoritative detection
const SOPRANO_TYPES = new Set(["B♭", "A", "C", "D", "E♭"]);
const BASS_ALIASES = [
    "Bass — Low E♭",
    "Bass — Low C",
    "Bass — Low D",
    "Bass — Low D ext",
    "Bass Clarinet - Low Eb",
    "Bass Clarinet (Low Eb)",
    "Bass Clarinet Low Eb",
    "Bass Clarinet Short",
    "Bass Clarinet (Short, Low Eb)",
    "Bass Clarinet — Low E♭",
    "Bass Clarinet - Low E♭",
    "Bass Clarinet - Low C",
    "Bass Clarinet (Low C)",
    "Bass Clarinet Low C",
    "Bass Clarinet Extended",
    "Bass Clarinet (Extended, Low C)",
    "Bass Clarinet - Low D Ext",
    "Bass Clarinet (Low D Extension)",
    "Bass Clarinet Low D Extension",
    "Bass Clarinet - Low D w/ Extension",
    "Bass Clarinet - Low D with Extension",
    "Bass Clarinet (Removable Low D)",
    "Bass Clarinet - Low D"
];

function looks_like_bass(category_title) {
    if (!category_title) return false;
    const t = String(category_title).toLowerCase();
    if (t.includes("bass clarinet")) return true;
    return BASS_ALIASES.map(a => a.toLowerCase()).some(a => a === t);
}

function should_autopopulate(frm) {
    const topEmpty = (frm.doc.top_joint_pads || []).length === 0;
    const bottomEmpty = (frm.doc.bottom_joint_pads || []).length === 0;
    const cat = frm.doc.instrument_category;
    const isSoprano = SOPRANO_TYPES.has(cat);
    const isBass = looks_like_bass(cat);
    return topEmpty && bottomEmpty && (isSoprano || isBass);
}

function call_server_populate(frm) {
    frm.disable_save();

    const isUnsaved = !frm.doc.name || frm.is_new() || frm.doc.__unsaved;

    const args = isUnsaved
        ? { doc_json: JSON.stringify(frm.doc) } // works pre-save; server returns rows
        : { docname: frm.doc.name };           // saved doc; server will save + we reload

    frappe.call({
        method: 'repair_portal.instrument_setup.doctype.clarinet_pad_map.clarinet_pad_map.populate_standard_pad_names',
        freeze: true,
        freeze_message: __('Generating pad map...'),
        args
    }).then((r) => {
        if (isUnsaved) {
            // Patch child tables in-place without reload
            const data = r.message || {};
            if (Array.isArray(data.top_joint_pads)) {
                frm.clear_table('top_joint_pads');
                data.top_joint_pads.forEach(row => frm.add_child('top_joint_pads', row));
                frm.refresh_field('top_joint_pads');
            }
            if (Array.isArray(data.bottom_joint_pads)) {
                frm.clear_table('bottom_joint_pads');
                data.bottom_joint_pads.forEach(row => frm.add_child('bottom_joint_pads', row));
                frm.refresh_field('bottom_joint_pads');
            }
            frappe.show_alert({ message: __('Pad map prepared (unsaved). Review, then Save.'), indicator: 'green' });
        } else {
            // Saved path: reload to reflect persisted rows
            return frm.reload_doc().then(() => {
                frappe.show_alert({ message: __('Pad map auto-populated.'), indicator: 'green' });
            });
        }
    }).catch((err) => {
        const msg = (err && err.message) || (err && err.exc) || 'Unknown error';
        frappe.msgprint({
            title: __('Auto-populate Failed'),
            message: __(msg),
            indicator: 'red'
        });
    }).finally(() => {
        frm.enable_save();
    });
}

// --- Child table guardrails: is_open_key when pad_position changes (soprano + bass)
// MUST match backend OPEN_KEY_POSITIONS_* sets.
const OPEN_KEY_POSITIONS = new Set([
    // Soprano
    "E/B Ring (LH 1)",
    "D/A Ring (LH 2)",
    "3 Ring Key",
    "F/C Pinky Key",
    "E/B Pinky Key",
    "E♭/B♭ Pinky Key (optional)",
    // Bass
    "LH 1 Plateau (E/B)",
    "LH 2 Plateau (D/A)",
    "LH 3 Plateau (C/G)",
    "RH 1 Plateau (E/B)",
    "RH 2 Plateau (D/A)",
    "RH 3 Plateau (C/G)"
]);

frappe.ui.form.on('Clarinet Pad Entry', {
    pad_position(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (!row) return;

        if (row.pad_position && OPEN_KEY_POSITIONS.has(row.pad_position)) {
            row.is_open_key = 1;
        } else if (row.is_open_key === undefined || row.is_open_key === null || row.is_open_key === "") {
            row.is_open_key = 0;
        }

        if (row.parentfield) {
            frm.refresh_field(row.parentfield);
        } else {
            frm.refresh_field('top_joint_pads');
            frm.refresh_field('bottom_joint_pads');
        }
    }
});