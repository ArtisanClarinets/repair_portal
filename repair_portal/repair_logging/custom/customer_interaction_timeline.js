frappe.ui.form.on("Customer", {
	refresh(frm) {
		if (!frm.doc.__islocal && frm.doc.related_interactions) {
			render_customer_timeline(frm);
		}
	},
});

function render_customer_timeline(frm) {
	const container = $(frm.fields_dict.related_interactions.wrapper)
		.parent()
		.prepend(`
    <div class="interaction-filter-bar" style="margin-bottom: 10px;">
      <input type="text" class="interaction-search" placeholder="Search interactions..." style="margin-right: 8px; width: 200px;">
      <select class="interaction-type-filter">
        <option value="">All Types</option>
        <option>Intake</option>
        <option>Inspection</option>
        <option>Service Plan</option>
        <option>Repair</option>
        <option>QA Check</option>
        <option>Upgrade Request</option>
      </select>
    </div>
  `);

	const $search = container.find(".interaction-search");
	const $typeFilter = container.find(".interaction-type-filter");

	function updateTimeline() {
		const searchVal = $search.val().toLowerCase();
		const typeVal = $typeFilter.val();
		frm.timeline.clear();
		(frm.doc.related_interactions || []).forEach((log) => {
			const text = (log.notes || "").toLowerCase();
			const matchType = !typeVal || log.interaction_type === typeVal;
			const matchSearch = !searchVal || text.includes(searchVal);
			if (matchType && matchSearch) {
				frm.timeline.append({
					doctype: log.reference_doctype,
					docname: log.reference_name,
					title: `${log.interaction_type}`,
					description: `${log.notes || ""}`,
					date: log.date,
					timeline_label: `${log.instrument_tracker}`,
				});
			}
		});
	}

	$search.on("input", updateTimeline);
	$typeFilter.on("change", updateTimeline);
	updateTimeline();
}
