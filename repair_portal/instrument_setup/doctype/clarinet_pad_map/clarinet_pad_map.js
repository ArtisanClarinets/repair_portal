// File Header Template
// Relative Path: repair_portal/instrument_setup/doctype/clarinet_pad_map/clarinet_pad_map.js
// Last Updated: 2025-07-28
// Version: v1.1
// Purpose: Auto-populate pads on Instrument Category change, before save

frappe.ui.form.on('Clarinet Pad Map', {
    instrument_category: function (frm) {
        // Only run if both tables are empty!
        if ((frm.doc.top_joint_pads || []).length === 0 && (frm.doc.bottom_joint_pads || []).length === 0) {
            // B♭, A, C, D, E♭ clarinets
            const standardTypes = ["B♭", "A", "C", "D", "E♭"];
            if (standardTypes.includes(frm.doc.instrument_category)) {
                const TOP = [
                    "Register Key",
                    "C Trill Key",
                    "B♭ Trill Key",
                    "F# Trill Key",
                    "B♭/E♭ Trill Key",
                    "A Key",
                    "G#/Ab Key",
                    "E/B Ring (LH 1)",
                    "D/A Ring (LH 2)",
                    "C/G Ring (LH 3)",
                    "Inline B♭/E♭ Key",
                    "C#/G# Key"
                ];
                const BOTTOM = [
                    "3 Ring Key",
                    "Inline F#/B Key",
                    "A♭/E♭ Pinky Key",
                    "F#/C# Pinky Key",
                    "F/C Pinky Key",
                    "E/B Pinky Key"
                ];
                // Populate Top Joint Pads
                TOP.forEach(function (name) {
                    frm.add_child("top_joint_pads", { pad_position: name });
                });
                // Populate Bottom Joint Pads
                BOTTOM.forEach(function (name) {
                    frm.add_child("bottom_joint_pads", { pad_position: name });
                });
                frm.refresh_field("top_joint_pads");
                frm.refresh_field("bottom_joint_pads");
            }
        }
    },
    refresh(frm) {
        frm.add_custom_button('Auto-Populate Pads', function () {
            frm.trigger('instrument_category');
        }, 'Actions');
    }
});

frappe.ui.form.on('Clarinet Pad Map', {
    refresh: function (frm) {
        if (!frm.is_new()) return;
        frm.add_custom_button('Auto-Populate Pads', function() {
            frappe.call({
                method: 'repair_portal.instrument_setup.doctype.clarinet_pad_map.clarinet_pad_map.populate_standard_pad_names',
                args: { docname: frm.doc.name },
                callback: function() {
                    frm.reload_doc();
                }
            });
        }, 'Actions');
    }
});
