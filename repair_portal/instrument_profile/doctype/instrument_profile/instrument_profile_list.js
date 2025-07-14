// relative path: instrument_profile/doctype/instrument_profile/instrument_profile_list.js
// date updated: 2025-07-01
// version: 1.0.1
// Purpose: Customizes Instrument Profile ListView to show Serial Number first.

frappe.listview_settings['Instrument Profile'] = {
    add_fields: ["serial_no", "brand", "model", "profile_status"],
    get_indicator: function (doc) {
        if (doc.profile_status === 'Ready') {
            return [__("Ready"), "green", "profile_status,=,Ready"];
        } else if (doc.profile_status === 'In Service') {
            return [__("In Service"), "blue", "profile_status,=,In Service"];
        } else if (doc.profile_status === 'Archived') {
            return [__("Archived"), "grey", "profile_status,=,Archived"];
        }
        return [__("Draft"), "orange", "profile_status,=,Draft"];
    },
    onload: function (listview) {
        listview.page.fields_dict.sort_by.set_value('serial_no');
    },
    // Prioritize serial_no column in ListView
    fields: [
        {
            fieldname: 'serial_no',
            label: __('Serial Number'),
            fieldtype: 'Data',
            in_list_view: 1,
            width: 180
        },
        { fieldname: 'brand', label: __('Brand'), fieldtype: 'Data', in_list_view: 1 },
        { fieldname: 'model', label: __('Model'), fieldtype: 'Data', in_list_view: 1 },
        { fieldname: 'profile_status', label: __('Status'), fieldtype: 'Select', in_list_view: 1 }
    ]
};
