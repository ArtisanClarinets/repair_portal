// Path: repair_logging/www/thread_view.js
// Client portal widget logic for message threads

frappe.ready(() => {
	const job = frappe.utils.get_url_arg("job");
	frappe.call({
		method: "repair_portal.repair_logging.api.get_thread",
		args: { job_reference: job },
		callback(r) {
			document.getElementById("thread-box").innerHTML =
				r.message.map(m => `<p><strong>${m.sender}:</strong> ${m.message}</p>`).join("");
		}
	});
});

function postMessage() {
	const job = frappe.utils.get_url_arg("job");
	const message = document.getElementById("new_message").value;
	frappe.call({
		method: "repair_portal.repair_logging.api.post_message",
		args: { job_reference: job, message: message },
		callback() { window.location.reload(); }
	});
}