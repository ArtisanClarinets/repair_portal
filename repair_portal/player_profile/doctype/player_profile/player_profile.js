// Path: repair_portal/player_profile/doctype/player_profile/player_profile.js
// Date: 2025-10-02
// Version: 3.0.0
// Description: Fortune-500 client-side controller for Player Profile with real-time validation,
//              dynamic UI, workflow integration, CRM actions, and secure API calls.
// Dependencies: frappe.ui, frappe.call, frappe.model.workflow

frappe.ui.form.on('Player Profile', {
  // === FORM LIFECYCLE ===
  
  onload(frm) {
    // Initialize dynamic field visibility
    frm.trigger('player_level');
    
    // Set up query filters for linked fields
    frm.set_query('customer', () => ({
      filters: { disabled: 0 }
    }));
  },

  refresh(frm) {
    // Status badge and summary headline
    if (frm.doc.profile_status) {
      frm.dashboard.clear_headline();
      frm.dashboard.set_headline(__('Profile Status: {0}', [frm.doc.profile_status]));
    }

    // Add workflow/action buttons based on status
    frm.trigger('add_workflow_buttons');
    
    // Add CRM action buttons
    frm.trigger('add_crm_buttons');
    
    // Add insight buttons
    frm.trigger('add_insight_buttons');
    
    // Display CRM metrics
    frm.trigger('display_metrics');
    
    // Add API action buttons
    frm.trigger('add_api_buttons');
  },

  // === WORKFLOW BUTTONS ===
  
  add_workflow_buttons(frm) {
    if (frm.doc.profile_status === 'Draft') {
      frm.add_custom_button(__('Activate'), () => {
        frappe.xcall('frappe.model.workflow.apply_workflow', {
          doc: frm.doc,
          action: 'Activate'
        }).then(() => {
          frappe.show_alert({ message: __('Profile activated'), indicator: 'green' });
          frm.reload_doc();
        }).catch(err => {
          frappe.msgprint(__('Failed to activate profile: {0}', [err.message]));
        });
      }, __('Actions'));
    }
    
    if (frm.doc.profile_status === 'Active') {
      frm.add_custom_button(__('Archive'), () => {
        frappe.confirm(
          __('Are you sure you want to archive this player profile?'),
          () => {
            frappe.xcall('frappe.model.workflow.apply_workflow', {
              doc: frm.doc,
              action: 'Archive'
            }).then(() => {
              frappe.show_alert({ message: __('Profile archived'), indicator: 'orange' });
              frm.reload_doc();
            }).catch(err => {
              frappe.msgprint(__('Failed to archive profile: {0}', [err.message]));
            });
          }
        );
      }, __('Actions'));
    }
    
    if (frm.doc.profile_status === 'Archived') {
      frm.add_custom_button(__('Restore'), () => {
        frappe.xcall('frappe.model.workflow.apply_workflow', {
          doc: frm.doc,
          action: 'Restore'
        }).then(() => {
          frappe.show_alert({ message: __('Profile restored'), indicator: 'green' });
          frm.reload_doc();
        }).catch(err => {
          frappe.msgprint(__('Failed to restore profile: {0}', [err.message]));
        });
      }, __('Actions'));
    }
  },

  // === CRM BUTTONS ===
  
  add_crm_buttons(frm) {
    if (!frm.is_new() && frm.doc.primary_email) {
      frm.add_custom_button(__('Email Player'), () => {
        frappe.new_doc('Communication', {
          recipients: frm.doc.primary_email,
          subject: __('Message for {0}', [frm.doc.preferred_name || frm.doc.player_name])
        });
      }, __('CRM'));
      
      frm.add_custom_button(__('Call Player'), () => {
        if (frm.doc.primary_phone) {
          frappe.new_doc('Communication', {
            communication_type: 'Phone',
            phone_no: frm.doc.primary_phone,
            subject: __('Call with {0}', [frm.doc.player_name])
          });
        } else {
          frappe.msgprint(__('No phone number on file'));
        }
      }, __('CRM'));
      
      frm.add_custom_button(__('Schedule Follow-up'), () => {
        frappe.new_doc('ToDo', {
          description: __('Follow up with {0}', [frm.doc.player_name]),
          reference_type: 'Player Profile',
          reference_name: frm.doc.name
        });
      }, __('CRM'));
    }
  },

  // === INSIGHT BUTTONS ===
  
  add_insight_buttons(frm) {
    if (!frm.is_new()) {
      frm.add_custom_button(__('Show Owned Instruments'), () => {
        frappe.route_options = { owner_player: frm.doc.name };
        frappe.set_route('List', 'Instrument Profile');
      }, __('Insights'));
      
      frm.add_custom_button(__('Show Liked Instruments'), () => {
        frappe.route_options = { player_likes: frm.doc.name };
        frappe.set_route('List', 'Instrument Profile');
      }, __('Insights'));
      
      frm.add_custom_button(__('View Service History'), () => {
        frm.trigger('load_service_history');
      }, __('Insights'));
    }
  },

  // === API ACTION BUTTONS ===
  
  add_api_buttons(frm) {
    if (!frm.is_new()) {
      frm.add_custom_button(__('Get Equipment Recommendations'), () => {
        frappe.call({
          method: 'get_equipment_recommendations',
          doc: frm.doc,
          callback: (r) => {
            if (r.message) {
              frm.trigger('display_recommendations', r.message);
            }
          },
          error: (err) => {
            frappe.msgprint(__('Failed to load recommendations: {0}', [err.message]));
          }
        });
      }, __('Equipment'));
    }
  },

  // === METRICS DISPLAY ===
  
  display_metrics(frm) {
    if (!frm.is_new()) {
      // Customer Lifetime Value
      if (frm.doc.customer_lifetime_value) {
        frm.dashboard.add_comment(
          __('Customer Lifetime Value: <b>{0}</b>', [
            frappe.format(frm.doc.customer_lifetime_value, { fieldtype: 'Currency' })
          ])
        );
      }
      
      // Last visit date
      if (frm.doc.last_visit_date) {
        frm.dashboard.add_comment(
          __('Last Visit: {0}', [frappe.format(frm.doc.last_visit_date, { fieldtype: 'Date' })])
        );
      }
      
      // Profile creation date
      if (frm.doc.profile_creation_date) {
        const days = frappe.datetime.get_day_diff(frappe.datetime.nowdate(), frm.doc.profile_creation_date);
        frm.dashboard.add_comment(
          __('Profile Age: {0} days', [Math.abs(days)])
        );
      }
    }
  },

  // === FIELD VALIDATION ===
  
  primary_email(frm) {
    if (frm.doc.primary_email) {
      // Real-time email format validation
      const email_pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
      if (!email_pattern.test(frm.doc.primary_email)) {
        frappe.msgprint({
          title: __('Invalid Email'),
          message: __('Please enter a valid email address'),
          indicator: 'red'
        });
        frm.set_value('primary_email', '');
      } else {
        // Check for duplicate email
        frappe.call({
          method: 'frappe.client.get_list',
          args: {
            doctype: 'Player Profile',
            filters: {
              primary_email: frm.doc.primary_email,
              name: ['!=', frm.doc.name || 'new']
            },
            fields: ['name', 'player_name']
          },
          callback: (r) => {
            if (r.message && r.message.length > 0) {
              frappe.msgprint({
                title: __('Duplicate Email'),
                message: __('Email already exists for player: {0}', [r.message[0].player_name]),
                indicator: 'orange'
              });
            }
          }
        });
      }
    }
  },

  primary_phone(frm) {
    if (frm.doc.primary_phone) {
      // Real-time phone format validation
      const phone_pattern = /^[\d\s\-\+\(\)\.]+$/;
      if (!phone_pattern.test(frm.doc.primary_phone)) {
        frappe.msgprint({
          title: __('Invalid Phone'),
          message: __('Phone number contains invalid characters'),
          indicator: 'red'
        });
      }
    }
  },

  player_level(frm) {
    // Dynamic UI: Show/Hide teacher/affiliation fields for students
    const isStudent = frm.doc.player_level && frm.doc.player_level.startsWith('Student');
    frm.toggle_display('primary_teacher', isStudent);
    frm.toggle_display('affiliation', isStudent);
    
    // Show recommendation hint
    if (isStudent) {
      frm.set_df_property('primary_teacher', 'description', 
        __('Recommended for student profiles'));
    }
  },

  // === MARKETING PREFERENCES ===
  
  newsletter_subscription(frm) {
    if (frm.doc.newsletter_subscription) {
      frappe.show_alert({
        message: __('Player subscribed to newsletter'),
        indicator: 'green'
      });
    } else {
      frappe.show_alert({
        message: __('Player unsubscribed from newsletter'),
        indicator: 'orange'
      });
    }
  },

  targeted_marketing_optin(frm) {
    if (frm.doc.targeted_marketing_optin && frm.doc.targeted_marketing_optin.length) {
      frappe.show_alert({
        message: __('Marketing interests updated: {0}', [frm.doc.targeted_marketing_optin]),
        indicator: 'green'
      });
    }
  },

  communication_preference(frm) {
    if (frm.doc.communication_preference) {
      frappe.show_alert({
        message: __('Preferred contact method: {0}', [frm.doc.communication_preference]),
        indicator: 'blue'
      });
    }
  },

  // === CUSTOM HANDLERS ===
  
  load_service_history(frm) {
    frappe.call({
      method: 'get_service_history',
      doc: frm.doc,
      callback: (r) => {
        if (r.message && r.message.length > 0) {
          // Build HTML table
          let html = '<table class="table table-bordered"><thead><tr>';
          html += '<th>Date</th><th>Type</th><th>Serial</th><th>Description</th></tr></thead><tbody>';
          
          r.message.forEach(item => {
            html += '<tr>';
            html += `<td>${item.date || ''}</td>`;
            html += `<td>${item.doctype || ''}</td>`;
            html += `<td>${item.serial_no || ''}</td>`;
            html += `<td>${item.description || ''}</td>`;
            html += '</tr>';
          });
          
          html += '</tbody></table>';
          
          frappe.msgprint({
            title: __('Service History for {0}', [frm.doc.player_name]),
            message: html,
            wide: true
          });
        } else {
          frappe.msgprint(__('No service history found'));
        }
      },
      error: (err) => {
        frappe.msgprint(__('Failed to load service history: {0}', [err.message]));
      }
    });
  },

  display_recommendations(frm, recommendations) {
    if (!recommendations) return;
    
    let html = '<div class="recommendations-container">';
    
    // Mouthpieces
    if (recommendations.mouthpieces && recommendations.mouthpieces.length > 0) {
      html += '<h5>' + __('Recommended Mouthpieces') + '</h5><ul>';
      recommendations.mouthpieces.forEach(mp => {
        html += `<li>${mp}</li>`;
      });
      html += '</ul>';
    }
    
    // Reeds
    if (recommendations.reeds && recommendations.reeds.length > 0) {
      html += '<h5>' + __('Recommended Reeds') + '</h5><ul>';
      recommendations.reeds.forEach(reed => {
        html += `<li>${reed}</li>`;
      });
      html += '</ul>';
    }
    
    html += '</div>';
    
    frappe.msgprint({
      title: __('Equipment Recommendations for {0}', [frm.doc.player_level]),
      message: html,
      wide: true
    });
  }
});

// === CHILD TABLE: EQUIPMENT PREFERENCES ===

frappe.ui.form.on('Player Equipment Preference', {
  equipment_preferences_add(frm, cdt, cdn) {
    // Set default values for new equipment preference row
    const row = frappe.get_doc(cdt, cdn);
    frappe.model.set_value(cdt, cdn, 'idx', frm.doc.equipment_preferences.length);
  },

  reed_strength(frm, cdt, cdn) {
    // Validate reed strength format
    const row = frappe.get_doc(cdt, cdn);
    if (row.reed_strength) {
      const valid_strengths = ['1.5', '2.0', '2.5', '3.0', '3.5', '4.0', '4.5', '5.0'];
      if (!valid_strengths.includes(row.reed_strength)) {
        frappe.msgprint({
          title: __('Invalid Reed Strength'),
          message: __('Please select a valid reed strength'),
          indicator: 'orange'
        });
      }
    }
  },

  instrument(frm, cdt, cdn) {
    // Validate linked instrument exists
    const row = frappe.get_doc(cdt, cdn);
    if (row.instrument) {
      frappe.call({
        method: 'frappe.client.get',
        args: {
          doctype: 'Instrument Profile',
          name: row.instrument
        },
        callback: (r) => {
          if (!r.message) {
            frappe.msgprint({
              title: __('Invalid Instrument'),
              message: __('Linked instrument not found'),
              indicator: 'red'
            });
            frappe.model.set_value(cdt, cdn, 'instrument', '');
          }
        }
      });
    }
  }
});
