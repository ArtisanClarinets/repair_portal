frappe.ui.form.on('Player Profile', {
  onload(frm) {
    frm.trigger('player_level');
    frm.set_query('customer', () => ({ filters: { disabled: 0 } }));
  },

  refresh(frm) {
    frm.trigger('player_level');

    if (frm.doc.profile_status === 'Archived') {
      frm.disable_form();
      frm.set_df_property('profile_status', 'read_only', 0);
    } else {
      frm.enable_form();
    }

    frm.dashboard.clear_headline();
    if (frm.doc.profile_status) {
      frm.dashboard.set_headline(__('Profile Status: {0}', [frm.doc.profile_status]));
    }

    frm.trigger('render_metrics');
    frm.trigger('render_workflow_buttons');
    frm.trigger('render_crm_actions');
    frm.trigger('render_insight_actions');
  },

  player_level(frm) {
    const isStudent = frm.doc.player_level && frm.doc.player_level.startsWith('Student');
    frm.toggle_display(['primary_teacher', 'affiliation'], !!isStudent);
  },

  primary_email(frm) {
    if (!frm.doc.primary_email) {
      return;
    }
    const pattern = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;
    if (!pattern.test(frm.doc.primary_email)) {
      frappe.msgprint({
        title: __('Invalid Email'),
        message: __('Please provide a valid email address.'),
        indicator: 'red'
      });
      frm.set_value('primary_email', '');
      return;
    }

    frappe.db.count('Player Profile', {
      filters: {
        primary_email: frm.doc.primary_email,
        name: ['!=', frm.doc.name || '']
      }
    }).then(total => {
      if (total > 0) {
        frappe.msgprint({
          title: __('Duplicate Email'),
          message: __('Another Player Profile already uses this email address.'),
          indicator: 'orange'
        });
      }
    });
  },

  primary_phone(frm) {
    if (!frm.doc.primary_phone) {
      return;
    }
    const pattern = /^[0-9+()\-\s]{7,20}$/;
    if (!pattern.test(frm.doc.primary_phone)) {
      frappe.msgprint({
        title: __('Invalid Phone'),
        message: __('Phone number may only contain digits, spaces, parentheses, hyphen, and plus sign.'),
        indicator: 'red'
      });
    }
  },

  render_workflow_buttons(frm) {
    const addAction = (label, action, opts = {}) => {
      frm.add_custom_button(label, () => {
        const perform = () => frappe.xcall('frappe.model.workflow.apply_workflow', {
          doc: frm.doc,
          action
        }).then(() => frm.reload_doc());
        if (opts.confirm_message) {
          frappe.confirm(opts.confirm_message, perform);
        } else {
          perform();
        }
      }, __('Actions'));
    };

    if (frm.doc.profile_status === 'Draft') {
      addAction(__('Activate'), 'Activate');
    }
    if (frm.doc.profile_status === 'Active') {
      addAction(__('Archive'), 'Archive', {
        confirm_message: __('Archive this Player Profile? Owned instruments remain linked but the record becomes read-only.')
      });
    }
    if (frm.doc.profile_status === 'Archived') {
      addAction(__('Restore'), 'Restore');
    }
  },

  render_crm_actions(frm) {
    if (frm.is_new()) {
      return;
    }
    if (frm.doc.primary_email) {
      frm.add_custom_button(__('Email Player'), () => {
        frappe.new_doc('Communication', {
          recipients: frm.doc.primary_email,
          subject: __('Message for {0}', [frm.doc.preferred_name || frm.doc.player_name])
        });
      }, __('CRM'));
    }
    frm.add_custom_button(__('Call Player'), () => {
      if (!frm.doc.primary_phone) {
        frappe.msgprint(__('No phone number on record.'));
        return;
      }
      frappe.new_doc('Communication', {
        communication_type: 'Phone',
        phone_no: frm.doc.primary_phone,
        subject: __('Call with {0}', [frm.doc.player_name])
      });
    }, __('CRM'));
  },

  render_insight_actions(frm) {
    if (frm.is_new()) {
      return;
    }
    frm.add_custom_button(__('Show Owned Instruments'), () => {
      frappe.route_options = { owner_player: frm.doc.name };
      frappe.set_route('List', 'Instrument Profile');
    }, __('Insights'));

    frm.add_custom_button(__('View Service History'), () => {
      frm.trigger('load_service_history');
    }, __('Insights'));
  },

  load_service_history(frm) {
    frappe.xcall(
      'repair_portal.player_profile.doctype.player_profile.player_profile.get_service_history',
      { player_profile: frm.doc.name }
    ).then(rows => {
      if (!rows || rows.length === 0) {
        frappe.msgprint(__('No service history found for this player.'));
        return;
      }
      const safe = rows.map(row => ({
        date: frappe.utils.escape_html(row.date || ''),
        type: frappe.utils.escape_html(row.type || ''),
        reference: frappe.utils.escape_html(row.reference || ''),
        serial_number: frappe.utils.escape_html(row.serial_number || ''),
        description: frappe.utils.escape_html(row.description || '')
      }));
      const header = `
        <table class="table table-bordered table-hover">
          <thead>
            <tr>
              <th>${__('Date')}</th>
              <th>${__('Type')}</th>
              <th>${__('Reference')}</th>
              <th>${__('Serial')}</th>
              <th>${__('Status')}</th>
            </tr>
          </thead>
          <tbody>
      `;
      const body = safe.map(item => `
        <tr>
          <td>${item.date}</td>
          <td>${item.type}</td>
          <td>${item.reference}</td>
          <td>${item.serial_number}</td>
          <td>${item.description}</td>
        </tr>
      `).join('');
      const footer = '</tbody></table>';
      frappe.msgprint({
        title: __('Service History for {0}', [frm.doc.player_name]),
        message: header + body + footer,
        wide: true
      });
    }).catch(err => {
      frappe.msgprint({
        title: __('Unable to load history'),
        message: err.message || err,
        indicator: 'red'
      });
    });
  },

  render_metrics(frm) {
    if (frm.is_new()) {
      return;
    }
    const currency = frappe.utils.format_currency(frm.doc.customer_lifetime_value || 0);
    frm.dashboard.add_comment(__('Customer Lifetime Value: {0}', [currency]));

    if (frm.doc.last_visit_date) {
      frm.dashboard.add_comment(__('Last Visit Date: {0}', [frappe.format(frm.doc.last_visit_date, { fieldtype: 'Date' })]));
    }

    if (frm.doc.profile_creation_date) {
      const ageDays = frappe.datetime.get_day_diff(frappe.datetime.nowdate(), frm.doc.profile_creation_date);
      frm.dashboard.add_comment(__('Profile Age: {0} days', [Math.max(ageDays, 0)]));
    }
  }
});
