frappe.ui.form.on('Instrument Inspection', {
    refresh: function(frm) {
        frm.trigger('toggle_fields_by_type');
    },
    inspection_type: function(frm) {
        frm.trigger('toggle_fields_by_type');
    },
    toggle_fields_by_type: function(frm) {
        let type = frm.doc.inspection_type;
        // Hide customer/pricing for New Inventory
        frm.toggle_display(['customer', 'preliminary_estimate'], type !== 'New Inventory');
        // Show manufacturer/model/key/wood for New Inventory
        frm.toggle_display([
            'manufacturer', 'model', 'key', 'wood_type',
            'unboxing_rh', 'unboxing_temperature', 'unboxing_time',
            'hygrometer_photo', 'rested_unopened',
            'acclimatization_controlled_env', 'acclimatization_playing_schedule', 'acclimatization_swabbing',
            'instrument_delivered', 'bore_condition', 'bore_notes'
        ], type === 'New Inventory');
        // Show overall_condition only for non-inventory
        frm.toggle_display('overall_condition', type !== 'New Inventory');
    }
});
