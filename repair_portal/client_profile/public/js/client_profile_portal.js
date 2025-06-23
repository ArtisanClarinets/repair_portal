// Enhances the Client Profile portal view with interactivity
frappe.ready(() => {
  if (frappe.web_form.doctype === "Client Profile") {
    frappe.web_form.after_load = () => {
      console.log("Client Profile Web Form loaded.");
      setupFAB();
      setupDisclosure();
      loadAlerts();
    };

    frappe.web_form.on('preferred_contact_method', (field, value) => {
      frappe.show_alert(`Preferred contact method set to ${value}`);
    });
  }
});

function setupFAB() {
  const fab = document.createElement("button");
  fab.className = "btn btn-primary fab";
  fab.style.position = "fixed";
  fab.style.bottom = "20px";
  fab.style.right = "20px";
  fab.innerText = "+ Add Instrument";
  fab.onclick = () => window.location.href = "/new-instrument";
  document.body.appendChild(fab);
}

function setupDisclosure() {
  document.querySelectorAll(".log-entry").forEach((entry, index) => {
    if (index >= 3) entry.classList.add("d-none");
  });

  const toggle = document.createElement("button");
  toggle.innerText = "Show Full History";
  toggle.className = "btn btn-sm btn-secondary mt-2";
  toggle.onclick = () => {
    document.querySelectorAll(".log-entry.d-none").forEach(el => el.classList.remove("d-none"));
    toggle.remove();
  };
  const logContainer = document.querySelector("#history-container");
  if (logContainer) logContainer.appendChild(toggle);
}

function loadAlerts() {
  frappe.call({
    method: "repair_portal.api.get_pending_alerts",
    callback: function(r) {
      const alerts = r.message || {};
      if (alerts.pending_tasks) {
        const badge = document.getElementById("service-alert");
        if (badge) badge.innerText = `(${alerts.pending_tasks})`;
      }
      if (alerts.expiring_warranties) {
        const badge = document.getElementById("warranty-alert");
        if (badge) badge.innerText = `(${alerts.expiring_warranties})`;
      }
    }
  });
}