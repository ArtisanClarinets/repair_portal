// File Header Template
// Relative Path: repair_portal/player_profile/doctype/player_profile/player_profile.js
// Last Updated: 2025-07-20
// Version: v2.0
// Purpose: Fortune-500 production JS for Player Profile: dynamic UI, validation, CRM triggers, field logic, and actionable insights.

frappe.ui.form.on('Player Profile', {
  refresh(frm) {
    // Status badge and summary headline
    if (frm.doc.profile_status) {
      frm.dashboard.clear_headline();
      frm.dashboard.set_headline(__('Profile Status: {0}', [frm.doc.profile_status]));
    }

    // Add workflow/action buttons based on status
    if (frm.doc.profile_status === 'Draft') {
      frm.add_custom_button(__('Activate'), () => {
        frappe.xcall('frappe.model.workflow.apply_workflow', {
          doc: frm.doc,
          action: 'Activate'
        }).then(() => frm.reload_doc());
      }, __('Actions'));
    }
    if (frm.doc.profile_status === 'Active') {
      frm.add_custom_button(__('Archive'), () => {
        frappe.xcall('frappe.model.workflow.apply_workflow', {
          doc: frm.doc,
          action: 'Archive'
        }).then(() => frm.reload_doc());
      }, __('Actions'));
    }
    if (frm.doc.profile_status === 'Archived') {
      frm.add_custom_button(__('Restore'), () => {
        frappe.xcall('frappe.model.workflow.apply_workflow', {
          doc: frm.doc,
          action: 'Restore'
        }).then(() => frm.reload_doc());
      }, __('Actions'));
    }

    // Personalized CRM quick actions
    if (frm.is_new() === false && frm.doc.primary_email) {
      frm.add_custom_button(__('Email Player'), () => {
        frappe.new_doc('Communication', {
          recipients: frm.doc.primary_email,
          subject: __('Personal message to {0}', [frm.doc.preferred_name || frm.doc.player_name])
        });
      }, __('CRM'));
    }

    // Quick access to instrument ownership and likes
    frm.add_custom_button(__('Show Owned Instruments'), () => {
      frappe.route_options = { owner_player: frm.doc.name };
      frappe.set_route('List', 'Instrument Profile');
    }, __('Insights'));
    frm.add_custom_button(__('Show Liked Instruments'), () => {
      frappe.route_options = { player_likes: frm.doc.name };
      frappe.set_route('List', 'Instrument Profile');
    }, __('Insights'));

    // CRM insights: Show CLV and last visit
    frm.dashboard.add_comment(__('Customer Lifetime Value: <b>{0}</b>', [frappe.format(frm.doc.customer_lifetime_value, {fieldtype: 'Currency'})]));
    if (frm.doc.last_visit_date) {
      frm.dashboard.add_comment(__('Last Visit: {0}', [frm.doc.last_visit_date]));
    }
  },

  player_level(frm) {
    // Dynamic UI: Show/Hide teacher/affiliation fields for students
    const isStudent = frm.doc.player_level && frm.doc.player_level.startsWith('Student');
    frm.toggle_display('primary_teacher', isStudent);
    frm.toggle_display('affiliation', isStudent);
  },

  // Live CRM opt-in/opt-out UI
  newsletter_subscription(frm) {
    if (frm.doc.newsletter_subscription) {
      frappe.show_alert(__('Player subscribed to newsletter'));
    }
  },

  targeted_marketing_optin(frm) {
    if (frm.doc.targeted_marketing_optin && frm.doc.targeted_marketing_optin.length) {
      frappe.show_alert(__('Player marketing interests updated'));
    }
  },

  // Communication preference: Alert on change
  communication_preference(frm) {
    if (frm.doc.communication_preference) {
      frappe.show_alert(__('Preferred contact: {0}', [frm.doc.communication_preference]));
    }
  },

  // On load: default dynamic field setup
  onload(frm) {
    frm.trigger('player_level');
  }
});
