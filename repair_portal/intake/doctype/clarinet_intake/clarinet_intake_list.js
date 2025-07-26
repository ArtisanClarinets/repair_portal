// File Header Template
// Relative Path: repair_portal/intake/doctype/clarinet_intake/clarinet_intake_list.js
// Last Updated: 2025-07-25
// Version: v2.0
// Purpose: Color-codes workflow states in ListView for maximum clarity
// Dependencies: Frappe v15 ListView, Intake Workflow

frappe.listview_settings['Clarinet Intake'] = {
    get_indicator: function(doc) {
        switch (doc.intake_status) {
            case "Pending":
                return [__("Pending"), "gray", "intake_status,=,Pending"];
            case "Received":
                return [__("Received"), "blue", "intake_status,=,Received"];
            case "Inspection":
                return [__("Inspection"), "orange", "intake_status,=,Inspection"];
            case "Setup":
                return [__("Setup"), "purple", "intake_status,=,Setup"];
            case "Repair":
                return [__("Repair"), "cyan", "intake_status,=,Repair"];
            case "Awaiting Customer Approval":
                return [__("Awaiting Customer Approval"), "yellow", "intake_status,=,Awaiting Customer Approval"];
            case "Awaiting Payment":
                return [__("Awaiting Payment"), "pink", "intake_status,=,Awaiting Payment"];
            case "In Transit":
                return [__("In Transit"), "blue", "intake_status,=,In Transit"];
            case "Repair Complete":
                return [__("Repair Complete"), "green", "intake_status,=,Repair Complete"];
            case "Returned to Customer":
                return [__("Returned to Customer"), "darkgrey", "intake_status,=,Returned to Customer"];
            default:
                return [__(doc.intake_status || "Unknown"), "red"];
        }
    },
    filters: [
        {
            fieldname: "intake_status",
            label: __("Status"),
            fieldtype: "Select",
            options: [
                { value: "Pending", label: __("Pending") },
                { value: "Received", label: __("Received") },
                { value: "Inspection", label: __("Inspection") },
                { value: "Setup", label: __("Setup") },
                { value: "Repair", label: __("Repair") },
                { value: "Awaiting Customer Approval", label: __("Awaiting Customer Approval") },
                { value: "Awaiting Payment", label: __("Awaiting Payment") },
                { value: "In Transit", label: __("In Transit") },
                { value: "Repair Complete", label: __("Repair Complete") },
                { value: "Returned to Customer", label: __("Returned to Customer") }
            ],
            default: "Pending"
        }
    ],
    onload: function(listview) {
        listview.page.add_action_item(__("Refresh List"), function() {
            listview.refresh();
            frappe.show_alert({ message: __("List refreshed successfully"), indicator: "green" });
        });
        listview.page.add_action_item(__("Reset Filters"), function() {
            listview.clear_filters();
            frappe.show_alert({ message: __("Filters reset successfully"), indicator: "green" });
            listview.refresh();
        });
        listview.page.add_action_item(__("Search"), function() {
            frappe.prompt({
                fieldname: 'search_term',
                fieldtype: 'Data',
                label: __('Search Term'),
                reqd: 1,
                placeholder: __('Enter search term')
            }, function(values) {
                listview.search(values.search_term);
            }, __('Search Clarinet Intakes'), __('Search'));
        });
        listview.page.add_action_item(__("New Clarinet Intake"), function() {
            frappe.new_doc("Clarinet Intake");
        });
    }
};
