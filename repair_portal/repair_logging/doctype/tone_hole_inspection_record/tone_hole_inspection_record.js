// Path: repair_portal/repair_logging/doctype/tone_hole_inspection_record/tone_hole_inspection_record.js
// Date: 2025-01-14
// Version: 2.0.0
// Description: Production-ready client script for tone hole inspection with comprehensive validation and UI enhancements
// Dependencies: frappe

frappe.ui.form.on('Tone Hole Inspection Record', {
    
    refresh(frm) {
        // Set up form styling and buttons
        frm.page.set_title(__('Tone Hole Inspection Record'));
        
        // Add custom buttons for inspection workflow
        if (frm.doc.docstatus === 0) {
            frm.add_custom_button(__('Load Standard Inspection Template'), 
                () => frm.events.load_inspection_template(frm));
        }
        
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('View Inspection History'), 
                () => frm.events.view_inspection_history(frm));
            frm.add_custom_button(__('Calculate Condition Trends'), 
                () => frm.events.calculate_condition_trends(frm));
        }
        
        // Set up field styling
        frm.events.setup_field_styling(frm);
    },
    
    onload(frm) {
        // Set up field queries and filters
        frm.events.setup_field_queries(frm);
        
        // Set default values
        if (frm.is_new()) {
            frm.set_value('inspection_timestamp', frappe.datetime.now_datetime());
            frm.set_value('inspected_by', frappe.session.user);
        }
    },
    
    validate(frm) {
        // Client-side validation before save
        frm.events.validate_required_fields(frm);
        frm.events.validate_measurement_ranges(frm);
        frm.events.validate_condition_consistency(frm);
    },
    
    tone_hole_number(frm) {
        // Validate tone hole number format and uniqueness
        if (frm.doc.tone_hole_number) {
            frm.events.validate_hole_number_format(frm);
        }
    },
    
    visual_status(frm) {
        // Auto-suggest condition rating based on visual status
        if (frm.doc.visual_status && !frm.doc.condition_rating) {
            frm.events.suggest_condition_rating(frm);
        }
        
        // Show/hide photo requirement
        frm.events.check_photo_requirement(frm);
    },
    
    condition_rating(frm) {
        // Validate rating and update calculated score
        if (frm.doc.condition_rating) {
            frm.events.validate_condition_rating(frm);
            frm.events.calculate_overall_condition(frm);
        }
    },
    
    hole_diameter(frm) {
        // Validate diameter measurement
        if (frm.doc.hole_diameter) {
            frm.events.validate_diameter_measurement(frm);
        }
    },
    
    // Custom event handlers
    setup_field_queries(frm) {
        // Set up queries for linked fields
        frm.set_query('inspected_by', () => {
            return {
                filters: {
                    enabled: 1,
                    name: ['in', frappe.user_roles.filter(role => 
                        ['Technician', 'Quality Inspector', 'Repair Specialist', 'System Manager'].includes(role)
                    )]
                }
            };
        });
    },
    
    setup_field_styling(frm) {
        // Apply conditional styling based on field values
        if (frm.doc.visual_status) {
            const status_color_map = {
                'Excellent': 'green',
                'Good': 'blue', 
                'Fair': 'orange',
                'Poor': 'red',
                'Damaged': 'red',
                'Cracked': 'red',
                'Chipped': 'orange'
            };
            
            const color = status_color_map[frm.doc.visual_status];
            if (color) {
                frm.get_field('visual_status').$wrapper.find('.control-input').css('border-left', `4px solid ${color}`);
            }
        }
        
        // Highlight condition rating based on value
        if (frm.doc.condition_rating) {
            const rating = parseFloat(frm.doc.condition_rating);
            let color = 'green';
            if (rating <= 3) color = 'red';
            else if (rating <= 5) color = 'orange';
            else if (rating <= 7) color = 'blue';
            
            frm.get_field('condition_rating').$wrapper.find('.control-input').css('border-left', `4px solid ${color}`);
        }
    },
    
    validate_required_fields(frm) {
        const required_fields = [
            'tone_hole_number',
            'visual_status',
            'inspected_by'
        ];
        
        let missing_fields = [];
        required_fields.forEach(field => {
            if (!frm.doc[field]) {
                missing_fields.push(frappe.meta.get_label(frm.doctype, field));
            }
        });
        
        if (missing_fields.length > 0) {
            frappe.throw(__('Missing required fields: {0}', [missing_fields.join(', ')]));
        }
        
        // Require photo for poor conditions
        if (['Poor', 'Damaged', 'Cracked', 'Chipped'].includes(frm.doc.visual_status) && !frm.doc.photo) {
            frappe.throw(__('Photo documentation is required for damaged or poor condition tone holes'));
        }
    },
    
    validate_measurement_ranges(frm) {
        // Validate diameter
        if (frm.doc.hole_diameter) {
            const diameter = parseFloat(frm.doc.hole_diameter);
            if (diameter <= 0) {
                frappe.throw(__('Hole diameter must be positive'));
            }
            if (diameter > 20) {
                frappe.throw(__('Hole diameter {0}mm seems unreasonably large', [diameter]));
            }
            if (diameter < 2) {
                frappe.msgprint(__('Warning: Hole diameter {0}mm is unusually small', [diameter]));
            }
        }
        
        // Validate chimney height
        if (frm.doc.chimney_height) {
            const height = parseFloat(frm.doc.chimney_height);
            if (height < 0) {
                frappe.throw(__('Chimney height cannot be negative'));
            }
            if (height > 15) {
                frappe.msgprint(__('Warning: Chimney height {0}mm is unusually tall', [height]));
            }
        }
        
        // Validate wall thickness
        if (frm.doc.wall_thickness) {
            const thickness = parseFloat(frm.doc.wall_thickness);
            if (thickness <= 0) {
                frappe.throw(__('Wall thickness must be positive'));
            }
            if (thickness > 5) {
                frappe.msgprint(__('Warning: Wall thickness {0}mm is unusually thick', [thickness]));
            }
        }
    },
    
    validate_condition_consistency(frm) {
        // Check consistency between visual status and condition rating
        if (frm.doc.visual_status && frm.doc.condition_rating) {
            const rating = parseFloat(frm.doc.condition_rating);
            
            if (['Excellent', 'Good'].includes(frm.doc.visual_status) && rating < 6) {
                frappe.msgprint(__('Warning: Good visual status but low condition rating ({0})', [rating]));
            } else if (['Damaged', 'Cracked'].includes(frm.doc.visual_status) && rating > 4) {
                frappe.msgprint(__('Warning: Damaged visual status but high condition rating ({0})', [rating]));
            }
        }
    },
    
    validate_hole_number_format(frm) {
        const hole_num = String(frm.doc.tone_hole_number).trim();
        
        if (!hole_num) {
            frappe.throw(__('Tone hole number cannot be empty'));
        }
        
        // Check for valid hole numbering
        if (/^\d+$/.test(hole_num)) {
            const hole_int = parseInt(hole_num);
            if (hole_int < 1 || hole_int > 24) {
                frappe.msgprint(__('Warning: Tone hole number {0} is outside typical range (1-24)', [hole_int]));
            }
        } else if (!['THUMB', 'REGISTER', 'SPEAKER', 'VENT'].includes(hole_num.toUpperCase())) {
            frappe.msgprint(__('Warning: Non-standard tone hole identifier: {0}', [hole_num]));
        }
    },
    
    suggest_condition_rating(frm) {
        const visual_ratings = {
            'Excellent': 10,
            'Good': 8,
            'Fair': 6,
            'Poor': 4,
            'Damaged': 2,
            'Cracked': 2,
            'Chipped': 3,
            'Worn': 5,
            'Debris Present': 6,
            'Needs Cleaning': 7
        };
        
        const suggested_rating = visual_ratings[frm.doc.visual_status];
        if (suggested_rating) {
            frm.set_value('condition_rating', suggested_rating);
        }
    },
    
    validate_condition_rating(frm) {
        const rating = parseFloat(frm.doc.condition_rating);
        if (rating < 1 || rating > 10) {
            frappe.throw(__('Condition rating must be between 1 and 10'));
        }
    },
    
    validate_diameter_measurement(frm) {
        const diameter = parseFloat(frm.doc.hole_diameter);
        
        // Check against standard tone hole sizes for instrument type
        if (frm.doc.parent && frm.doc.parenttype === 'Instrument Inspection') {
            // Could validate against instrument-specific standards
            // This would require instrument type information from parent
        }
    },
    
    calculate_overall_condition(frm) {
        // This would typically aggregate multiple measurements
        // For now, just ensure the calculated score is set
        if (frm.doc.condition_rating && !frm.doc.calculated_condition_score) {
            frm.set_value('calculated_condition_score', frm.doc.condition_rating);
        }
    },
    
    check_photo_requirement(frm) {
        const photo_required_statuses = ['Poor', 'Damaged', 'Cracked', 'Chipped'];
        const requires_photo = photo_required_statuses.includes(frm.doc.visual_status);
        
        if (requires_photo) {
            frm.get_field('photo').set_description(__('Photo is required for {0} condition', [frm.doc.visual_status]));
            frm.get_field('photo').$wrapper.addClass('has-error');
        } else {
            frm.get_field('photo').set_description('');
            frm.get_field('photo').$wrapper.removeClass('has-error');
        }
    },
    
    load_inspection_template(frm) {
        frappe.prompt([
            {
                fieldtype: 'Select',
                label: __('Instrument Type'),
                fieldname: 'instrument_type',
                options: ['Bb Clarinet', 'A Clarinet', 'Eb Clarinet', 'Bass Clarinet', 'Custom'],
                reqd: 1
            }
        ], (values) => {
            frappe.call({
                method: 'repair_portal.repair_logging.doctype.tone_hole_inspection_record.tone_hole_inspection_record.get_inspection_template',
                args: {
                    instrument_type: values.instrument_type
                },
                callback: (r) => {
                    if (r.message) {
                        // Load template data into form
                        Object.keys(r.message).forEach(field => {
                            if (frm.doc[field] === undefined || frm.doc[field] === null) {
                                frm.set_value(field, r.message[field]);
                            }
                        });
                        frappe.show_alert(__('Inspection template loaded'));
                    }
                }
            });
        }, __('Select Inspection Template'));
    },
    
    view_inspection_history(frm) {
        if (!frm.doc.parent || !frm.doc.tone_hole_number) {
            frappe.msgprint(__('Inspection history requires parent document and tone hole number'));
            return;
        }
        
        frappe.call({
            method: 'repair_portal.repair_logging.doctype.tone_hole_inspection_record.tone_hole_inspection_record.get_inspection_history',
            args: {
                instrument_profile: frm.doc.parent,
                tone_hole_number: frm.doc.tone_hole_number
            },
            callback: (r) => {
                if (r.message && r.message.length > 0) {
                    const history_html = frm.events.format_inspection_history(frm, r.message);
                    frappe.msgprint(history_html, __('Inspection History - Tone Hole {0}', [frm.doc.tone_hole_number]));
                } else {
                    frappe.msgprint(__('No inspection history found for this tone hole'));
                }
            }
        });
    },
    
    calculate_condition_trends(frm) {
        frappe.call({
            method: 'repair_portal.repair_logging.doctype.tone_hole_inspection_record.tone_hole_inspection_record.calculate_condition_trends',
            args: {
                instrument_profile: frm.doc.parent,
                tone_hole_number: frm.doc.tone_hole_number
            },
            callback: (r) => {
                if (r.message) {
                    const trend_data = r.message;
                    let trend_message = __('Condition Trend: {0}', [trend_data.trend]);
                    
                    if (trend_data.current_rating && trend_data.previous_rating) {
                        trend_message += `<br>Current: ${trend_data.current_rating}, Previous: ${trend_data.previous_rating}`;
                    }
                    
                    frappe.msgprint(trend_message, __('Condition Trend Analysis'));
                }
            }
        });
    },
    
    format_inspection_history(frm, history) {
        let html = '<table class="table table-bordered"><thead><tr>';
        html += '<th>Date</th><th>Visual Status</th><th>Condition Rating</th><th>Seal Quality</th><th>Inspector</th>';
        html += '</tr></thead><tbody>';
        
        history.forEach(record => {
            html += '<tr>';
            html += `<td>${frappe.datetime.str_to_user(record.inspection_timestamp)}</td>`;
            html += `<td>${record.visual_status || ''}</td>`;
            html += `<td>${record.condition_rating || ''}</td>`;
            html += `<td>${record.seal_quality || ''}</td>`;
            html += `<td>${record.inspected_by || ''}</td>`;
            html += '</tr>';
        });
        
        html += '</tbody></table>';
        return html;
    }
});
