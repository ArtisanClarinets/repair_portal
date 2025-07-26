// File Header Template
// Relative Path: repair_portal/intake/doctype/clarinet_intake/clarinet_intake_list.js
// Last Updated: 2025-07-25
// Version: v1.0
// Purpose: Color-codes workflow states in ListView for maximum clarity
// Dependencies: Frappe v15 ListView, Clarinet Intake Workflow

frappe.listview_settings['Clarinet Intake'] = {
    get_indicator: function (doc) {
        switch (doc.workflow_state) {
            case "Received":
                return ["Received", "blue", "workflow_state,=,Received"];
            case "In Progress":
                return ["In Progress", "orange", "workflow_state,=,In Progress"];
            case "Inspection":
                return ["Inspection", "purple", "workflow_state,=,Inspection"];
            case "Awaiting Customer Approval":
                return ["Awaiting Customer Approval", "yellow", "workflow_state,=,Awaiting Customer Approval"];
            case "Repair":
                return ["Repair", "cyan", "workflow_state,=,Repair"];
            case "Awaiting Payment":
                return ["Awaiting Payment", "pink", "workflow_state,=,Awaiting Payment"];
            case "Repair Complete":
                return ["Repair Complete", "green", "workflow_state,=,Repair Complete"];
            case "Returned to Customer":
                return ["Returned to Customer", "gray", "workflow_state,=,Returned to Customer"];
            case "Rejected":
                return ["Rejected", "red", "workflow_state,=,Rejected"];
            default:
                return [__(doc.workflow_state || "Unknown"), "darkgrey"];
        }
    }
};
frappe.listview_settings['Clarinet Intake'] = {
    get_indicator: function (doc) {
        switch (doc.fieldname.intake_type) {
            case "Repair":
                return ["Repair", "yellow", "intake_type,=,Repair"];
            case "Maintenance":
                return ["Maintenance", "blue", "intake_type,=,Maintenance"];
            case "New Inventory":
                return ["New Inventory", "green", "intake_type,=,New Inventory"];
        }
    }
};
frappe.listview_settings['Clarinet Intake'].onload = function (listview) {
    // Add custom button to refresh the list
    listview.page.add_action_item(__("Refresh List"), function () {
        listview.refresh();
        frappe.show_alert({
            message: __("List refreshed successfully"),
            indicator: "green"
        });
        // Reset workflow_state filter to default if present
        (frappe.listview_settings['Clarinet Intake'].filters || []).forEach(filter => {
            if (filter.fieldname === "workflow_state") {
                listview.set_filter_value(filter.fieldname, filter.default);
            }
        });
    });

    // Add custom button to reset filters
    listview.page.add_action_item(__("Reset Filters"), function () {
        listview.clear_filters();
        frappe.show_alert({
            message: __("Filters reset successfully"),
            indicator: "green"
        });
        listview.refresh();
    });

    // Add custom button for search
    listview.page.add_action_item(__("Search"), function () {
        frappe.prompt({
            fieldname: 'search_term',
            fieldtype: 'Data',
            label: __('Search Term'),
            reqd: 1,
            placeholder: __('Enter search term')
        }, function (values) {
            listview.search(values.search_term);
        }, __('Search Clarinet Intakes'), __('Search'));
    });

    // Add custom button to create a new Clarinet Intake entry
    listview.page.add_action_item(__("New Clarinet Intake"), function () {
        frappe.new_doc("Clarinet Intake");
    });
};

// Add custom filters to the list view
frappe.listview_settings['Clarinet Intake'].filters = [
    {
        fieldname: "workflow_state",
        label: __("Workflow State"),
        fieldtype: "Select",
        options: [
            { "value": "Received", "label": __("Received") },
            { "value": "In Progress", "label": __("In Progress") },
            { "value": "Inspection", "label": __("Inspection") },
            { "value": "Awaiting Customer Approval", "label": __("Awaiting Customer Approval") },
            { "value": "Repair", "label": __("Repair") },
            { "value": "Awaiting Payment", "label": __("Awaiting Payment") },
            { "value": "Repair Complete", "label": __("Repair Complete") },
            { "value": "Returned to Customer", "label": __("Returned to Customer") },
            { "value": "Rejected", "label": __("Rejected") }
        ],
        default: "In Progress"
    }
];
