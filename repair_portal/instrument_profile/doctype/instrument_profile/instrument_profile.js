frappe.ui.form.on('Instrument Profile', {
  refresh(frm) {
    if (frappe.user_roles.includes('System Manager')) {
      frm.add_custom_button('Renew Warranty', () => {
        frappe.prompt(
          [
            { fieldname: 'new_start_date', label: 'New Start Date', fieldtype: 'Date', reqd: 1 },
            { fieldname: 'new_end_date', label: 'New End Date', fieldtype: 'Date', reqd: 1 },
            { fieldname: 'reason', label: 'Reason for Renewal', fieldtype: 'Data', reqd: 1 },
          ],
          (values) => {
            frm.set_value('warranty_start_date', values.new_start_date);
            frm.set_value('warranty_end_date', values.new_end_date);
            frm.set_value('warranty_modification_reason', values.reason);
            frm.save();
          },
          'Renew Warranty'
        );
      });
    }

    frm.add_custom_button('View Lab Data', () => {
      frappe.set_route('lab-dashboard', { instrument: frm.doc.name });
    });

    if (!frm.is_new()) {
      render_timeline(frm);
      frm.add_custom_button('Next Upgrade', () => {
        const upgrade = suggest_next_upgrade(frm.doc);
        frappe.set_route('/repair-hub/upgrade', {
          instrument: frm.doc.name,
          sku: upgrade.sku,
        });
      });
    }
  },
});

function render_timeline(frm) {
  frappe
    .call('repair_portal.instrument_profile.utils.get_instrument_timeline', {
      name: frm.doc.name,
    })
    .then((r) => {
      const events = r.message || [];
      const html = ['<ul class="timeline list-unstyled">'];
      events.forEach((ev) => {
        html.push(
          `<li class="timeline-item mb-3">` +
            `<span class="badge bg-primary me-2">${frappe.format_date(ev.date)}</span>` +
            (ev.photo ? `<img src="${ev.photo}" class="img-thumbnail me-2" style="height:40px;">` : '') +
            `${ev.description}` +
            (ev.reference_link ? ` <a href="${ev.reference_link}" class="ms-2">View</a>` : '') +
            `</li>`
        );
      });
      html.push('</ul>');
      frm.dashboard.add_section(html.join(''), 'Lifetime Instrument Timeline');
      frm.dashboard.show();
    });
}

function suggest_next_upgrade(doc) {
  const today = frappe.datetime.now_date();
  const creation = doc.creation ? frappe.datetime.str_to_obj(doc.creation) : frappe.datetime.str_to_obj(today);
  const last_service = doc.last_service_date ? frappe.datetime.str_to_obj(doc.last_service_date) : creation;
  const age_years = frappe.datetime.get_year_diff(today, creation);
  const last_years = frappe.datetime.get_year_diff(today, last_service);

  let suggestion = { sku: 'BARREL', desc: 'Barrel upgrade' };
  if (age_years >= 5 || last_years >= 5) {
    suggestion = { sku: 'PADSET', desc: 'Full pad set' };
  }
  return suggestion;
}
