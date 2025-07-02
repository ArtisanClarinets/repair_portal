# Frappe JavaScript API Reference

This document consolidates the main APIs, methods, and examples for Frappe Client-Side Development.

---

## 📋 Table of Contents

- [Form Scripts](#form-scripts)
- [Child Table Scripts](#child-table-scripts)
- [Client Scripts](#client-scripts)
- [Form Events](#form-events)
- [Form API (`frm` methods)](#form-api)
- [List View Customization](#list-view-customization)
- [Tree View Customization](#tree-view-customization)
- [Page API](#page-api)
- [Dialog and Prompt APIs](#dialog-and-prompt-apis)
- [Chart API](#chart-api)
- [Scanner API](#scanner-api)
- [Server Calls](#server-calls)
- [Logging](#logging)
- [Form Tours](#form-tours)

---

## Form Scripts

Use `frappe.ui.form.on()` to bind events to a DocType.

```javascript
frappe.ui.form.on('ToDo', {
    refresh(frm) {
        if (frm.doc.reference_type && frm.doc.reference_name) {
            frm.add_custom_button(__(frm.doc.reference_name), () => {
                frappe.set_route('Form', frm.doc.reference_type, frm.doc.reference_name);
            });
        }
    }
});
```

---

## Child Table Scripts

Child events:

```javascript
frappe.ui.form.on('Quotation Item', {
    item_code(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
    }
});
```

---

## Client Scripts

Use *Client Script* if logic is site-specific.

Path: *Home > Customization > Client Script > New*

---

## Form Events

| Event | Description |
|-------|-------------|
| setup | Triggered once when the form is created |
| before_load | Before loading |
| onload | Loaded before render |
| refresh | After render |
| validate | Before save |
| before_save | Before save triggered |
| after_save | After save |
| on_submit | After submit |
| before_cancel | Before cancel |
| after_cancel | After cancel |

Use field triggers:

```javascript
frappe.ui.form.on('ToDo', {
    status(frm) {
        // handle field change
    }
});
```

---

## Form API

Common `frm` methods:

- `frm.set_value(field, value)`
- `frm.refresh()`
- `frm.save()`
- `frm.reload_doc()`
- `frm.add_custom_button(label, function)`
- `frm.toggle_enable(fields, condition)`
- `frm.toggle_reqd(field, condition)`
- `frm.toggle_display(field, condition)`
- `frm.set_query(fieldname, function)`

Example:

```javascript
frm.set_value('status', 'Closed');
frm.refresh_field('status');
```

---

## List View Customization

Create `doctype_list.js`:

```javascript
frappe.listview_settings['Note'] = {
    filters: [['public', '=', 1]],
    get_indicator(doc) {
        if (doc.public) {
            return [__('Public'), 'green'];
        }
        return [__('Private'), 'darkgrey'];
    }
};
```

---

## Tree View Customization

Create `doctype_tree.js`:

```javascript
frappe.treeview_settings['Account'] = {
    title: 'Chart of Accounts',
    get_tree_nodes: 'path.to.method',
    add_tree_node: 'path.to.method',
    fields: [
        { fieldtype: 'Data', fieldname: 'account_name', label: 'Name', reqd: true }
    ]
};
```

---

## Page API

Create page:

```javascript
let page = frappe.ui.make_app_page({
    title: 'My Page',
    parent: wrapper,
    single_column: true
});

page.set_primary_action('New', () => console.log('clicked'));
```

---

## Dialog and Prompt APIs

**Dialog Example:**

```javascript
let d = new frappe.ui.Dialog({
    title: 'My Dialog',
    fields: [{ label: 'Name', fieldname: 'name', fieldtype: 'Data' }],
    primary_action_label: 'Submit',
    primary_action(values) {
        console.log(values);
        d.hide();
    }
});
d.show();
```

**Prompt:**

```javascript
frappe.prompt('Enter Value', (values) => console.log(values));
```

**Confirm:**

```javascript
frappe.confirm('Are you sure?', () => console.log('Yes'), () => console.log('No'));
```

**Msgprint:**

```javascript
frappe.msgprint('Action completed');
```

---

## Chart API

```javascript
let chart = new frappe.ui.RealtimeChart('#chart', 'event_name', 10, {
    title: 'Realtime Chart',
    data: { datasets: [{ name: 'Dataset', values: [] }] },
    type: 'line'
});
chart.start_updating();
```

---

## Scanner API

```javascript
new frappe.ui.Scanner({
    dialog: true,
    on_scan(data) {
        console.log(data.decodedText);
    }
});
```

---

## Server Calls

**frappe.call:**

```javascript
frappe.call('frappe.client.get_list', {
    doctype: 'User'
}).then(r => console.log(r));
```

**frappe.db.get_value:**

```javascript
frappe.db.get_value('User', 'Administrator', 'email')
.then(r => console.log(r));
```

---

## Logging

```python
logger = frappe.logger('api', allow_site=True)
logger.info('My log message')
```

---

## Form Tours

```javascript
frm.tour.init({ tour_name: 'My Tour' }).then(() => frm.tour.start());
```

---

**End of Reference.**