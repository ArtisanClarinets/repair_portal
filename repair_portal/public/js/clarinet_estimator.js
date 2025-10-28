const __ = frappe._;
const form = document.getElementById("estimator-form");
const instrumentSelect = document.getElementById("instrument-family");
const hotspots = Array.from(document.querySelectorAll(".hotspot"));
const expediteInput = document.getElementById("expedite");
const photosInput = document.getElementById("photos");
const lineItemsBody = document.getElementById("line-items-body");
const totalDisplay = document.getElementById("total-display");
const etaDisplay = document.getElementById("eta-display");
const statusEl = document.getElementById("form-status");

const state = {
  selected: new Set(),
  rules: {},
  hasExistingPhotos: false,
};

const currency = (frappe.boot && frappe.boot.sysdefaults && frappe.boot.sysdefaults.currency) || "USD";
const currencyFormatter = new Intl.NumberFormat(undefined, { style: "currency", currency });

function formatCurrency(amount) {
  if (!amount) {
    return currencyFormatter.format(0);
  }
  return currencyFormatter.format(amount);
}

async function loadBootstrap() {
  state.selected.clear();
  hotspots.forEach((btn) => btn.setAttribute("aria-pressed", "false"));
  statusEl.textContent = "";
  try {
    const response = await frappe.call({
      method: "repair_portal.api.estimator.get_bootstrap",
      args: { instrument_family: instrumentSelect.value },
    });
    state.rules = (response && response.message && response.message.regions) || {};
    state.hasExistingPhotos = false;
    renderPreview();
  } catch (error) {
    console.error(error);
    statusEl.textContent = __("Unable to load pricing rules. Contact support.");
  }
}

function toggleRegion(button) {
  const region = button.dataset.region;
  if (!region) return;
  if (state.selected.has(region)) {
    state.selected.delete(region);
    button.setAttribute("aria-pressed", "false");
  } else {
    state.selected.add(region);
    button.setAttribute("aria-pressed", "true");
  }
  renderPreview();
}

function renderPreview() {
  const rows = [];
  let total = 0;
  let etaDays = 0;
  const expedite = expediteInput.checked;

  state.selected.forEach((region) => {
    const regionData = state.rules[region];
    if (!regionData) return;
    const label = regionData.label || region;
    (regionData.components || []).forEach((component) => {
      const partQuantity = component.part_quantity || 0;
      const partRate = component.part_rate || 0;
      const partAmount = partQuantity && partRate ? partQuantity * partRate : 0;
      if (partAmount) {
        rows.push({
          region: label,
          description: component.task_description,
          role: __("Part"),
          rate: partRate,
          qty: partQuantity,
          amount: partAmount,
        });
        total += partAmount;
      }

      let laborRate = component.labor_rate || 0;
      if (laborRate) {
        laborRate *= component.family_multiplier || 1;
        if (expedite) {
          laborRate *= component.rush_multiplier || 1;
        }
      }
      const laborHours = component.labor_hours || 0;
      const laborAmount = laborRate && laborHours ? laborRate * laborHours : 0;
      if (laborAmount) {
        rows.push({
          region: label,
          description: `${component.task_description} ${__("Labor")}`,
          role: __("Labor"),
          rate: laborRate,
          qty: laborHours,
          amount: laborAmount,
        });
        total += laborAmount;
      }
      etaDays = Math.max(etaDays, component.eta_days || 0);
    });
  });

  if (expedite && etaDays) {
    etaDays = Math.max(2, etaDays - 2);
  }

  lineItemsBody.innerHTML = "";
  if (!rows.length) {
    const empty = document.createElement("tr");
    empty.classList.add("empty-state");
    const td = document.createElement("td");
    td.colSpan = 6;
    td.textContent = __("Select a region to populate the estimate.");
    empty.appendChild(td);
    lineItemsBody.appendChild(empty);
    totalDisplay.textContent = "—";
    etaDisplay.textContent = "—";
    return;
  }

  const fragment = document.createDocumentFragment();
  rows.forEach((row) => {
    const tr = document.createElement("tr");
    const regionCell = document.createElement("td");
    regionCell.textContent = row.region;
    const descCell = document.createElement("td");
    descCell.textContent = row.description;
    const roleCell = document.createElement("td");
    roleCell.textContent = row.role;
    const rateCell = document.createElement("td");
    rateCell.textContent = formatCurrency(row.rate || 0);
    const qtyCell = document.createElement("td");
    qtyCell.textContent = (row.qty || 0).toFixed(2);
    const amountCell = document.createElement("td");
    amountCell.textContent = formatCurrency(row.amount || 0);
    tr.append(regionCell, descCell, roleCell, rateCell, qtyCell, amountCell);
    fragment.appendChild(tr);
  });
  lineItemsBody.appendChild(fragment);
  totalDisplay.textContent = formatCurrency(total);
  etaDisplay.textContent = etaDays ? `${etaDays}` : "—";
}

async function submitForm(event) {
  event.preventDefault();
  statusEl.textContent = "";

  if (!form.reportValidity()) {
    statusEl.textContent = __("Please fill out all required fields.");
    return;
  }
  if (!state.selected.size) {
    statusEl.textContent = __("Select at least one region before submitting.");
    return;
  }
  if (!state.hasExistingPhotos && photosInput.files.length === 0) {
    statusEl.textContent = __("Upload at least one inspection photo.");
    photosInput.focus();
    return;
  }

  const formData = new FormData(form);
  formData.append("selections", JSON.stringify(Array.from(state.selected)));

  try {
    statusEl.textContent = __("Generating estimate...");
    const response = await fetch("/api/method/repair_portal.api.estimator.submit", {
      method: "POST",
      headers: { "X-Frappe-CSRF-Token": frappe.csrf_token },
      body: formData,
    });
    const payload = await response.json();
    if (!response.ok || payload.exc) {
      throw new Error(payload.exc || payload._server_messages || response.statusText);
    }
    const message = payload.message || payload;
    applyServerResult(message);
    state.hasExistingPhotos = true;
    photosInput.value = "";
    statusEl.textContent = `${__("Estimate saved")}: ${message.estimate}`;
  } catch (error) {
    console.error(error);
    const detail = error && error.message ? ` ${error.message}` : "";
    statusEl.textContent = `${__("Failed to generate estimate.")}${detail}`;
  }
}

function applyServerResult(message) {
  if (!message) return;
  if (Array.isArray(message.line_items) && message.line_items.length) {
    lineItemsBody.innerHTML = "";
    const fragment = document.createDocumentFragment();
    message.line_items.forEach((item) => {
      const tr = document.createElement("tr");
      const regionCell = document.createElement("td");
      regionCell.textContent = (state.rules[item.region_id] && state.rules[item.region_id].label) || item.region_id;
      const descCell = document.createElement("td");
      descCell.textContent = item.description;
      const roleCell = document.createElement("td");
      roleCell.textContent = item.line_role;
      const rateCell = document.createElement("td");
      rateCell.textContent = formatCurrency(item.rate || 0);
      const qtyCell = document.createElement("td");
      const qtyValue = item.line_role === "Labor" ? item.hours : item.quantity;
      qtyCell.textContent = (qtyValue || 0).toFixed(2);
      const amountCell = document.createElement("td");
      amountCell.textContent = formatCurrency(item.amount || 0);
      tr.append(regionCell, descCell, roleCell, rateCell, qtyCell, amountCell);
      fragment.appendChild(tr);
    });
    lineItemsBody.appendChild(fragment);
  }
  if (message.total !== undefined) {
    totalDisplay.textContent = formatCurrency(message.total);
  }
  if (message.eta_days !== undefined) {
    etaDisplay.textContent = message.eta_days ? `${message.eta_days}` : "—";
  }
}

instrumentSelect.addEventListener("change", loadBootstrap);
expediteInput.addEventListener("change", renderPreview);
hotspots.forEach((button) => {
  button.addEventListener("click", () => toggleRegion(button));
});
form.addEventListener("submit", submitForm);

loadBootstrap();
