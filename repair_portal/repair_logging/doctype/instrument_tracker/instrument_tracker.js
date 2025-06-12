frappe.ui.form.on("Instrument Tracker", {
	refresh: function (frm) {
		if (!frm.doc.__islocal && frm.doc.interaction_logs) {
			render_timeline_with_filter(frm);
			add_export_button(frm);
		}
	},
});

function render_timeline_with_filter(frm) {
	const container = $(frm.fields_dict.interaction_logs.wrapper)
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
		(frm.doc.interaction_logs || []).forEach((log) => {
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
					timeline_label: `${log.reference_doctype}: ${log.reference_name}`,
				});
			}
		});
	}

	$search.on("input", updateTimeline);
	$typeFilter.on("change", updateTimeline);
	updateTimeline();
}

function add_export_button(frm) {
	frm.add_custom_button("Export Log as CSV", () => {
		const rows = [
			[
				"Interaction Type",
				"Reference DocType",
				"Reference Name",
				"Date",
				"Notes",
			],
		];
		(frm.doc.interaction_logs || []).forEach((log) => {
			rows.push([
				log.interaction_type,
				log.reference_doctype,
				log.reference_name,
				log.date,
				log.notes?.replace(/\n/g, " ") || "",
			]);
		});

		const csvContent =
			"data:text/csv;charset=utf-8," +
			rows.map((e) => e.map((v) => '"' + v + '"').join(",")).join("\n");
		const encodedUri = encodeURI(csvContent);
		const link = document.createElement("a");
		link.setAttribute("href", encodedUri);
		link.setAttribute(
			"download",
			`Instrument_Log_${frm.doc.serial_number || "tracker"}.csv`,
		);
		document.body.appendChild(link);
		link.click();
		document.body.removeChild(link);
	});
}
