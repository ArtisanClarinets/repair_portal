// Path: repair_portal/repair_logging/custom/item_interaction_timeline.js
// Date: 2025-01-14
// Version: 2.0.0
// Description: Production-ready item interaction timeline with security validation and performance optimization
// Dependencies: frappe

frappe.ui.form.on("Item", {
    refresh(frm) {
        // Only render timeline for existing items with proper permissions
        if (!frm.doc.__islocal && frm.doc.name && frappe.model.can_read("Item")) {
            frm.events.render_item_timeline(frm);
        }
    },
    
    render_item_timeline(frm) {
        // Security check - verify user has permission to view item interactions
        if (!frappe.user.has_role(['System Manager', 'Technician', 'Inventory Manager', 'Quality Inspector'])) {
            return;
        }
        
        const container = $(frm.fields_dict.related_interactions?.wrapper);
        if (!container.length) return;
        
        // Create secure filter interface with enhanced styling
        container.parent().find('.interaction-filter-bar').remove();
        container.parent().prepend(`
            <div class="interaction-filter-bar" style="margin-bottom: 15px; padding: 10px; background: #f8f9fa; border-radius: 5px;">
                <div class="row">
                    <div class="col-md-4">
                        <input type="text" 
                               class="form-control interaction-search" 
                               placeholder="${__('Search interactions...')}"
                               maxlength="100"
                               autocomplete="off">
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
                            <option value="Usage Log">${__('Usage Log')}</option>
                            <option value="Material Use">${__('Material Use')}</option>
                            <option value="Tool Usage">${__('Tool Usage')}</option>
                        </select>
                    </div>
                    <div class="col-md-3">
                        <select class="form-control interaction-status-filter">
                            <option value="">${__('All Statuses')}</option>
                            <option value="Draft">${__('Draft')}</option>
                            <option value="Open">${__('Open')}</option>
                            <option value="In Progress">${__('In Progress')}</option>
                            <option value="Completed">${__('Completed')}</option>
                            <option value="Cancelled">${__('Cancelled')}</option>
                            <option value="Verified">${__('Verified')}</option>
                        </select>
                    </div>
                    <div class="col-md-2">
                        <button class="btn btn-primary btn-sm refresh-timeline" type="button" title="${__('Refresh Timeline')}">
                            <i class="fa fa-refresh"></i> ${__('Refresh')}
                        </button>
                    </div>
                </div>
                <div class="row mt-2">
                    <div class="col-md-6">
                        <small class="text-muted">
                            ${__('Showing item-related interactions from repair logging')}
                        </small>
                    </div>
                    <div class="col-md-6 text-right">
                        <span class="interaction-count badge badge-info"></span>
                    </div>
                </div>
            </div>
        `);
        
        const $search = container.parent().find('.interaction-search');
        const $typeFilter = container.parent().find('.interaction-type-filter');
        const $statusFilter = container.parent().find('.interaction-status-filter');
        const $refreshBtn = container.parent().find('.refresh-timeline');
        const $countBadge = container.parent().find('.interaction-count');
        
        // Performance optimized debounced search
        let searchTimeout;
        function debouncedUpdate() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                frm.events.update_timeline(frm, $search.val(), $typeFilter.val(), $statusFilter.val(), $countBadge);
            }, 300);
        }
        
        // Event handlers with accessibility support
        $search.on('input', debouncedUpdate);
        $search.on('keypress', (e) => {
            if (e.which === 13) { // Enter key
                e.preventDefault();
                debouncedUpdate();
            }
        });
        
        $typeFilter.on('change', debouncedUpdate);
        $statusFilter.on('change', debouncedUpdate);
        
        $refreshBtn.on('click', () => {
            $refreshBtn.prop('disabled', true);
            frm.events.fetch_fresh_interactions(frm, () => {
                $refreshBtn.prop('disabled', false);
            });
        });
        
        // Keyboard navigation
        $search.on('keydown', (e) => {
            if (e.which === 27) { // Escape key
                $search.val('').trigger('input');
            }
        });
        
        // Initial load
        frm.events.fetch_fresh_interactions(frm);
    },
    
    update_timeline(frm, searchVal = '', typeVal = '', statusVal = '', $countBadge = null) {
        // Clear existing timeline
        if (frm.timeline) {
            frm.timeline.clear();
        }
        
        const interactions = frm.doc.related_interactions || [];
        let displayCount = 0;
        let filteredCount = 0;
        const maxDisplay = 75; // Higher limit for item interactions
        
        interactions.forEach((log) => {
            // Security check - sanitize all data
            const sanitizedLog = frm.events.sanitize_interaction_data(log);
            
            // Apply filters with comprehensive matching
            const text = (sanitizedLog.notes || '').toLowerCase() + 
                        (sanitizedLog.interaction_type || '').toLowerCase() +
                        (sanitizedLog.instrument_tracker || '').toLowerCase();
            const matchType = !typeVal || sanitizedLog.interaction_type === typeVal;
            const matchStatus = !statusVal || sanitizedLog.status === statusVal;
            const matchSearch = !searchVal || text.includes(searchVal.toLowerCase());
            
            if (matchType && matchStatus && matchSearch) {
                filteredCount++;
                if (displayCount < maxDisplay) {
                    frm.events.add_timeline_entry(frm, sanitizedLog);
                    displayCount++;
                }
            }
        });
        
        // Update count badge with performance indicator
        if ($countBadge && $countBadge.length) {
            const totalCount = interactions.length;
            let countText = `${filteredCount} of ${totalCount}`;
            if (displayCount < filteredCount) {
                countText += ` (showing ${displayCount})`;
            }
            $countBadge.text(countText);
            
            // Performance warning for large datasets
            if (totalCount > 200) {
                $countBadge.addClass('badge-warning').attr('title', 'Large dataset - consider filtering');
            } else {
                $countBadge.removeClass('badge-warning').removeAttr('title');
            }
        }
        
        // Show performance feedback
        if (displayCount === maxDisplay && filteredCount > maxDisplay) {
            frappe.show_alert(__('Showing first {0} of {1} matching interactions. Please refine filters.', [maxDisplay, filteredCount]), 'orange');
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
            } else if (typeof value === 'number' || typeof value === 'boolean') {
                sanitized[key] = value;
            } else if (value === null || value === undefined) {
                sanitized[key] = '';
            } else {
                // For complex objects, convert to safe string
                sanitized[key] = String(value);
            }
        });
        
        return sanitized;
    },
    
    add_timeline_entry(frm, log) {
        if (!frm.timeline) return;
        
        // Enhanced type styling with more interaction types
        const type_styles = {
            'Intake': { icon: 'fa fa-sign-in', color: 'blue', priority: 5 },
            'Inspection': { icon: 'fa fa-search', color: 'orange', priority: 4 },
            'Service Plan': { icon: 'fa fa-calendar', color: 'green', priority: 3 },
            'Repair': { icon: 'fa fa-wrench', color: 'purple', priority: 4 },
            'QA Check': { icon: 'fa fa-check-circle', color: 'teal', priority: 3 },
            'Upgrade Request': { icon: 'fa fa-level-up', color: 'indigo', priority: 2 },
            'Usage Log': { icon: 'fa fa-clock-o', color: 'cyan', priority: 1 },
            'Material Use': { icon: 'fa fa-cube', color: 'brown', priority: 2 },
            'Tool Usage': { icon: 'fa fa-tools', color: 'dark', priority: 2 },
            'Warranty': { icon: 'fa fa-shield', color: 'red', priority: 4 }
        };
        
        const style = type_styles[log.interaction_type] || { icon: 'fa fa-circle', color: 'gray', priority: 0 };
        
        // Enhanced title with status indicator
        const statusIndicator = log.status ? ` [${log.status}]` : '';
        const title = __('{0}{1} - {2}', [
            log.interaction_type || 'Interaction',
            statusIndicator,
            log.instrument_tracker || log.reference_name || 'Unknown'
        ]);
        
        // Enhanced description with metadata
        let description = log.notes || __('No details available');
        if (log.technician) {
            description = `<strong>${__('Technician')}:</strong> ${log.technician}<br>${description}`;
        }
        if (log.duration) {
            description += `<br><small class="text-muted">${__('Duration')}: ${log.duration}</small>`;
        }
        
        frm.timeline.append({
            doctype: log.reference_doctype || 'Unknown',
            docname: log.reference_name || '',
            title: title,
            description: description,
            date: log.date || frappe.datetime.now_date(),
            timeline_label: log.interaction_type || 'Unknown',
            icon: style.icon,
            color: style.color,
            creation: log.creation || frappe.datetime.now_datetime(),
            priority: style.priority
        });
    },
    
    fetch_fresh_interactions(frm, callback = null) {
        // Fetch fresh interaction data with proper permission checking
        if (!frm.doc.name) {
            if (callback) callback();
            return;
        }
        
        frappe.call({
            method: 'repair_portal.api.customer.get_item_interaction_timeline',
            args: {
                item_code: frm.doc.name,
                limit: 150
            },
            callback: (r) => {
                if (r.message && Array.isArray(r.message)) {
                    // Sort by priority and date for better display
                    const sortedInteractions = r.message.sort((a, b) => {
                        const typeA = type_styles[a.interaction_type] || { priority: 0 };
                        const typeB = type_styles[b.interaction_type] || { priority: 0 };
                        
                        // Primary sort by priority
                        if (typeA.priority !== typeB.priority) {
                            return typeB.priority - typeA.priority;
                        }
                        
                        // Secondary sort by date (newest first)
                        const dateA = new Date(a.creation || a.date || 0);
                        const dateB = new Date(b.creation || b.date || 0);
                        return dateB - dateA;
                    });
                    
                    frm.doc.related_interactions = sortedInteractions;
                    frm.events.update_timeline(frm);
                    frappe.show_alert(__('Timeline refreshed with {0} interactions', [sortedInteractions.length]));
                } else {
                    frm.doc.related_interactions = [];
                    frm.events.update_timeline(frm);
                    frappe.show_alert(__('No interactions found'), 'orange');
                }
                
                if (callback) callback();
            },
            error: (r) => {
                frappe.show_alert(__('Failed to load interactions: {0}', [r.message || 'Unknown error']), 'red');
                if (callback) callback();
            }
        });
    }
});
