// File: intake/web_form/customer_sign_off/customer_sign_off.js
// Updated: 2025-06-20
// Version: 1.3
// Purpose: Dynamic terms loader, read-only handling, signature capture

frappe.ready(async function () {
  const form = frappe.web_form;

  // Hide backend fields
  ['ip_address', 'signed_at', 'signature_hash', 'signature_image'].forEach(field => {
    const wrapper = form.fields_dict[field]?.wrapper;
    if (wrapper) wrapper.style.display = 'none';
  });

  // Load dynamic terms
  let terms_html = "<p><strong>Terms not configured.</strong></p>";
  if (form.doc.reference_doctype) {
    await frappe.call({
      method: "frappe.client.get_list",
      args: {
        doctype: "Sign Off Terms",
        filters: { reference_doctype: form.doc.reference_doctype },
        fields: ["html_terms"],
        limit_page_length: 1
      },
      callback: r => {
        if (r.message && r.message.length > 0) {
          terms_html = r.message[0].html_terms;
        }
      }
    });
  }

  const termsDiv = document.createElement('div');
  termsDiv.innerHTML = `
    <div style="margin: 20px 0; padding: 10px; border-left: 4px solid #666;">
      ${terms_html}
    </div>
  `;
  form.wrapper.appendChild(termsDiv);

  // Read-only display (submitted)
  if (form.doc?.__islocal === 0 && form.doc.docstatus === 1) {
    const info = document.createElement('div');
    info.innerHTML = `
      <p><strong>Already Signed</strong></p>
      <ul>
        <li><b>Signed At:</b> ${form.doc.signed_at || '—'}</li>
        <li><b>IP Address:</b> ${form.doc.ip_address || '—'}</li>
        <li><b>Hash:</b> ${form.doc.signature_hash?.slice(0, 8) + '…' || '—'}</li>
      </ul>
    `;
    form.wrapper.appendChild(info);
    return;
  }

  // Signature pad UI
  const sigDiv = document.createElement('div');
  sigDiv.innerHTML = `
    <label>Signature:</label>
    <canvas id="signature-pad" width="300" height="150" style="border:1px solid #ccc;"></canvas>
    <button id="clear-signature" type="button">Clear</button>
  `;
  form.wrapper.appendChild(sigDiv);

  const canvas = document.getElementById('signature-pad');
  const clearBtn = document.getElementById('clear-signature');
  const ctx = canvas.getContext('2d');
  let drawing = false;

  canvas.addEventListener('mousedown', () => drawing = true);
  canvas.addEventListener('mouseup', () => drawing = false);
  canvas.addEventListener('mouseout', () => drawing = false);
  canvas.addEventListener('mousemove', draw);
  clearBtn.addEventListener('click', () => ctx.clearRect(0, 0, canvas.width, canvas.height));

  function draw(e) {
    if (!drawing) return;
    ctx.lineWidth = 2;
    ctx.lineCap = 'round';
    ctx.strokeStyle = '#000';
    ctx.lineTo(e.offsetX, e.offsetY);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(e.offsetX, e.offsetY);
  }

  // Signature data binding
  form.on('before_submit', () => {
    const signatureImage = canvas.toDataURL();
    const hash = frappe.utils.hash(signatureImage);
    form.set_value('signature_hash', hash);
    form.set_value('signature_image', signatureImage);
    form.set_value('signed_at', frappe.datetime.now_datetime());
    frappe.call('frappe.client.get_session_user', null, (res) => {
      if (res.message && res.message.ip_address) {
        form.set_value('ip_address', res.message.ip_address);
      }
    });
  });

  // Confirmation screen
  form.on('after_submit', () => {
    frappe.msgprint({
      title: 'Signature Submitted',
      indicator: 'green',
      message: 'Thank you for signing. This has been saved and logged.',
      primary_action: {
        label: 'Done',
        action() { window.location.href = '/my_repairs'; }
      }
    });
  });
});