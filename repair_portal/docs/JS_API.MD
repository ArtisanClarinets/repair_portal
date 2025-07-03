# Frappe JavaScript API Reference

This document consolidates the main APIs, methods, and examples for Frappe Client-Side Development.

---
Please review:
Form Scripts 
Form Scripts lets you add client side logic to your Forms. You can write Form Scripts for automatically fetching values, adding validation or adding contextual actions to your Form.

Standard Form Scripts 
When you create a new DocType, a {doctype}.js is created where you can write your form script.

Syntax:

frappe.ui.form.on(doctype, {
    event1() {
        // handle event 1
    },
    event2() {
        // handle event 2
    }
})
For example, todo.js which is located at frappe/desk/doctype/todo/todo.js may look like this:

// Script for ToDo Form
frappe.ui.form.on('ToDo', {
    // on refresh event
    refresh(frm) {
        // if reference_type and reference_name are set,
        // add a custom button to go to the reference form
        if (frm.doc.reference_type && frm.doc.reference_name) {
            frm.add_custom_button(__(frm.doc.reference_name), () => {
                frappe.set_route("Form", frm.doc.reference_type, frm.doc.reference_name);
            });
        }
    }
})
Child Table Scripts 
Child Table Scripts should be written in the same file as their parent.

frappe.ui.form.on('Quotation', {
    // ...
})

frappe.ui.form.on('Quotation Item', {
    // cdt is Child DocType name i.e Quotation Item
    // cdn is the row name for e.g bbfcb8da6a
    item_code(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
    }
})
Custom Form Scripts 
You can also write form scripts by creating Client Script in the system. You should write Client Scripts if the logic is specific to your site. If you want to share Form Scripts across sites, you must include them via Apps.

To create a new Client Script, go to

Home > Customization > Client Script > New

New Client Script
New Client Script for Form

Form Events 
Form Scripts depend on events to trigger. Here are the list of all Form Events that are triggered by Form.

These events will get frm as the first parameter in their handler functions.

frappe.ui.form.on('ToDo', {
 // frm passed as the first parameter
 setup(frm) {
 // write setup code
 }
})
Event Name	Description
setup	Triggered once when the form is created for the first time
before_load	Triggered before the form is about to load
onload	Triggered when the form is loaded and is about to render
refresh	Triggered when the form is loaded and rendered.
onload_post_render	Triggered after the form is loaded and rendered
validate	Triggered before before_save
before_save	Triggered before save is called
after_save	Triggered after form is saved
before_submit	Triggered before submit is called
on_submit	Triggered after form is submitted
before_cancel	Triggered before cancel is called
after_cancel	Triggered after form is cancelled
timeline_refresh	Triggered after form timeline is rendered
{fieldname}_on_form_rendered	Triggered when a row is opened as a form in a Table field
{fieldname}	Triggered when the value of fieldname is changed
Child Table Events 
These events are triggered in the context of a Child Table. Hence, along with frm, they will also get the cdt (Child DocType) and cdn (Child Docname) parameters in their handler functions.

Imagine our "ToDo" DocType has a field called "links" that contains a Child Table. This Child Table is defined in a DocType called "Dynamic Link". We want our code to run whenever a row is added to the table.

// this code is located inside `todo.js`

frappe.ui.form.on('Dynamic Link', { // The child table is defined in a DoctType called "Dynamic Link"
 links_add(frm, cdt, cdn) { // "links" is the name of the table field in ToDo, "_add" is the event
 // frm: current ToDo form
 // cdt: child DocType 'Dynamic Link'
 // cdn: child docname (something like 'a6dfk76')
 // cdt and cdn are useful for identifying which row triggered this event

 frappe.msgprint('A row has been added to the links table 🎉 ');
 }
});
Event Name	Description
before_{fieldname}_remove	Triggered when a row is about to be removed from a Table field
{fieldname}_add	Triggered when a row is added to a Table field
{fieldname}_remove	Triggered when a row is removed from a Table field
{fieldname}_move	Triggered when a row is reordered to another location in a Table field
form_render	Triggered when a row is opened as a form in a Table field
Form API 
Here are a list of common methods that are available on the frm object.

frm.set_value 
Set the value of a field. This will trigger the field change event in the form.

// set a single value
frm.set_value('description', 'New description')

// set multiple values at once
frm.set_value({
 status: 'Open',
 description: 'New description'
})

// returns a promise
frm.set_value('description', 'New description')
 .then(() => {
 // do something after value is set
 })
frm.refresh 
Refresh the form with the latest values from the server. Will trigger before_load, onload, refresh, timeline_refresh and onload_post_render.

frm.refresh();
frm.save 
Trigger form save. Will trigger validate, before_save, after_save, timeline_refresh and refresh.

It can be used to trigger other save actions like Submit, Cancel and Update. In that case, the relevant events will be triggered.

// save form
frm.save();

// submit form
frm.save('Submit');

// cancel form
frm.save('Cancel');

// update form (after submit)
frm.save('Update');

// all methods returns a promise
frm.enable\save / frm.disable\save 
Methods to enable / disable the Save button in the form.

if (frappe.user_roles.includes('Custom Role')) {
 frm.enable_save();
} else {
 frm.disable_save();
}
frm.email_doc 
Open Email dialog for this form.

// open email dialog
frm.email_doc();

// open email dialog with some message
frm.email_doc(`Hello ${frm.doc.customer_name}`);
frm.reload_doc 
Reload document with the latest values from the server and call frm.refresh().

frm.reload_doc();
frm.refresh_field 
Refresh the field and it's dependencies.

frm.refresh_field('description');
frm.is_dirty 
Check if form values has been changed and is not saved yet.

if (frm.is_dirty()) {
 frappe.show_alert('Please save form before attaching a file')
}
frm.dirty 
Set form as "dirty". This is used to set form as dirty when document values are changed. This triggers the _"Not Saved"_ indicator in the Form Views.

frm.doc.browser_data = navigator.appVersion;
frm.dirty();
frm.save();
Calling save without setting the form dirty will trigger a _"No changes in document"_ toast.

frm.is_new 
Check if the form is new and is not saved yet.

// add custom button only if form is not new
if (!frm.is_new()) {
 frm.add_custom_button('Click me', () => console.log('Clicked custom button'))
}
frm.set_intro 
Set intro text on the top of the form. The function takes two parameters: message (string, required) and color (string, optional).

Color can be 'blue', 'red', 'orange', 'green' or 'yellow'. Default is blue.

if (!frm.doc.description) {
 frm.set_intro('Please set the value of description', 'blue');
}
Intro text example
Intro Text Example

frm.add\_custom_button 
Add a custom button in the inner toolbar of the page. Alias to page.add\_inner_button.

// Custom buttons
frm.add_custom_button('Open Reference form', () => {
 frappe.set_route('Form', frm.doc.reference_type, frm.doc.reference_name);
})

// Custom buttons in groups
frm.add_custom_button('Closed', () => {
 frm.doc.status = 'Closed'
}, 'Set Status');
frm.change\custom\button\_type 
Change a specific custom button type by label (and group).

// change type of ungrouped button
frm.change_custom_button_type('Open Reference form', null, 'primary');

// change type of a button in a group
frm.change_custom_button_type('Closed', 'Set Status', 'danger');
frm.remove\_custom_button 
Remove a specific custom button by label (and group).

// remove custom button
frm.remove_custom_button('Open Reference form');

// remove custom button in a group
frm.remove_custom_button('Closed', 'Set Status');
frm.clear\_custom_buttons 
Remove all custom buttons from the inner toolbar.

frm.clear_custom_buttons();
frm.set\_df_property 
Change the docfield property of a field and refresh the field.

// change the fieldtype of description field to Text
frm.set_df_property('description', 'fieldtype', 'Text');

// set the options of the status field to only be [Open, Closed]
frm.set_df_property('status', 'options', ['Open', 'Closed'])

// set a field as mandatory
frm.set_df_property('title', 'reqd', 1)

// set a field as read only
frm.set_df_property('status', 'read_only', 1)
frm.toggle_enable 
Toggle a field or list of fields as read_only based on a condition.

// set status and priority as read_only
// if user does not have System Manager role
let is_allowed = frappe.user_roles.includes('System Manager');
frm.toggle_enable(['status', 'priority'], is_allowed);
frm.toggle_reqd 
Toggle a field or list of fields as mandatory (reqd) based on a condition.

// set priority as mandatory
// if status is Open
frm.toggle_reqd('priority', frm.doc.status === 'Open');
frm.toggle_display 
Show/hide a field or list of fields based on a condition.

// show priority and due_date field
// if status is Open
frm.toggle_display(['priority', 'due_date'], frm.doc.status === 'Open');
frm.set_query 
Apply filters on a Link field to show limited records to choose from. You must call frm.set_query very early in the form lifecycle, usually in setup or onload.

// show only customers whose territory is set to India
frm.set_query('customer', () => {
 return {
 filters: {
 territory: 'India'
 }
 }
})

// show customers whose territory is any of India, Nepal, Japan
frm.set_query('customer', () => {
 return {
 filters: {
 territory: ['in', ['India', 'Nepal', 'Japan']]
 }
 }
})

// set filters for Link field item_code in
// items field which is a Child Table
frm.set_query('item_code', 'items', () => {
 return {
 filters: {
 item_group: 'Products'
 }
 }
})
You can also override the filter method and provide your own custom method on the server side. Just the set the query to the module path of your python method.

// change the filter method by passing a custom method
frm.set_query('fieldname', () => {
 return {
 query: 'dotted.path.to.custom.custom_query',
 filters: {
 field1: 'value1'
 }
 }
})
# python method signature
def custom_query(doctype, txt, searchfield, start, page_len, filters):
 # your logic
 return filtered_list
frm.add_child 
Add a row with values to a Table field.

let row = frm.add_child('items', {
 item_code: 'Tennis Racket',
 qty: 2
});

frm.refresh_field('items');
frm.call 
Call a server side controller method with arguments.

Note: While accessing any server side method using frm.call(), you need to whitelist such method using the @frappe.whitelist decorator.

For the following controller code:

class ToDo(Document):
 @frappe.whitelist()
 def get_linked_doc(self, throw_if_missing=False):
 if not frappe.db.exists(self.reference_type, self.reference_name):
 if throw_if_missing:
 frappe.throw('Linked document not found')

 return frappe.get_doc(self.reference_type, self.reference_name)
You can call it from client using frm.call.

frm.call('get_linked_doc', { throw_if_missing: true })
 .then(r => {
 if (r.message) {
 let linked_doc = r.message;
 // do something with linked_doc
 }
 })
frm.trigger 
Trigger any form event explicitly.

frappe.ui.form.on('ToDo', {
 refresh(frm) {
 frm.trigger('set_mandatory_fields');
 },

 set_mandatory_fields(frm) {
 frm.toggle_reqd('priority', frm.doc.status === 'Open');
 }
})
frm.get_selected 
Get selected rows in Child Tables in an object where key is the table fieldname and values are row names.

let selected = frm.get_selected()
console.log(selected)
// {
// items: ["bbfcb8da6a", "b1f1a43233"]
// taxes: ["036ab9452a"]
// }
frm.ignore\doctypes\on\cancel\all 
To avoid cancellation of linked documents during cancel all, you need to set the frm.ignored_doctypes_on_cancel_all property with an array of DocTypes of linked documents.

frappe.ui.form.on("DocType 1", {
 onload: function(frm) {
 // Ignore cancellation for all linked documents of respective DocTypes.
 frm.ignore_doctypes_on_cancel_all = ["DocType 2", "DocType 3"];
 }
}
In the above example, the system will avoid cancellation for all documents of 'DocType 2' and 'DocType 3' which are linked with document of 'DocType 1' during cancellation.


Controls 
frappe.ui.form.make_control 
frappe.ui.form.make_control({ parent, df })

Makes a frappe control based on df properties and appends into parent container.

frappe.ui.form.make_control({
 parent: $wrapper.find('.my-control'),
 df: {
 label: 'Due Date',
 fieldname: 'due_date',
 fieldtype: 'Date'
 },
 render_input: true
})
Here are the df properties for most of frappe control types.

// Attach
{
 label: 'Attachment',
 fieldname: 'attachment',
 fieldtype: 'Attach'
}

// Attach Image
{
 label: 'User Image',
 fieldname: 'user_image',
 fieldtype: 'Attach Image'
}

// Autocomplete
{
 label: 'Select User',
 label: 'user',
 fieldtype: 'Autocomplete',
 options: [
 'faris@erpnext.com',
 'suraj@erpnext.com'
 ]
}

// Barcode
{
 label: 'Item Barcode',
 fieldname: 'item_barcode',
 fieldtype: 'Barcode'
}

// Check
{
 label: 'Enable feature',
 fieldname: 'enable_feature',
 fieldtype: 'Check'
}

// Code
{
 label: 'JS Script',
 fieldname: 'script',
 fieldtype: 'Code',
 // for syntax highlighting
 options: 'Javascript' // JS, HTML, CSS, Markdown, SCSS, JSON,
 // wrap code
 wrap: true,
 // changing `max_lines` will set the max-height of the editor
 max_lines: 10,
 // changing `min_lines` will set the min-height of the editor
 min_lines: 5
}

// Color
{
 label: 'Your favorite color',
 fieldname: 'user_color',
 fieldtype: 'Color'
}

// Currency
{
 label: 'Amount',
 fieldname: 'amount',
 fieldtype: 'Currency',
 options: 'INR' // or name of field which holds currency
}

// Data
{
 label: 'First Name',
 fieldname: 'first_name',
 fieldtype: 'Data',
 options: 'Email' // 'Name', 'Phone', 'URL', 'Barcode'
}

// Date Range
{
 label: 'Select Date Range',
 fieldname: 'date_range',
 fieldtype: 'Date Range'
}

// Date
{
 label: 'Birth Date',
 fieldname: 'birth_date',
 fieldtype: 'Date'
}

// Datetime
{
 label: 'Submission Date and Time',
 fieldname: 'submission',
 fieldtype: 'Datetime'
}

// Dynamic Link
{
 label: 'Party',
 fieldname: 'party',
 fieldtype: 'Dynamic Link',
 options: 'party_type' // fieldname which holds the Link type
}

// Float
{
 label: 'Threshold',
 fieldname: 'threshold',
 fieldtype: 'Float'
}

// Geolocation
{
 label: 'Meeting Place',
 fieldname: 'meeting_place',
 fieldtype: 'Geolocation'
}

// HTML Editor
{
 label: 'Custom HTML',
 fieldname: 'custom_html',
 fieldtype: 'HTML Editor'
}

// Int
{
 label: 'No of days',
 fieldname: 'no_of_days',
 fieldtype: 'Int'
}

// Link
{
 label: 'Select User',
 fieldname: 'user',
 fieldtype: 'Link',
 options: 'User' // name of doctype
}

// Markdown Editor
{
 label: 'Blog Content',
 fieldname: 'content',
 fieldtype: 'Markdown Editor'
}

// MultiCheck
{
 label: 'Blog Content',
 fieldname: 'content',
 fieldtype: 'MultiCheck',
 options: [
 'Option 1',
 'Option 2',
 'Option 3',
 'Option 4',
 ],
 columns: 2 // break into 2 columns
}

// MultiSelect
{
 label: 'Select Users',
 fieldname: 'users',
 fieldtype: 'MultiSelect',
 options: [
 'faris@erpnext.com',
 'suraj@erpnext.com',
 'shivam@erpnext.com'
 ]
}

// Password
{
 label: 'New Password',
 fieldname: 'password',
 fieldtype: 'Password'
}

// Rating
{
 label: 'Rate your experience',
 fieldname: 'rating',
 fieldtype: 'Rating'
}

// Select
{
 label: 'Status',
 fieldname: 'status',
 fieldtype: 'Select',
 options: [
 'Open',
 'Closed',
 'Cancelled'
 ]
}

// Signature
{
 label: 'Status',
 fieldname: 'status',
 fieldtype: 'Signature'
}

// Text Editor
{
 label: 'Description',
 fieldname: 'description',
 fieldtype: 'Text Editor'
}

// Time
{
 label: 'In Time',
 fieldname: 'in_time',
 fieldtype: 'Time'
}

// Button
{
 label: 'Fetch',
 fieldname: 'fetch',
 fieldtype: 'Button',
 btn_size: 'xs' // xs, sm, lg
}

//Icon
{
 label: 'Page Icon',
 fieldname: 'page_icon',
 fieldtype: 'Icon'
}
Adding Custom Formatters 
You can add custom formatters for text type objects (Data, Select, Text etc) by adding them to the docfield object in frappe.meta.docfield_map

Example:

frappe.meta.docfield_map['DocField'].fieldtype.formatter = (value) => {
 if (value==='Section Break') return '🔵 Section Break';
 else return value;
}


List 
The List View is generated for all DocTypes except Child Tables and Single DocTypes.

The List view is packed with features. Some of them are:

Filters
Sorting
Paging
Filter by tags
Switch view to Report, Calendar, Gantt, Kanban, etc.
List View
List View

Standard List JS 
To customize the List View you must have a {doctype}_list.js file in the doctype directory. Below are all the options that can be customized.

For instance, if you want to customize the Note DocType, you'll have to create a file note_list.js with the following contents.

frappe.listview_settings['Note'] = {
 // add fields to fetch
 add_fields: ['title', 'public'],
 // set default filters
 filters: [
 ['public', '=', 1]
 ],
 hide_name_column: true, // hide the last column which shows the `name`
 onload(listview) {
 // triggers once before the list is loaded
 },
 before_render() {
 // triggers before every render of list records
 },

 // set this to true to apply indicator function on draft documents too
 has_indicator_for_draft: false,

 get_indicator(doc) {
 // customize indicator color
 if (doc.public) {
 return [__("Public"), "green", "public,=,Yes"];
 } else {
 return [__("Private"), "darkgrey", "public,=,No"];
 }
 },
 primary_action() {
 // triggers when the primary action is clicked
 },
 get_form_link(doc) {
 // override the form route for this doc
 },
 // add a custom button for each row
 button: {
 show(doc) {
 return doc.reference_name;
 },
 get_label() {
 return 'View';
 },
 get_description(doc) {
 return __('View {0}', [`${doc.reference_type} ${doc.reference_name}`])
 },
 action(doc) {
 frappe.set_route('Form', doc.reference_type, doc.reference_name);
 }
 },
 // format how a field value is shown
 formatters: {
 title(val) {
 return val.bold();
 },
 public(val) {
 return val ? 'Yes' : 'No';
 }
 }
}
Custom List JS 
You can also customize the list view by creating Client Script in the system. You should write Client Scripts if the logic is specific to your site. If you want to share List view customization across sites, you must include them via Apps.

To create a new Client Script, go to

Home > Customization > Client Script > New



Page API 
Every screen inside the Desk is rendered inside a frappe.ui.Page object.

frappe.ui.make\app\page 
Creates a new Page and attaches it to parent.

let page = frappe.ui.make_app_page({
 title: 'My Page',
 parent: wrapper // HTML DOM Element or jQuery object
 single_column: true // create a page without sidebar
})
New Page
New Page

Page methods 
This section lists out the common methods available on the page instance object.

page.set_title 
Set the page title along with the document title. The document title is shown in browser tab.

page.set_title('My Page')
Page Title
Page Title

page.set\title\sub 
Set the secondary title of the page. It is shown on the right side of the page header.

page.set_title_sub('Subtitle')
Page Subtitle
Page Subtitle

page.set_indicator 
Set the indicator label and color.

page.set_indicator('Pending', 'orange')
Page Indicator
Page Indicator

page.clear_indicator 
Clear the indicator label and color.

page.clear_indicator()
page.set\_primary_action 
Set the primary action button label and handler. The third argument is the icon class which will be shown in mobile view.

let $btn = page.set_primary_action('New', () => create_new(), 'octicon octicon-plus')
Page Primary Action
Page Primary Action

page.clear\_primary_action 
Clear primary action button and handler.

page.clear_primary_action()
page.set\_secondary_action 
Set the secondary action button label and handler. The third argument is the icon class which will be shown in mobile view.

let $btn = page.set_secondary_action('Refresh', () => refresh(), 'octicon octicon-sync')
Page Secondary Action
Page Secondary Action

page.clear\_secondary_action 
Clear secondary action button and handler.

page.clear_secondary_action()
page.add\_menu_item 
Add menu items in the Menu dropdown.

// add a normal menu item
page.add_menu_item('Send Email', () => open_email_dialog())

// add a standard menu item
page.add_menu_item('Send Email', () => open_email_dialog(), true)
Page Menu Dropdown
Page Menu Dropdown

page.clear_menu 
Remove Menu dropdown with items.

page.clear_menu()
page.add\_action_item 
Add menu items in the Actions dropdown.

// add a normal menu item
page.add_action_item('Delete', () => delete_items())
Page Actions Dropdown
Page Actions Dropdown

page.clear\_actions_menu 
Remove Actions dropdown with items.

page.clear_actions_menu()
page.add\_inner_button 
Add buttons in the inner toolbar.

// add a normal inner button
page.add_inner_button('Update Posts', () => update_posts())
Page Inner Button
Page Inner Button

// add a dropdown button in a group
page.add_inner_button('New Post', () => new_post(), 'Make')
Page Inner Button Group
Page Inner Button Group

page.change\_custom_button_type 
Change a specific custom button type by label (and group).

// change type of ungrouped button
page.change_inner_button_type('Update Posts', null, 'primary');

// change type of a button in a group
page.change_inner_button_type('Delete Posts', 'Actions', 'danger');
page.remove\_inner_button 
Remove buttons in the inner toolbar.

// remove inner button
page.remove_inner_button('Update Posts')

// remove dropdown button in a group
page.remove_inner_button('New Posts', 'Make')
page.clear\_inner_toolbar 
Remove the inner toolbar.

page.remove_inner_toolbar()
page.add_field 
Add a form control in the page form toolbar.

let field = page.add_field({
 label: 'Status',
 fieldtype: 'Select',
 fieldname: 'status',
 options: [
 'Open',
 'Closed',
 'Cancelled'
 ],
 change() {
 console.log(field.get_value());
 }
});
Page Form Toolbar
Page Form Toolbar

page.get\_form_values 
Get all form values from the page form toolbar in an object.

let values = page.get_form_values()
// { status: 'Open', priority: 'Low' }
page.clear_fields 
Clear all fields from the page form toolbar.

page.clear_fields()




Tree 
The Tree View is generated for all DocTypes that has Is Tree enabled.

Tree View
Tree View

Standard Tree JS 
To customize the Tree View you must have a {doctype}_tree.js file in the doctype directory. Below are all the options that can be customized.

For instance, if you want to configure the Account DocType, you'll have to create a file account_tree.js with the following contents.

frappe.treeview_settings['Account'] = {
 breadcrumb: 'Accounting',
 title: 'Chart of Accounts',
 filters: [
 {
 fieldname: 'company',
 fieldtype:'Select',
 options: 'Company 1
Company 2',
 label: 'Company',
 on_change: handle_company_change()
 }
 ],
 get_tree_nodes: 'path.to.whitelisted_method.get_children',
 add_tree_node: 'path.to.whitelisted_method.handle_add_account',
 // fields for a new node
 fields: [
 {
 fieldtype: 'Data', fieldname: 'account_name',
 label: 'New Account Name', reqd: true
 },
 {
 fieldtype: 'Link', fieldname: 'account_currency',
 label: 'Currency', options: 'Currency'
 },
 {
 fieldtype: 'Check', fieldname: 'is_group', label: 'Is Group'
 }
 ],
 // ignore fields even if mandatory
 ignore_fields: ['parent_account'],
 // to add custom buttons under 3-dot menu group
 menu_items: [
 {
 label: 'New Company',
 action: function() { frappe.new_doc('Company', true) },
 condition: 'frappe.boot.user.can_create.indexOf('Company') !== -1'
 }
 ],
 onload: function(treeview) {
 // triggered when tree view is instanciated
 },
 post_render: function(treeview) {
 // triggered when tree is instanciated
 },
 onrender: function(node) {
 // triggered when a node is instanciated
 },
 on_get_node: function(nodes) {
 // triggered when `get_tree_nodes` returns nodes
 }
 // enable custom buttons beside each node
 extend_toolbar: true,
 // custom buttons to be displayed beside each node
 toolbar: [
 {
 label: 'Add Child',
 condition: function(node) {},
 click: function() {},
 btnClass: 'hidden-xs'
 }
 ]
}



Common Utilities API 
frappe.get_route 
frappe.get_route()

Returns the current route as an array.

frappe.get_route()
// ["List", "Task", "List"]
frappe.set_route 
frappe.set_route(route)

Changes the current route to route.

// route in parts
frappe.set_route('List', 'Task', 'List')

// route as array
frappe.set_route(['List', 'Task', 'Gantt'])

// route as string
frappe.set_route('List/Event/Calendar')

// route with options
frappe.set_route(['List', 'Task', 'Task'], { status: 'Open' })
frappe.format 
frappe.format(value, df, options, doc)

Format a raw value into user presentable format.

frappe.format('2019-09-08', { fieldtype: 'Date' })
// "09-08-2019"

frappe.format('2399', { fieldtype: 'Currency', options: 'currency' }, { inline: true })
// "2,399.00"
frappe.provide 
frappe.provide(namespace)

Creates a namespace attached to the window object if it doesn't exist.

frappe.provide('frappe.ui.form');

// has the same effect as
window.frappe = {}
window.frappe.ui = {}
window.frappe.ui.form = {}
frappe.require 
frappe.require(asset_path, callback)

Load a JS or CSS asset asynchronously. It is used for libraries that are not used often.

// load a single asset
frappe.require('/assets/frappe/chat.js', () => {
 // chat.js is loaded
})

// load multiple assets
frappe.require(['/assets/frappe/chat.js', '/assets/frappe/chat.css'], () => {
 // chat.js and chat.css are loaded
})


Dialog API 
Frappe provides a group of standard, interactive and flexible dialogs that are easy to configure and use. There's also an API for Python.

frappe.ui.Dialog 
new frappe.ui.Dialog({ title, fields, primary_action })

Creates a new Dialog instance.

let d = new frappe.ui.Dialog({
    title: 'Enter details',
    fields: [
        {
            label: 'First Name',
            fieldname: 'first_name',
            fieldtype: 'Data'
        },
        {
            label: 'Last Name',
            fieldname: 'last_name',
            fieldtype: 'Data'
        },
        {
            label: 'Age',
            fieldname: 'age',
            fieldtype: 'Int'
        }
    ],
    size: 'small', // small, large, extra-large 
    primary_action_label: 'Submit',
    primary_action(values) {
        console.log(values);
        d.hide();
    }
});

d.show();

Dialog
frappe.ui.Dialog

frappe.msgprint 
frappe.msgprint(message) or frappe.msgprint({ title, message, indicator })

Show message in a modal.

// only message
frappe.msgprint(__('Document updated successfully'));

// with options
frappe.msgprint({
    title: __('Notification'),
    indicator: 'green',
    message: __('Document updated successfully')
});

Msgprint
frappe.msgprint

You can also bind a primary action to this dialog by passing action(as a method) within primary_action. Alternatively, primary_action can contain server_action or client_action.

The server_action and client_action are dotted paths to the respective methods which will execute on clicking the primary button.

// with primary action
 frappe.msgprint({
    title: __('Notification'),
    message: __('Are you sure you want to proceed?'),
    primary_action:{
        action(values) {
            console.log(values);
        }
    }
});

// with server and client action
frappe.msgprint({
    title: __('Notification'),
    message: __('Are you sure you want to proceed?'),
    primary_action: {
    'label': 'Proceed',
    // either one of the actions can be passed
    'server_action': 'dotted.path.to.method',
    'client_action': 'dotted_path.to_method',
    'args': args
    }
});

Msgprint with Primary Action
frappe.msgprint with primary action bound

frappe.throw 
frappe.throw(error_message)

Show error_message in a modal and throw exception.

frappe.throw(__('This is an Error Message'))

Throw
frappe.throw

frappe.prompt 
frappe.prompt(label) or frappe.prompt(df) or frappe.prompt(fields)

Prompt user for a value or list of values.

// prompt for single value of type Data
frappe.prompt('First Name', ({ value }) => console.log(value))

// Set title and button label
frappe.prompt('First Name', console.log, 'Enter First Name', 'Submit');

// prompt for single value of any type
frappe.prompt({
    label: 'Birth Date',
    fieldname: 'date',
    fieldtype: 'Date'
}, (values) => {
    console.log(values.date);
})

// prompt for multiple values
frappe.prompt([
    {
        label: 'First Name',
        fieldname: 'first_name',
        fieldtype: 'Data'
    },
    {
        label: 'Last Name',
        fieldname: 'last_name',
        fieldtype: 'Data'
    },
], (values) => {
    console.log(values.first_name, values.last_name);
})

Prompt
frappe.prompt

frappe.confirm 
frappe.confirm(message, if_yes, if_no)

Show a confirmation modal, executes if_yes if confirmation is given else executes if_no.

frappe.confirm('Are you sure you want to proceed?',
    () => {
        // action to perform if Yes is selected
    }, () => {
        // action to perform if No is selected
    })

Prompt
frappe.confirm

frappe.warn 
frappe.warn(title, message_html, proceed_action, primary_label, is_minimizable)

Show a warning modal, executes proceed_actiion if confirmation is given. It can be set as minimizable which allows the dialog to be minimized.

frappe.warn('Are you sure you want to proceed?',
    'There are unsaved changes on this page',
    () => {
        // action to perform if Continue is selected
    },
    'Continue',
    true // Sets dialog as minimizable
)

Prompt
frappe.confirm

frappe.show_alert 
frappe.show_alert(message, seconds) or frappe.show_alert({message, indicator}, seconds)

Alert Dialog is used for showing non-obstructive messages.

Its parameters include message, which can contain the indicator color as well, and its display duration. The default is 7 seconds.

frappe.show_alert('Hi, you have a new message', 5);

//show_alert with indicator
frappe.show_alert({
    message:__('Hi, you have a new message'),
    indicator:'green'
}, 5);

Show Alert
frappe.show_alert

frappe.show_progress 
frappe.show_progress(title, count, total, description)

Displays a progress bar with count (as current progress) and total (as maximum progress value).

frappe.show_progress('Loading..', 70, 100, 'Please wait');

Show Progress
frappe.show_progress

frappe.new_doc 
frappe.new_doc(doctype, route_options, init_callback)

Opens a new form of the specified DocType that allows to edit and save it. If "Quick Entry" is enabled for the DocType (that allows to enter the most important fields) the "Quick Entry" pop-up window will be shown. Otherwise you will be redirected to the usual document entry form.

For example, let's create a new Task:

frappe.new_doc("Task");

Often when you are creating a new document in the user interface you want to initialize some of its fields based on the user interaction that triggered the creation. The other two arguments can be used for such initialization.

Specifically, the route_options argument is a quick and convenient way to set any field of type Link, Select, Data, or Dynamic Link in the new document. Its value should be an object whose keys are the desired field names and whose values are the initial values.

frappe.new_doc("Task", {subject: "New Task"});

If you need to do any other initialization of the new document that is not possible with route_options, init_callback gives you full control. It should be a function of one argument. If the doctype is initialized with a "Quick Entry" form, the callback is called with the "Quick Entry" dialog object just before control is released back to the user. Otherwise, the callback is called with the new document just before the user is allowed to edit it in the standard form.

frappe.new_doc("Task", {subject: "New Task"},
                doc => {doc.description = "Do what's necessary";});

Note that subject is a field of type "Data", so we are able to take advantage of the route_options argument to set it. description is a field of type "Text Editor", so if we want to initialize it, that must be done in the callback.

For a slightly more complex example, here's a call that creates a new Journal Entry of type "Bank Entry" and populates one side of the transaction:

frappe.new_doc("Journal Entry", {"voucher_type": "Bank Entry"}, doc => {
    doc.posting_date = frappe.datetime.get_today();
    let row = frappe.model.add_child(doc, "accounts");
    row.account = 'Bank - A';
    row.account_currency = 'USD';
    row.debit_in_account_currency = 100.0;
    row.credit_in_account_currency = 0.0;
});

frappe.ui.form.MultiSelectDialog 
new frappe.ui.form.MultiSelectDialog({ doctype, target, setters, date_field, get_query, action })

A MultiSelectDialog consists of filter fields followed by a multiple selection list. The primary button will perform the passed action on the selected options.

By default, the Search Term field and Date Range field will compose the filter fields.

The argument list includes:

doctype: The source to fetch and display selection entries from.
target: The target where the modal is to be displayed.
setters: These will compose the filter fields and values to populate them with. These also translate to custom columns for the selection list.
add_filters_group: A boolean value to add/remove the filter group in the dialog below setters. The filter group is same as the list view filters.
date_field: It is necessary to pass the date_field of the DocType in consideration.
get_query: A function that returns query and filters to query the selection list. A custom server side method can be passed via query, and filters will be passed to that method.
action: Contains the primary action to be performed on the selected options. It takes selections as a parameter, which comprises of the selected options.
columns: An array of fields returned by custom query which will become columns in result datatable. Only works with the custom query (get_query argument returning a query).
Let us assume we want to fetch Material Requests into our dialog. We can then go on to invoke the MultiSelectDialog in the following manner:

new frappe.ui.form.MultiSelectDialog({
    doctype: "Material Request",
    target: this.cur_frm,
    setters: {
        schedule_date: null,
        status: 'Pending'
    },
    add_filters_group: 1,
    date_field: "transaction_date",
    get_query() {
        return {
            filters: { docstatus: ['!=', 2] }
        }
    },
    action(selections) {
        console.log(selections);
    }
});

// MultiSelectDialog with custom query method
let query_args = {
    query:"dotted.path.to.method",
    filters: { docstatus: ["!=", 2], supplier: "John Doe" }
}

new frappe.ui.form.MultiSelectDialog({
    doctype: "Material Request",
    target: this.cur_frm,
    setters: {
        schedule_date: null,
        status: 'Pending'
    },
    add_filters_group: 1,
    date_field: "transaction_date",
    columns: ["name", "transaction_date", "status"],
    get_query() {
        return query_args;
    },
    action(selections) {
        console.log(selections);
    }
});

MultiSelectDialog
frappe.ui.form.MultiSelectDialog

Here all the Material Requests that fulfill the filter criteria will be fetched into the selection area. The setter company is added to the filter fields along with its passed value. The date_field will be used to fetch and query dates from the DocType mentioned.

The Make Material Request (or Make {DocType}) secondary action button will redirect you to a new form in order to make a new entry into the DocType passed.

Now, if we want to only select particular item from a Material Request, then we can use optional child_selection_mode to enable child selection


// MultiSelectDialog for individual child selection
new frappe.ui.form.MultiSelectDialog({
    doctype: "Material Request",
    target: this.cur_frm,
    setters: {
        schedule_date: null,
        status: null
    },
    add_filters_group: 1,
    date_field: "transaction_date",
    allow_child_item_selection: 1,
    child_fieldname: "items", // child table fieldname, whose records will be shown &amp; can be filtered
    child_columns: ["item_code", "qty"], // child item columns to be displayed
    get_query() {
        return {
            filters: { docstatus: ['!=', 2] }
        }
    },
    action(selections, args) {
        console.log(args.filtered_children); // list of selected item names
    }
});

MultiSelectDialog
frappe.ui.form.MultiSelectDialog

Here you will see a checkbox Select Individual Items to toggle between child item selection & parent selection. Once you toggle it, all the individual Material Requests Items are listed from the all the queried Material Request, you can now filter these items for selection.

To access the selected children, you can use args.filtered_children list which contains selected child item names.



Chart API 
Frappe provides easy-to-use and fully configurable SVG charts. You can learn about them in the Frappe Chart's documentation.

frappe.ui.RealtimeChart 
new frappe.ui.RealtimeChart(dom_element, event_name, max_label_count, data)

Creates a new RealtimeChart instance that adds real-time data update functionality on top of the Frappe Chart API.

dom_element: HTML Element to be used to render the Chart. event_name: Socket event which will provide the data stream. max_label_count: Maximum number of labels allowed on the x-axis. data: Data for the chart to be initialized with.

// Empty data array
const data = {
 datasets: [
 {
 name: "Some Data",
 values: [],
 },
 ],
};

// Realtime Chart initialization
let chart = new frappe.ui.RealtimeChart("#chart", "test_event", 8, {
 title: "My Realtime Chart",
 data: data,
 type: "line",
 height: 250,
 colors: ["#7cd6fd", "#743ee2"]
});
Here is the sample client code to render a chart over the specified socket event.

The following python code can be executed as a cron job using Hook functionality.

data = {
 'label': 1,
 'points': [10]
}
frappe.publish_realtime('test_event', data)
The label key specifies the label to be appended in the Chart. The points key specifies the array of points to be plotted. The number of values in the points array depends on the number of datasets.

This would produce a Chart like

RealtimeChart

frappe.ui.RealtimeChart.start_updating 
frappe.ui.RealtimeChart.start_updating()

Start listening to the specified socket event and update the RealtimeChart accordingly.

frappe.ui.RealtimeChart.start_updating();
RealtimeChart _frappe.ui.RealtimeChart.start_updating_

frappe.ui.RealtimeChart.stop_updating 
frappe.ui.RealtimeChart.stop_updating()

Stop listening to the socket event that RealtimeChart was initialized with.

frappe.ui.RealtimeChart.stop_updating();
frappe.ui.RealtimeChart.update_chart 
frappe.ui.update_chart(label, data)

Manually updates RealtimeChart by appending the label and associated data to the end of the chart.

frappe.ui.update_chart(2, [30]);



Scanner API 
Frappe uses the open-source library Html5-QRCode to provide a flexible way to handle inputs like Barcodes, QRCodes, etc. using the device camera.

frappe.ui.Scanner 
new frappe.ui.Scanner({ ... })
Creates a new Scanner instance that can be used to scan single or multiple barcodes.

Options:

container: Dom element under which video feed from the camera will be shown.
dialog: If set as true, will open a dialog to show video feed from the camera.
multiple: If set as false, will stop scanning after one successful scan.
on_scan: Callback method to handle the scanned input.
Here is a sample client code to scan one single barcode and log it to the console.

new frappe.ui.Scanner({
 dialog: true, // open camera scanner in a dialog
 multiple: false, // stop after scanning one value
 on_scan(data) {
 console.log(data.decodedText);
 }
});
The below code can be used to continously scan and handle the scanned input.

const scanner = new frappe.ui.Scanner({
 dialog: true, // open camera scanner in a dialog
 multiple: true, // stop after scanning one value
 on_scan(data) {
 handle_scanned_barcode(data.decodedText);
 }
});


Server Calls (AJAX) 
frappe.call 
frappe.call(method, args)

Makes an AJAX request to the server, where the method which is the dotted path to a whitelisted Python method, is executed and it's return value is sent as the response.

// call with no parameters
frappe.call('ping')
 .then(r => {
 console.log(r)
 // {message: "pong"}
 })

// call with a single parameter
frappe.call('frappe.core.doctype.user.user.get_role_profile', {
 role_profile: 'Test'
}).then(r => {
 console.log(r.message)
})

// call with all options
frappe.call({
 method: 'frappe.core.doctype.user.user.get_role_profile',
 args: {
 role_profile: 'Test'
 },
 // disable the button until the request is completed
 btn: $('.primary-action'),
 // freeze the screen until the request is completed
 freeze: true,
 callback: (r) => {
 // on success
 },
 error: (r) => {
 // on error
 }
})
frappe.db.get_doc 
frappe.db.get_doc(doctype, name, filters)

Returns the Document object of doctype and name. If name is not provided, gets the first document matched by filters.

// get doc by name
frappe.db.get_doc('Task', 'TASK00002')
 .then(doc => {
 console.log(doc)
 })

// get doc by filters
frappe.db.get_doc('Task', null, { status: 'Open' })
 .then(doc => {
 console.log(doc)
 })
frappe.db.get_list 
frappe.db.get_list(doctype, { fields, filters })

Returns a list of records of doctype with fields and filters.

frappe.db.get_list('Task', {
 fields: ['subject', 'description'],
 filters: {
 status: 'Open'
 }
}).then(records => {
 console.log(records);
})
frappe.db.get_value 
frappe.db.get_value(doctype, name, fieldname)

Returns a document's field value or a list of values.

// single value
frappe.db.get_value('Task', 'TASK00004', 'status')
 .then(r => {
 console.log(r.message.status) // Open
 })

// multiple values
frappe.db.get_value('Task', 'TASK00004', ['status', 'subject'])
 .then(r => {
 let values = r.message;
 console.log(values.status, values.subject)
 })

// using filters
frappe.db.get_value('Task', {status: 'Open'}, 'subject')
 .then(r => {
 let values = r.message;
 console.log(values.subject)
 })
frappe.db.get\single\value 
frappe.db.get_single_value(doctype, field)

Returns a field value from a Single DocType.

frappe.db.get_single_value('System Settings', 'time_zone')
 .then(time_zone => {
 console.log(time_zone);
 })
frappe.db.set_value 
frappe.db.set_value(doctype, docname, fieldname, value, callback)

Sets a document's property using frappe.get_doc and doc.save on server.

// update a field's value
frappe.db.set_value('Task', 'TASK00004', 'status', 'Open')
 .then(r => {
 let doc = r.message;
 console.log(doc);
 })

// update multiple fields
frappe.db.set_value('Task', 'TASK00004', {
 status: 'Working',
 priority: 'Medium'
}).then(r => {
 let doc = r.message;
 console.log(doc);
})
frappe.db.insert 
frappe.db.insert(doc)

Insert a new document.

frappe.db.insert({
 doctype: 'Task',
 subject: 'New Task'
}).then(doc => {
 console.log(doc);
})
frappe.db.count 
frappe.db.count(doctype, filters)

Returns number of records for a given doctype and filters.

// total number of Task records
frappe.db.count('Task')
 .then(count => {
 console.log(count)
 })

// total number of Open Tasks
frappe.db.count('Task', { status: 'Open' })
 .then(count => {
 console.log(count)
 })
frappe.db.delete_doc 
frappe.db.delete_doc(doctype, name)

Delete a document identified by doctype and name.

frappe.db.delete_doc('Task', 'TASK00004')
frappe.db.exists 
frappe.db.exists(doctype, name)

Returns true if a document record exists.

frappe.db.exists('Task', 'TASK00004')
 .then(exists => {
 console.log(exists) // true
 })


Logging 
Logging is a means of tracking events that happen when some software runs. Under the bench architecture, with multitenancy, it might get really complicated really fast to track down and eliminate any uncertainties. You may wan't to log events along with circumstantial, variable data.

Frappe implements Python's logging module to maintain bench and site wise logs. Version 13 uses Log Rotation to maintain the last 20 files along with the current running of 100kB each for the out of the box log files.

frappe.log_level 
Maintains the log level of Frappe processes. To learn more about logging levels, you can check out Python's documentation.

frappe.utils.logger.set_log_level 
frappe.utils.logger.set_log_level(level) can be used to set the log level and regenerate the loggers dynamically.

frappe.loggers 
frappe.loggers maintains a dict of active loggers in your process. The key is the name of the logger, typically "{module}-{site}" and the value holds the Logger instance.

A web worker may have frappe.loggers such as the following if docs.erpnext.com and frappeframework.com are the sites on the bench.

{
    "frappe.web-docs.erpnext.com": <logger frappe.web-docs.erpnext.com="" (debug)="">,
    "frappe.web-frappeframework.com": <logger frappe.web-frappeframework.com="" (debug)="">
}
frappe.logger 
frappe.logger(module, with_more_info, allow_site, filter, max_size, file_count)

Returns a logging.Logger object with Site and Bench level logging capabilities. If logger doesn't already exist, creates and updatesfrappe.loggers.

Arguments:

module: Name of your logger and consequently your log file.
with_more_info: Will log the Form Dict as additional information, typically useful for requests.
allow_site: Pass site name to explicitly log under it's logs. If True and unspecified, guesses which site the logs would be saved under.
filter: Add a filter function for your logger.
max_size: Max file size of each log file in bytes.
file_count: Max count of log files to be retained via Log Rotation.
Usage 
frappe.logger("frappe.web").debug({
    "site": "frappeframework.com",
    "remote_addr": "192.148.1.7",
    "base_url": "https://frappeframework.com/docs/v14/user/en/api/logging",
    "full_path": "/docs/v14/user/en/api/logging",
    "method": "POST",
    "scheme": "https",
    "http_status_code": 200
})
2020-07-31 16:06:55,067 DEBUG frappe.web {'site': 'frappeframework.com', 'remote_addr': '192.148.1.7', 'base_url': 'https://frappeframework.com/docs/v14/user/en/api/logging', 'full_path': '/docs/v14/user/en/api/logging', 'method': 'POST', 'scheme': 'https', 'http_status_code': 200}
The above entry would be logged under ./logs/frappe.web.log and ./sites/frappeframework.com/logs/frappe.web.log files.

Usage specified as implemented in app.py#L102-L110

Example 
Consider a scenario where you've written an API for updating a counter with the value sent by the user and return the updated value. Now you want to log information in the API, to make sure it's working as expected. So, you create a logger api to track events for the same.

frappe.utils.logger.set_log_level("DEBUG")
logger = frappe.logger("api", allow_site=True, file_count=50)


@frappe.whitelist()
def update(value):
    user = frappe.session.user
    logger.info(f"{user} accessed counter_app.update with value={value}")

    current_value = frappe.get_single_value("Value", "counter")
    updated_value = current_value + value
    logger.debug(f"{current_value} + {value} = {updated_value}")
    frappe.db.set_value("Value", "Value", "counter", updated_value)
    logger.info(f"{user} updated value to {value}")

    return updated_value
API calls made to this endpoint will now start getting logged in your api.log as follows

2020-07-31 16:06:55,067 INFO api gavin@frappe.io accessed counter_app.update with value 100
2020-07-31 16:06:55,067 DEBUG api 1000 + 100 = 1100
2020-07-31 16:06:55,068 INFO api gavin@frappe.io updated value to 1100
Learn more about Logging in Frappe here

Form Tours 
Frappe provides an easy way to generate form tutorials for your complex doctype with very little configuration.

Form Tour

Creating a Form Tour 
To create a Form Tour, type "new form tour" in awesomebar and hit enter.

Enter Title. For eg., 'Creating a Custom Field'
Select Reference DocType.
Add steps defining each fields.
Save the document.
Custom Field Form Tour
A Tour to explain creation of Custom Fields

Configuration Options 
Form Tour 
Is Standard: To make a standard Form Tour which will be stored as JSON. Can only be set while developer mode is on.
Save on Completion: If checked, the last step of the Form Tour will prompt the user to save the document.
Show First Document Tour: If you want to show the tour of an existing document instead of a new form, enable this. As the name suggests, it gives the tour of the very first document created for this DocType.
Include Name Field: For some doctypes, the name is set by the user. On enabling this, the name field becomes the first step of the tour.
Form Tour Steps 
Field: A field from the selected doctype. This will be highlighted with a Title & Description.
Title & Description: To describe the field for its use, impact, and other hidden wirings of the field.
Position: The position of the highlighting popover is decided by this field. There are multiple options to choose depending upon the position of the highlighted field.
Next Condition: A code field which expects a valid JS condition which applies on the document. For eg., for a Task DocType Tour, we can check if task priority is set before going to the next condition by setting next condition as follows:

eval: doc.priority != ""

Is Table Field: To be checked if the field to be highlighted is under a child table.
Parent Field: Table field from the selected doctype. Only visible if Is Table Field is checked. Allows user to select a child table field.
Triggering the Tours 
Once you are done describing the Form & its fields, you are now ready to trigger the tour by using Form API. You just have to initialize the tour with appropriate tour_name and then simply start the tour with frm.tour.start().

frappe.ui.form.on('Custom Field', 'onload', () => {
 const tour_name = 'Creating a Custom Field';
 frm.tour
 .init({ tour_name })
 .then(() => frm.tour.start());
});

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