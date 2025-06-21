frappe.ready(function () {
  const jobName = frappe.utils.get_url_arg("job");
  const threadBox = document.getElementById("thread-content");
  const messageBox = document.getElementById("message-box");
  const sendButton = document.getElementById("send-button");

  function loadThread() {
    frappe.call({
      method: "repair_portal.repair_logging.doctype.customer_interaction_thread.customer_interaction_thread.get_thread_entries",
      args: { job_name: jobName },
      callback: function (r) {
        if (r.message) {
          threadBox.innerHTML = r.message.map(entry => `
            <div class="message ${entry.direction}">
              <strong>${entry.sender}</strong>: ${entry.message}
              <small class="text-muted">${entry.creation}</small>
            </div>
          `).join("");
        }
      }
    });
  }

  sendButton.onclick = function () {
    frappe.call({
      method: "repair_portal.repair_logging.doctype.customer_interaction_thread.customer_interaction_thread.add_portal_message",
      args: {
        job_name: jobName,
        message: messageBox.value
      },
      callback: function (r) {
        messageBox.value = "";
        loadThread();
      }
    });
  };

  loadThread();
});