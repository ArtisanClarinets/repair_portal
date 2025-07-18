frappe.ready(() => {
load_profiles();
});

function load_profiles() {
frappe.call('repair_portal.api.dashboard.get_profiles').then(r => {
const data = r.message || {};
render_client(data.client);
render_players(data.players || []);
render_instruments(data.instruments || []);
});
}

function render_client(client) {
const wrap = document.getElementById('client-pane');
wrap.innerHTML = '';
if (!client) {
wrap.innerHTML = '<p>No Client Profile found.</p>';
return;
}
const html = `
<div class="card">
<div class="card-body">
<h5 class="card-title">${frappe.utils.escape_html(client.client_name || '')}</h5>
<p>Email: ${frappe.utils.escape_html(client.email || '')}</p>
<p>Phone: ${frappe.utils.escape_html(client.phone || '')}</p>
<button class="btn btn-primary btn-sm" id="edit-client">Edit</button>
</div>
</div>`;
wrap.innerHTML = html;
wrap.querySelector('#edit-client').addEventListener('click', () => {
open_edit_dialog('Client Profile', client.name, [
{fieldname: 'client_name', label: 'Client Name', fieldtype: 'Data', reqd: 1, default: client.client_name},
{fieldname: 'email', label: 'Email', fieldtype: 'Data', default: client.email},
{fieldname: 'phone', label: 'Phone', fieldtype: 'Data', default: client.phone}
]);
});
}

function render_players(players) {
const wrap = document.getElementById('player-pane');
wrap.innerHTML = '';
if (!players.length) {
wrap.innerHTML = '<p>No Player Profiles.</p>';
return;
}
players.forEach(p => {
const div = document.createElement('div');
div.className = 'card mb-2';
div.innerHTML = `<div class="card-body">
<h5 class="card-title">${frappe.utils.escape_html(p.player_name)}</h5>
<button class="btn btn-primary btn-sm" data-name="${p.name}">Edit</button>
</div>`;
div.querySelector('button').addEventListener('click', (e) => {
open_edit_dialog('Player Profile', p.name, [
{fieldname: 'player_name', label: 'Player Name', fieldtype: 'Data', reqd: 1, default: p.player_name}
]);
});
wrap.appendChild(div);
});
}

function render_instruments(instruments) {
const wrap = document.getElementById('instrument-pane');
wrap.innerHTML = '';
if (!instruments.length) {
wrap.innerHTML = '<p>No Instrument Profiles.</p>';
return;
}
instruments.forEach(i => {
const div = document.createElement('div');
div.className = 'card mb-2';
div.innerHTML = `<div class="card-body">
<h5 class="card-title">${frappe.utils.escape_html(i.serial_no || i.name)}</h5>
<button class="btn btn-primary btn-sm" data-name="${i.name}">Edit</button>
</div>`;
div.querySelector('button').addEventListener('click', () => {
open_edit_dialog('Instrument Profile', i.name, [
{fieldname: 'serial_no', label: 'Serial No', fieldtype: 'Data', reqd: 1, default: i.serial_no}
]);
});
wrap.appendChild(div);
});
}

function open_edit_dialog(doctype, docname, fields) {
const dialog = new frappe.ui.Dialog({title: `Edit ${doctype}`, fields});
dialog.set_primary_action('Save', () => {
const values = dialog.get_values();
frappe.call('repair_portal.api.dashboard.save_profile', {docname, data: values}).then(() => {
dialog.hide();
load_profiles();
});
});
dialog.show();
}
