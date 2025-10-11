// -*- coding: utf-8 -*-
// Absolute Path: /home/frappe/frappe-bench/apps/repair_portal/repair_portal/intake/doctype/clarinet_intake/clarinet_intake.js
// Last Updated: 2025-09-19
// Version: v2.0.0 (UX hardening: async/await, debounce, safe guards, quick actions)
// Purpose:
//   Client UX for Clarinet Intake (Frappe v15)
//   • Fast, safe lookups with debounce + freeze overlays
//   • Dynamic required fields by intake type
//   • One-click navigation to related docs (Inspection / Initial Setup / Instrument)
//   • Sensible query filters for links

(() => {
  const METHODS = {
    inspectionName:
      'repair_portal.intake.doctype.clarinet_intake.clarinet_intake.get_instrument_inspection_name',
    instrumentBySerial:
      'repair_portal.intake.doctype.clarinet_intake.clarinet_intake.get_instrument_by_serial',
  };

  // Simple debounce utility
  function debounce(fn, wait = 350) {
    let t = null;
    return function (...args) {
      clearTimeout(t);
      t = setTimeout(() => fn.apply(this, args), wait);
    };
  }

  // Apply dynamic "reqd" flags based on intake_type
  function apply_dynamic_required(frm) {
    const required_fields = {
      'New Inventory': ['item_code', 'item_name', 'acquisition_cost', 'store_asking_price'],
      Repair: ['customer', 'customers_stated_issue'],
      Maintenance: ['customer', 'customers_stated_issue'],
    };
    Object.keys(required_fields).forEach((type) => {
      (required_fields[type] || []).forEach((field) => {
        frm.toggle_reqd(field, frm.doc.intake_type === type);
      });
    });
  }

  // Link field queries for safer pickers
  function set_queries(frm) {
    // Active customers only
    frm.set_query('customer', () => ({
      filters: { disabled: 0 },
    }));

    // Only active instrument categories if schema supports it
    frm.set_query('instrument_category', () => ({
      filters: { is_active: 1 },
    }));

    // Brands (Manufacturer) — no special filter, but searchable
    frm.set_query('manufacturer', () => ({}));

    // Work Orders that are not completed (if used for Repair/Maintenance)
    frm.set_query('work_order_number', () => ({
      filters: [['status', 'not in', ['Completed', 'Cancelled']]],
    }));

    // Assigning user (Employee/Technician) — enabled users only
    frm.set_query('employee', () => ({
      filters: { enabled: 1 },
    }));
  }

  // Add Settings button for managers
  function add_settings_button(frm) {
    if (frappe.user.has_role('System Manager') || frappe.user.has_role('Repair Manager')) {
      frm.add_custom_button(
        __('Settings'),
        () => frappe.set_route('Form', 'Clarinet Intake Settings'),
        __('Actions')
      );
    }
  }

  // Add "View" group buttons once the doc exists
  async function add_view_buttons(frm) {
    if (frm.doc.__islocal) return;

    // Instrument Inspection (via whitelisted method)
    try {
      const { message: insp } = await frappe.call({
        method: METHODS.inspectionName,
        args: { intake_record_id: frm.doc.name },
        freeze: false,
      });
      if (insp) {
        frm.add_custom_button(
          __('Instrument Inspection'),
          () => frappe.set_route('Form', 'Instrument Inspection', insp),
          __('View')
        );
      }
    } catch (e) {
      // Non-fatal
      // eslint-disable-next-line no-console
      console.warn('Inspection lookup failed:', e);
    }

    // Initial Setup (for New Inventory + instrument present)
    if (frm.doc.intake_type === 'New Inventory' && frm.doc.instrument) {
      try {
        const rows = await frappe.db.get_list('Clarinet Initial Setup', {
          filters: { instrument: frm.doc.instrument },
          fields: ['name'],
          limit: 1,
        });
        if (rows && rows.length) {
          frm.add_custom_button(
            __('Initial Setup'),
            () => frappe.set_route('Form', 'Clarinet Initial Setup', rows[0].name),
            __('View')
          );
        }
      } catch (e) {
        // Non-fatal
        // eslint-disable-next-line no-console
        console.warn('Initial Setup lookup failed:', e);
      }
    }

    // Instrument (if linked)
    if (frm.doc.instrument) {
      frm.add_custom_button(
        __('Instrument'),
        () => frappe.set_route('Form', 'Instrument', frm.doc.instrument),
        __('View')
      );
    }
  }

  // Optional "Make" actions (kept conservative to avoid relying on server methods)
  function add_make_buttons(frm) {
    if (frm.doc.__islocal) return;

    // Create Repair Order prefilled (if your schema supports these fields)
    frm.add_custom_button(
      __('Repair Order'),
      () => {
        const doc = frappe.model.get_new_doc('Repair Order');
        // Best-effort prefill; missing fields will be ignored by server if not in schema
        doc.instrument = frm.doc.instrument || null;
        doc.customer = frm.doc.customer || null;
        doc.intake = frm.doc.name;
        doc.player_profile = frm.doc.player_profile || null;
        frappe.ui.form.make_quick_entry('Repair Order', null, null, doc);
      },
      __('Make')
    );
  }

  // Debounced serial fetch
  const debounced_serial_fetch = debounce(async function (frm) {
    if (!frm.doc.serial_no || !frm.doc.serial_no.trim()) return;

    try {
      const { message } = await frappe.call({
        method: METHODS.instrumentBySerial,
        args: { serial_no: frm.doc.serial_no.trim() },
        freeze: true,
        freeze_message: __('Looking up instrument…'),
      });

      if (message) {
        // Fill only empty fields so we don't clobber user edits
        Object.keys(message).forEach((key) => {
          if (!frm.doc[key] && message[key] != null) {
            frm.set_value(key, message[key]);
          }
        });
      }
    } catch (e) {
      frappe.msgprint({
        title: __('Lookup Failed'),
        message: __('Could not fetch instrument by serial. See console for details.'),
        indicator: 'red',
      });
      // eslint-disable-next-line no-console
      console.error(e);
    }
  }, 350);

  frappe.ui.form.on('Clarinet Intake', {
    setup(frm) {
      set_queries(frm);
    },

    onload(frm) {
      apply_dynamic_required(frm);
    },

    refresh: async function (frm) {
      add_settings_button(frm);
      apply_dynamic_required(frm);
      await add_view_buttons(frm);
      add_make_buttons(frm);
    },

    intake_type(frm) {
      apply_dynamic_required(frm);
    },

    // Debounced serial lookup and autofill
    serial_no(frm) {
      debounced_serial_fetch(frm);
    },
  });
})();
