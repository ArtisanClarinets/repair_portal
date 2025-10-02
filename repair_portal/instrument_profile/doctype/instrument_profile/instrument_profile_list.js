// Path: repair_portal/instrument_profile/doctype/instrument_profile/instrument_profile_list.js
// Date: 2025-10-02
// Version: 2.0.0
// Description: Enhanced Instrument Profile ListView with comprehensive filtering, batch operations, real-time status updates, accessibility features, and Fortune-500 level user experience.
// Dependencies: frappe

frappe.listview_settings['Instrument Profile'] = {
    add_fields: ["serial_no", "brand", "model", "profile_status", "customer", "warranty_status", "last_service_date", "is_active"],
    
    get_indicator: function (doc) {
        // Enhanced status indicators with business logic
        if (doc.profile_status === 'Ready') {
            return [__("Ready for Use"), "green", "profile_status,=,Ready"];
        } else if (doc.profile_status === 'In Service') {
            return [__("In Service"), "blue", "profile_status,=,In Service"];
        } else if (doc.profile_status === 'Archived') {
            return [__("Archived"), "grey", "profile_status,=,Archived"];
        } else if (doc.profile_status === 'Needs Repair') {
            return [__("Needs Repair"), "red", "profile_status,=,Needs Repair"];
        } else if (doc.profile_status === 'Under Warranty') {
            return [__("Under Warranty"), "purple", "profile_status,=,Under Warranty"];
        }
        return [__("Draft"), "orange", "profile_status,=,Draft"];
    },

    // Enhanced column configuration with business context
    fields: [
        {
            fieldname: 'serial_no',
            label: __('Serial Number'),
            fieldtype: 'Data',
            in_list_view: 1,
            width: 160
        },
        { 
            fieldname: 'customer', 
            label: __('Customer'), 
            fieldtype: 'Link', 
            options: 'Customer',
            in_list_view: 1,
            width: 140
        },
        { 
            fieldname: 'brand', 
            label: __('Brand'), 
            fieldtype: 'Data', 
            in_list_view: 1,
            width: 100
        },
        { 
            fieldname: 'model', 
            label: __('Model'), 
            fieldtype: 'Data', 
            in_list_view: 1,
            width: 120
        },
        { 
            fieldname: 'profile_status', 
            label: __('Status'), 
            fieldtype: 'Select', 
            in_list_view: 1,
            width: 120
        },
        { 
            fieldname: 'warranty_status', 
            label: __('Warranty'), 
            fieldtype: 'Data', 
            in_list_view: 1,
            width: 100
        }
    ],

    onload: function (listview) {
        try {
            // Enhanced initialization with error handling
            listview.setup_enhanced_features();
            listview.setup_bulk_operations();
            listview.setup_real_time_updates();
            listview.setup_accessibility();
            listview.setup_advanced_filters();
            listview.configure_default_view();
            
        } catch (error) {
            console.error("Error initializing Instrument Profile list:", error);
            frappe.show_alert({
                message: __("Some list features may not work properly"),
                indicator: "orange"
            });
        }
    },

    refresh: function(listview) {
        try {
            listview.refresh_status_counts();
            listview.check_pending_updates();
            
        } catch (error) {
            console.error("Error refreshing list:", error);
        }
    },

    // Custom formatting for list rows
    formatters: {
        serial_no: function(value, field, doc) {
            if (!value) return '<span class="text-muted">No Serial</span>';
            
            // Add QR code icon for easy scanning
            return `<span class="serial-number-cell">
                <i class="fa fa-qrcode text-muted" title="${__('Scannable Serial')}"></i>
                <strong>${value}</strong>
            </span>`;
        },
        
        warranty_status: function(value, field, doc) {
            if (!value) return '<span class="text-muted">Unknown</span>';
            
            const status_colors = {
                'Active': 'green',
                'Expired': 'red',
                'Expiring Soon': 'orange',
                'Not Applicable': 'grey'
            };
            
            const color = status_colors[value] || 'blue';
            return `<span class="label label-${color}">${value}</span>`;
        },
        
        last_service_date: function(value, field, doc) {
            if (!value) return '<span class="text-muted">Never</span>';
            
            const date = moment(value);
            const days_ago = moment().diff(date, 'days');
            
            if (days_ago > 365) {
                return `<span class="text-warning" title="${__('Service overdue')}">${date.format('MMM YYYY')}</span>`;
            } else if (days_ago > 180) {
                return `<span class="text-info">${date.format('MMM YYYY')}</span>`;
            } else {
                return `<span class="text-success">${date.format('MMM DD, YYYY')}</span>`;
            }
        }
    }
};

// Enhanced ListView prototype extensions
$.extend(frappe.views.ListView.prototype, {
    setup_enhanced_features() {
        if (this.doctype !== 'Instrument Profile') return;
        
        // Add enhanced search capabilities
        this.setup_smart_search();
        
        // Add status summary cards
        this.add_status_summary();
        
        // Add export options
        this.setup_export_options();
    },

    setup_smart_search() {
        const original_setup_filter_area = this.setup_filter_area;
        this.setup_filter_area = function() {
            original_setup_filter_area.call(this);
            
            // Add quick search shortcuts
            this.page.add_inner_button(__('Quick Filters'), () => {
                this.show_quick_filters();
            });
        };
    },

    show_quick_filters() {
        const dialog = new frappe.ui.Dialog({
            title: __('Quick Filters'),
            fields: [
                {
                    fieldtype: 'Section Break',
                    label: __('Status Filters')
                },
                {
                    fieldname: 'ready_instruments',
                    label: __('Ready for Use'),
                    fieldtype: 'Button',
                    click: () => {
                        this.filter_area.add([[this.doctype, 'profile_status', '=', 'Ready']]);
                        dialog.hide();
                    }
                },
                {
                    fieldname: 'in_service_instruments',
                    label: __('In Service'),
                    fieldtype: 'Button',
                    click: () => {
                        this.filter_area.add([[this.doctype, 'profile_status', '=', 'In Service']]);
                        dialog.hide();
                    }
                },
                {
                    fieldtype: 'Column Break'
                },
                {
                    fieldname: 'warranty_expiring',
                    label: __('Warranty Expiring Soon'),
                    fieldtype: 'Button',
                    click: () => {
                        this.filter_area.add([[this.doctype, 'warranty_status', '=', 'Expiring Soon']]);
                        dialog.hide();
                    }
                },
                {
                    fieldname: 'needs_service',
                    label: __('Needs Service'),
                    fieldtype: 'Button',
                    click: () => {
                        const cutoff_date = moment().subtract(6, 'months').format('YYYY-MM-DD');
                        this.filter_area.add([[this.doctype, 'last_service_date', '<', cutoff_date]]);
                        dialog.hide();
                    }
                }
            ]
        });
        
        dialog.show();
    },

    add_status_summary() {
        if (this.$status_summary) return;
        
        this.$status_summary = $(`
            <div class="status-summary-cards row" style="margin: 15px 0;">
                <div class="col-sm-3">
                    <div class="status-card ready-card">
                        <div class="status-count">-</div>
                        <div class="status-label">${__('Ready')}</div>
                    </div>
                </div>
                <div class="col-sm-3">
                    <div class="status-card service-card">
                        <div class="status-count">-</div>
                        <div class="status-label">${__('In Service')}</div>
                    </div>
                </div>
                <div class="col-sm-3">
                    <div class="status-card warranty-card">
                        <div class="status-count">-</div>
                        <div class="status-label">${__('Under Warranty')}</div>
                    </div>
                </div>
                <div class="col-sm-3">
                    <div class="status-card repair-card">
                        <div class="status-count">-</div>
                        <div class="status-label">${__('Needs Repair')}</div>
                    </div>
                </div>
            </div>
        `);
        
        this.$frappe_list.prepend(this.$status_summary);
        this.load_status_counts();
    },

    load_status_counts() {
        frappe.call({
            method: "repair_portal.instrument_profile.api.get_profile_status_counts",
            callback: (r) => {
                if (r.message) {
                    this.update_status_cards(r.message);
                }
            }
        });
    },

    update_status_cards(counts) {
        if (!this.$status_summary) return;
        
        this.$status_summary.find('.ready-card .status-count').text(counts.ready || 0);
        this.$status_summary.find('.service-card .status-count').text(counts.in_service || 0);
        this.$status_summary.find('.warranty-card .status-count').text(counts.under_warranty || 0);
        this.$status_summary.find('.repair-card .status-count').text(counts.needs_repair || 0);
        
        // Add click handlers for filtering
        this.$status_summary.find('.ready-card').off('click').on('click', () => {
            this.filter_area.add([[this.doctype, 'profile_status', '=', 'Ready']]);
        });
        
        this.$status_summary.find('.service-card').off('click').on('click', () => {
            this.filter_area.add([[this.doctype, 'profile_status', '=', 'In Service']]);
        });
        
        this.$status_summary.find('.warranty-card').off('click').on('click', () => {
            this.filter_area.add([[this.doctype, 'warranty_status', '=', 'Active']]);
        });
        
        this.$status_summary.find('.repair-card').off('click').on('click', () => {
            this.filter_area.add([[this.doctype, 'profile_status', '=', 'Needs Repair']]);
        });
    },

    setup_bulk_operations() {
        if (this.doctype !== 'Instrument Profile') return;
        
        // Add bulk operation buttons
        this.page.add_actions_menu_item(__('Bulk Update Status'), () => {
            this.show_bulk_status_update();
        });
        
        this.page.add_actions_menu_item(__('Export Selected'), () => {
            this.export_selected_profiles();
        });
        
        this.page.add_actions_menu_item(__('Generate QR Codes'), () => {
            this.generate_qr_codes();
        });
    },

    show_bulk_status_update() {
        if (!this.get_checked_items().length) {
            frappe.msgprint(__('Please select instruments to update'));
            return;
        }
        
        const dialog = new frappe.ui.Dialog({
            title: __('Bulk Status Update'),
            fields: [
                {
                    fieldname: 'new_status',
                    label: __('New Status'),
                    fieldtype: 'Select',
                    options: 'Ready\nIn Service\nNeeds Repair\nArchived',
                    reqd: 1
                },
                {
                    fieldname: 'update_reason',
                    label: __('Reason for Update'),
                    fieldtype: 'Text',
                    reqd: 1
                }
            ],
            primary_action_label: __('Update Status'),
            primary_action: (values) => {
                this.execute_bulk_status_update(values);
                dialog.hide();
            }
        });
        
        dialog.show();
    },

    execute_bulk_status_update(values) {
        const selected_items = this.get_checked_items();
        
        frappe.call({
            method: "repair_portal.instrument_profile.api.bulk_update_status",
            args: {
                profile_names: selected_items,
                new_status: values.new_status,
                reason: values.update_reason
            },
            callback: (r) => {
                if (r.message) {
                    frappe.show_alert({
                        message: __('Status updated for {0} instruments', [r.message.updated_count]),
                        indicator: "green"
                    });
                    this.refresh();
                }
            }
        });
    },

    export_selected_profiles() {
        const selected_items = this.get_checked_items();
        
        if (!selected_items.length) {
            frappe.msgprint(__('Please select instruments to export'));
            return;
        }
        
        frappe.call({
            method: "repair_portal.instrument_profile.api.export_profiles",
            args: {
                profile_names: selected_items,
                format: 'excel'
            },
            callback: (r) => {
                if (r.message && r.message.file_url) {
                    window.open(r.message.file_url);
                }
            }
        });
    },

    generate_qr_codes() {
        const selected_items = this.get_checked_items();
        
        if (!selected_items.length) {
            frappe.msgprint(__('Please select instruments to generate QR codes'));
            return;
        }
        
        frappe.call({
            method: "repair_portal.instrument_profile.api.generate_qr_codes",
            args: {
                profile_names: selected_items
            },
            callback: (r) => {
                if (r.message && r.message.pdf_url) {
                    window.open(r.message.pdf_url);
                }
            }
        });
    },

    setup_real_time_updates() {
        if (this.doctype !== 'Instrument Profile') return;
        
        // Set up real-time status monitoring
        this.status_monitor = setInterval(() => {
            this.check_pending_updates();
        }, 30000); // Check every 30 seconds
    },

    check_pending_updates() {
        if (!this.is_visible()) return;
        
        frappe.call({
            method: "repair_portal.instrument_profile.api.check_pending_updates",
            args: {
                last_update: this.last_update_time || ''
            },
            callback: (r) => {
                if (r.message && r.message.has_updates) {
                    this.show_update_notification();
                }
            }
        });
    },

    show_update_notification() {
        if (this.$update_notification) return;
        
        this.$update_notification = $(`
            <div class="alert alert-info update-notification">
                <i class="fa fa-refresh"></i>
                ${__('New updates available')}
                <button class="btn btn-xs btn-primary pull-right" onclick="cur_list.refresh()">
                    ${__('Refresh')}
                </button>
            </div>
        `);
        
        this.$frappe_list.prepend(this.$update_notification);
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (this.$update_notification) {
                this.$update_notification.fadeOut(() => {
                    this.$update_notification.remove();
                    this.$update_notification = null;
                });
            }
        }, 10000);
    },

    setup_accessibility() {
        if (this.doctype !== 'Instrument Profile') return;
        
        // Add ARIA labels and keyboard navigation
        this.$frappe_list.attr('role', 'grid');
        this.$frappe_list.attr('aria-label', __('Instrument Profile List'));
        
        // Add keyboard shortcuts
        $(document).on('keydown', (e) => {
            if (!this.is_visible()) return;
            
            if (e.ctrlKey && e.key === 'f') {
                e.preventDefault();
                this.page.fields_dict.text_search.$input.focus();
            }
            
            if (e.ctrlKey && e.key === 'r') {
                e.preventDefault();
                this.refresh();
            }
        });
    },

    setup_advanced_filters() {
        if (this.doctype !== 'Instrument Profile') return;
        
        // Add advanced filter options
        this.page.add_inner_button(__('Advanced Filters'), () => {
            this.show_advanced_filters();
        });
    },

    show_advanced_filters() {
        const dialog = new frappe.ui.Dialog({
            title: __('Advanced Filters'),
            size: 'large',
            fields: [
                {
                    fieldtype: 'Section Break',
                    label: __('Service History')
                },
                {
                    fieldname: 'service_date_range',
                    label: __('Last Service Date Range'),
                    fieldtype: 'DateRange'
                },
                {
                    fieldname: 'service_overdue',
                    label: __('Service Overdue (days)'),
                    fieldtype: 'Int',
                    description: __('Show instruments not serviced for X days')
                },
                {
                    fieldtype: 'Section Break',
                    label: __('Warranty Status')
                },
                {
                    fieldname: 'warranty_expiring_days',
                    label: __('Warranty Expiring Within (days)'),
                    fieldtype: 'Int'
                },
                {
                    fieldtype: 'Section Break',
                    label: __('Customer Information')
                },
                {
                    fieldname: 'customer_type',
                    label: __('Customer Type'),
                    fieldtype: 'Link',
                    options: 'Customer Type'
                }
            ],
            primary_action_label: __('Apply Filters'),
            primary_action: (values) => {
                this.apply_advanced_filters(values);
                dialog.hide();
            }
        });
        
        dialog.show();
    },

    apply_advanced_filters(values) {
        // Apply advanced filters based on user selection
        const filters = [];
        
        if (values.service_overdue) {
            const cutoff_date = moment().subtract(values.service_overdue, 'days').format('YYYY-MM-DD');
            filters.push([this.doctype, 'last_service_date', '<', cutoff_date]);
        }
        
        if (values.warranty_expiring_days) {
            const cutoff_date = moment().add(values.warranty_expiring_days, 'days').format('YYYY-MM-DD');
            filters.push([this.doctype, 'warranty_expiry_date', '<', cutoff_date]);
        }
        
        if (values.customer_type) {
            filters.push(['Customer', 'customer_type', '=', values.customer_type]);
        }
        
        filters.forEach(filter => {
            this.filter_area.add([filter]);
        });
    },

    configure_default_view() {
        // Set default sort and pagination
        this.sort_by = 'serial_no';
        this.sort_order = 'asc';
        this.page_length = 50;
        
        // Set default filters for active instruments
        this.filter_area.add([[this.doctype, 'is_active', '=', 1]]);
    },

    refresh_status_counts() {
        this.load_status_counts();
        this.last_update_time = moment().format();
    },

    is_visible() {
        return this.$frappe_list && this.$frappe_list.is(':visible');
    }
});

// Add custom CSS for enhanced styling
frappe.ready(() => {
    if (!$('#instrument-profile-list-styles').length) {
        $('head').append(`
            <style id="instrument-profile-list-styles">
                .status-summary-cards .status-card {
                    background: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    padding: 15px;
                    text-align: center;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }
                
                .status-summary-cards .status-card:hover {
                    background: #e9ecef;
                    transform: translateY(-2px);
                }
                
                .status-summary-cards .status-count {
                    font-size: 24px;
                    font-weight: bold;
                    color: #495057;
                }
                
                .status-summary-cards .status-label {
                    font-size: 12px;
                    color: #6c757d;
                    margin-top: 5px;
                }
                
                .serial-number-cell {
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                }
                
                .update-notification {
                    margin: 10px 0;
                    border-radius: 4px;
                }
                
                .instrument-profile-row.warranty-expiring {
                    background-color: #fff3cd !important;
                }
                
                .instrument-profile-row.service-overdue {
                    background-color: #f8d7da !important;
                }
            </style>
        `);
    }
});
