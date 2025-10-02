// Path: repair_portal/repair_logging/custom/customer_interaction_timeline.js
// Date: 2025-01-14
// Version: 2.0.0
// Description: Production-ready customer interaction timeline with security validation and performance optimization
// Dependencies: frappe

frappe.ui.form.on("Customer", {
    refresh(frm) {
        // Only render timeline for existing customers with proper permissions
        if (!frm.doc.__islocal && frm.doc.name && frappe.model.can_read("Customer")) {
            frm.events.render_customer_timeline(frm);
        }
    },
    
    render_customer_timeline(frm) {
        // Security check - verify user has permission to view customer interactions
        if (!frappe.user.has_role(['System Manager', 'Technician', 'Customer Service'])) {
            return;
        }
        
        const container = $(frm.fields_dict.related_interactions?.wrapper);
        if (!container.length) return;
        
        // Create secure filter interface
        container.parent().find('.interaction-filter-bar').remove();
        container.parent().prepend(`
            <div class="interaction-filter-bar" style="margin-bottom: 15px; padding: 10px; background: #f8f9fa; border-radius: 5px;">
                <div class="row">
                    <div class="col-md-4">
                        <input type="text" 
                               class="form-control interaction-search" 
                               placeholder="${__('Search interactions...')}"
                               maxlength="100">
                    </div>
                    <div class="col-md-3">
                        <select class="form-control interaction-type-filter">
                            <option value="">${__('All Types')}</option>
                            <option value="Intake">${__('Intake')}</option>
                            <option value="Inspection">${__('Inspection')}</option>
                            <option value="Service Plan">${__('Service Plan')}</option>
                            <option value="Repair">${__('Repair')}</option>
                            <option value="QA Check">${__('QA Check')}</option>
                            <option value="Upgrade Request">${__('Upgrade Request')}</option>
                            <option value="Warranty">${__('Warranty')}</option>
                        </select>
                    </div>
                    <div class="col-md-3">
                        <select class="form-control interaction-status-filter">
                            <option value="">${__('All Statuses')}</option>
                            <option value="Open">${__('Open')}</option>
                            <option value="In Progress">${__('In Progress')}</option>
                            <option value="Completed">${__('Completed')}</option>
                            <option value="Cancelled">${__('Cancelled')}</option>
                        </select>
                    </div>
                    <div class="col-md-2">
                        <button class="btn btn-primary btn-sm refresh-timeline" type="button">
                            ${__('Refresh')}
                        </button>
                    </div>
                </div>
                <div class="row mt-2">
                    <div class="col-md-12">
                        <small class="text-muted">
                            ${__('Showing interactions from repair logging and related modules')}
                        </small>
                    </div>
                </div>
            </div>
        `);
        
        const $search = container.parent().find('.interaction-search');
        const $typeFilter = container.parent().find('.interaction-type-filter');
        const $statusFilter = container.parent().find('.interaction-status-filter');
        const $refreshBtn = container.parent().find('.refresh-timeline');
        
        // Debounced search to improve performance
        let searchTimeout;
        function debouncedUpdate() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                frm.events.update_timeline(frm, $search.val(), $typeFilter.val(), $statusFilter.val());
            }, 300);
        }
        
        // Event handlers with security validation
        $search.on('input', debouncedUpdate);
        $typeFilter.on('change', debouncedUpdate);
        $statusFilter.on('change', debouncedUpdate);
        $refreshBtn.on('click', () => {
            frm.events.fetch_fresh_interactions(frm);
        });
        
        // Initial load
        frm.events.fetch_fresh_interactions(frm);
    },
    
    update_timeline(frm, searchVal = '', typeVal = '', statusVal = '') {
        // Clear existing timeline
        if (frm.timeline) {
            frm.timeline.clear();
        }
        
        const interactions = frm.doc.related_interactions || [];
        let displayCount = 0;
        const maxDisplay = 50; // Limit for performance
        
        interactions.forEach((log) => {
            if (displayCount >= maxDisplay) return;
            
            // Security check - sanitize all data
            const sanitizedLog = frm.events.sanitize_interaction_data(log);
            
            // Apply filters
            const text = (sanitizedLog.notes || '').toLowerCase();
            const matchType = !typeVal || sanitizedLog.interaction_type === typeVal;
            const matchStatus = !statusVal || sanitizedLog.status === statusVal;
            const matchSearch = !searchVal || text.includes(searchVal.toLowerCase());
            
            if (matchType && matchStatus && matchSearch) {
                frm.events.add_timeline_entry(frm, sanitizedLog);
                displayCount++;
            }
        });
        
        // Show count information
        const totalCount = interactions.length;
        const filteredCount = displayCount;
        
        if (filteredCount < totalCount) {
            frm.dashboard.add_indicator(__('Showing {0} of {1} interactions', [filteredCount, totalCount]), 'blue');
        }
    },
    
    sanitize_interaction_data(log) {
        // Sanitize all string fields to prevent XSS
        const sanitized = {};
        
        Object.keys(log).forEach(key => {
            const value = log[key];
            if (typeof value === 'string') {
                // Remove any potential script tags and escape HTML
                sanitized[key] = $('<div>').text(value).html();
            } else {
                sanitized[key] = value;
            }
        });
        
        return sanitized;
    },
    
    add_timeline_entry(frm, log) {
        if (!frm.timeline) return;
        
        // Determine icon and color based on interaction type
        const type_styles = {
            'Intake': { icon: 'fa fa-sign-in', color: 'blue' },
            'Inspection': { icon: 'fa fa-search', color: 'orange' },
            'Service Plan': { icon: 'fa fa-calendar', color: 'green' },
            'Repair': { icon: 'fa fa-wrench', color: 'purple' },
            'QA Check': { icon: 'fa fa-check-circle', color: 'teal' },
            'Upgrade Request': { icon: 'fa fa-level-up', color: 'indigo' },
            'Warranty': { icon: 'fa fa-shield', color: 'red' }
        };
        
        const style = type_styles[log.interaction_type] || { icon: 'fa fa-circle', color: 'gray' };
        
        frm.timeline.append({
            doctype: log.reference_doctype || 'Unknown',
            docname: log.reference_name || '',
            title: __('{0} - {1}', [log.interaction_type || 'Interaction', log.instrument_tracker || '']),
            description: log.notes || __('No details available'),
            date: log.date || frappe.datetime.now_date(),
            timeline_label: log.status || 'Unknown',
            icon: style.icon,
            color: style.color,
            creation: log.creation || frappe.datetime.now_datetime()
        });
    },
    
    fetch_fresh_interactions(frm) {
        // Fetch fresh interaction data with proper permission checking
        if (!frm.doc.name) return;
        
        frappe.call({
            method: 'repair_portal.api.customer.get_customer_interaction_timeline',
            args: {
                customer: frm.doc.name,
                limit: 100
            },
            callback: (r) => {
                if (r.message) {
                    frm.doc.related_interactions = r.message;
                    frm.events.update_timeline(frm);
                    frappe.show_alert(__('Timeline refreshed'));
                } else {
                    frappe.show_alert(__('No interactions found'), 'orange');
                }
            },
            error: (r) => {
                frappe.show_alert(__('Failed to load interactions: {0}', [r.message || 'Unknown error']), 'red');
            }
        });
    }
});
