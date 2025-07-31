# Frappe Python API Reference

This document provides an in-depth reference of Frappe’s Python APIs, including Realtime Events, Background Jobs, Document APIs, Database APIs, Request Lifecycle, Utility Functions, and Hooks.

---
Can you please repeat with this in a file called PYTHON_API.md

Information:
Realtime (socket.io) 
Frappe ships with an API for realtime events based on socket.io. Since socket.io needs a Node server to run, we run a Node process in parallel to the main web server.

frappe.realtime.on 
To listen to realtime events on the client (browser), you can use the frappe.realtime.on method:

frappe.realtime.on('event_name', (data) => {
 console.log(data)
})
frappe.realtime.off 
Stop listening to an event you have subscribed to:

frappe.realtime.off('event_name')
frappe.publish_realtime 
To publish a realtime event from the server, you can use the frappe.publish_realtime method:

frappe.publish_realtime('event_name', data={'key': 'value'})
frappe.publish_progress 
You can use this method to show a progress bar in a dialog:

frappe.publish_progress(25, title='Some title', description='Some description')

Background Jobs 
Frappe ships with a system for running jobs in the background. It is implemented by using the schedule package and a simple long-running infinite while loop.

You can enqueue a python method to run in the background by using the frappe.enqueue method:

def long_running_job(param1, param2):
 # expensive tasks
 pass

# directly pass the function
frappe.enqueue(long_running_job, queue='short', param1='A', param2='B')

# or pass the full module path as string
frappe.enqueue('app.module.folder.long_running_job', queue='short', param1='A', param2='B')
Here are all the possible arguments you can pass to the enqueue:

frappe.enqueue(
 method, # python function or a module path as string
 queue="default", # one of short, default, long
 timeout=None, # pass timeout manually
 is_async=True, # if this is True, method is run in worker
 now=False, # if this is True, method is run directly (not in a worker) 
 job_name=None, # specify a job name
 enqueue_after_commit=False, # enqueue the job after the database commit is done at the end of the request
 at_front=False, # put the job at the front of the queue
 **kwargs, # kwargs are passed to the method as arguments
)
You can also enqueue a Document method by using frappe.enqueue_doc:

frappe.enqueue_doc(
 doctype,
 name,
 "do_something", # name of the controller method
 queue="long",
 timeout=4000,
 param="value"
)
Queue 
There are 3 default queues that are configured with the framework: short, default, and long. Each queue has a default timeout as follows:

short: 300 seconds
default: 300 seconds
long: 1500 seconds
You can also pass a custom timeout to the enqueue method.

Custom Queues 
You can add custom queues by configuring them in [common_site_config.json](https://frappeframework.com/docs/v14/user/en/basics/site_config#common-site-config):

{
 ...
 "workers": {
 "myqueue": {
 "timeout": 5000, # queue timeout
 "background_workers": 4, # number of workers for this queue
 } 
 }
}
Workers 
By default Frappe sets up 3 worker types for consuming from each queue. The default configuration looks like this:

bench worker --queue short
bench worker --queue default
bench worker --queue long
In production these 3 worker processes are replicated to configured number of background workers to handle higher workloads.

NOTE: This way of mapping workers to single queue is just a convention and it's not necessary to follow it.

Multi-queue consumption 
You can specify more than one queue for workers to consume from by specifying a comma separate string of queue names.

Example: If you wanted to combine short and default workers and only use two types of workers instead of default configuration then you can modify your worker configuration like this:

bench worker --queue short,default
bench worker --queue long
NOTE: The examples shown here are for Procfile format but they can be applied to supervisor or systemd configurations easily too.

Burst Mode using --burst 
bench worker --queue short --burst
This command will spawn a tempoary worker that will start consuming short queue and quit once queue is empty. If you periodically need higher amount of workers then you can use your OS's crontab to setup burst workers at specific times.

Scheduler Events 
You can use Scheduler Events for running tasks periodically in the background using the scheduler_events hook.

app/hooks.py

scheduler_events = {
 "hourly": [
 # will run hourly
 "app.scheduled_tasks.update_database_usage"
 ],
}
app/scheduled_tasks.py

def update_database_usage():
 pass
After changing any scheduled events in hooks.py, you need to run bench migrate for changes to take effect.

Available Events 
hourly, daily, weekly, and monthly

These events will trigger every hour, day, week, and month respectively.

hourly_long, daily_long, weekly_long, monthly_long

Same as above but these jobs are run in the long worker suitable for long-running jobs.

all

The all event is triggered every 60 seconds. This can be configured via the scheduler_tick_interval key in [common_site_config.json](https://frappeframework.com/docs/v14/user/en/basics/sites#scheduler_tick_interval)

cron

A valid cron string that can be parsed by croniter.

Usage Examples:

scheduler_events = {
 "daily": [
 "app.scheduled_tasks.manage_recurring_invoices"
 ],
 "daily_long": [
 "app.scheduled_tasks.take_backups_daily"
 ],
 "cron": {
 "15 18 * * *": [
 "app.scheduled_tasks.delete_all_barcodes_for_users"
 ],
 "*/6 * * * *": [
 "app.scheduled_tasks.collect_error_snapshots"
 ],
 "annual": [
 "app.scheduled_tasks.collect_error_snapshots"
 ]
 }
}

Document API 
A Document is an instance of a DocType. It is derived from the frappe.model.Document class and represents a single record in the database table.

frappe.get_doc 
frappe.get_doc(doctype, name)

Returns a Document object of the record identified by doctype and name. If no document is found, a DoesNotExistError is raised. If doctype is a Single DocType name is not required.

# get an existing document
doc = frappe.get_doc('Task', 'TASK00002')
doc.title = 'Test'
doc.save()

# get a single doctype
doc = frappe.get_doc('System Settings')
doc.timezone # Asia/Kolkata
frappe.get_doc(dict)

Returns a new Document object in memory which does not exist yet in the database.

# create a new document
doc = frappe.get_doc({
 'doctype': 'Task',
 'title': 'New Task'
})
doc.insert()
frappe.get_doc(doctype={document_type}, key1 = value1, key2 = value2, ...)

Returns a new Document object in memory which does not exist yet in the database.

# create new object with keyword arguments
user = frappe.get_doc(doctype='User', email_id='test@example.com')
user.insert()
frappe.get\last\doc 
frappe.get_last_doc(doctype, filters, order_by)

Returns the last Document object created under the mentioned doctype.

# get the last Task created
task = frappe.get_last_doc('Task')
You can also specify filters to refine your results. For instance, you can retrieve the last canceled Task by adding a filter.

# get the last available Cancelled Task
task = frappe.get_last_doc('Task', filters={"status": "Cancelled"})
By default, the order_by argument is set to creation desc, but this value can be overridden to use other non-standard fields that can serve the same purpose. For instance, you have a field timestamp under the Task DocType that tracks the time it was approved or marked valid instead of the time it was created.

# get the last Task created based on a non-standard field
task = frappe.get_last_doc('Task', filters={"Status": "Cancelled"}, order_by="timestamp desc")
Alternatively, you can choose to go completely against all of this and as a part of a joke change it to "creation asc" to retrieve the first document instead.

frappe.get\cached\doc 
Similar to frappe.get_doc but will look up the document in cache first before hitting the database.

frappe.new_doc 
frappe.new_doc(doctype)

Alternative way to create a new Document.

# create a new document
doc = frappe.new_doc('Task')
doc.title = 'New Task 2'
doc.insert()
frappe.delete_doc 
frappe.delete_doc(doctype, name)

Deletes the record and its children from the database. Also deletes other documents like Communication, Comments, etc linked to it.

frappe.delete_doc('Task', 'TASK00002')
frappe.rename_doc 
frappe.rename_doc(doctype, old_name, new_name, merge=False)

Rename a document's name (primary key) from old_name to new_name. If merge is True and a record with new_name exists, will merge the record with it.

frappe.rename_doc('Task', 'TASK00002', 'TASK00003')
Rename will only work if Allow Rename is set in the DocType Form.

frappe.get_meta 
frappe.get_meta(doctype)

Returns meta information of doctype. This will also apply custom fields and property setters.

meta = frappe.get_meta('Task')
meta.has_field('status') # True
meta.get_custom_fields() # [field1, field2, ..]
To get the original document of DocType (without custom fields and property setters) use frappe.get_doc('DocType', doctype_name)

Document Methods 
This section lists out common methods that are available on the doc object.

doc.insert 
This method inserts a new document into the database table. It will check for user permissions and execute before_insert, validate, on_update, after_insert methods if they are written in the controller.

It has some escape hatches that can be used to skip certain checks explained below.

doc.insert(
 ignore_permissions=True, # ignore write permissions during insert
 ignore_links=True, # ignore Link validation in the document
 ignore_if_duplicate=True, # dont insert if DuplicateEntryError is thrown
 ignore_mandatory=True # insert even if mandatory fields are not set
)
doc.save 
This method saves changes to an existing document. This will check for user permissions and execute validate before updating and on_update after updating values.

doc.save(
 ignore_permissions=True, # ignore write permissions during insert
 ignore_version=True # do not create a version record
)
doc.delete 
Delete the document record from the database table. This method is an alias to frappe.delete_doc.

doc.delete()
doc.get\doc\before\_save 
Will return a version of the doc before the changes were made. You can use it to compare what changed from the last version.

old_doc = doc.get_doc_before_save()
if old_doc.price != doc.price:
 # price changed
 pass
doc.reload 
Will get the latest values from the database and update the doc state.

When you are working with a document, it may happen that some other part of code updates the value of some field directly in the database. In such cases you can use this method to reload the doc.

doc.reload()
doc.check_permission 
Throw if the current user has no permission for the provided permtype.

doc.check_permission(permtype='write') # throws if no write permission
doc.get_title 
Get the document title based on title_field or field named title or name.

title = doc.get_title()
doc.notify_update 
Publish realtime event to indicate that the document has been modified. Client side event handlers react to this event by updating the form.

doc.notify_update()
doc.db_set 
Set a field value of the document directly in the database and update the modified timestamp.

This method does not trigger controller validations and should be used very carefully.

# updates value in database, updates the modified timestamp
doc.db_set('price', 2300)

# updates value in database, will trigger doc.notify_update()
doc.db_set('price', 2300, notify=True)

# updates value in database, will also run frappe.db.commit()
doc.db_set('price', 2300, commit=True)

# updates value in database, does not update the modified timestamp
doc.db_set('price', 2300, update_modified=False)
doc.append 
Append a new item to a child table.

doc.append("childtable", {
 "child_table_field": "value",
 "child_table_int_field": 0,
 ...
})
doc.get_url 
Returns Desk URL for this document. For e.g: /app/task/TASK00002

url = doc.get_url()
doc.add_comment 
Add a comment to this document. Will show up in timeline in Form view.

# add a simple comment
doc.add_comment('Comment', text='Test Comment')

# add a comment of type Edit
doc.add_comment('Edit', 'Values changed')

# add a comment of type Shared
doc.add_comment("Shared", "{0} shared this document with everyone".format(user))
doc.add_seen 
Add the given/current user to list of users who have seen this document. Will update the _seen column in the table. It is stored as a JSON Array.

# add john to list of seen
doc.add_seen('john@doe.com')

# add session user to list of seen
doc.add_seen()
This works only if Track Seen is enabled in the DocType.

doc.add_viewed 
Add a view log when a user views a document i.e opens the Form.

# add a view log by john
doc.add_viewed('john@doe.com')

# add a view log by session user
doc.add_viewed()
This works only if Track Views is enabled in the DocType.

doc.add_tag 
Add a tag to a document. Tags are generally used to filter and group documents.

# add tags
doc.add_tag('developer')
doc.add_tag('frontend')
doc.get_tags 
Returns a list of tags associated with the specific document.

# get all tags
doc.get_tags()
doc.run_method 
Run method if defined in controller, will also trigger hooks if defined.

doc.run_method('validate')
doc.queue_action 
Run a controller method in background. If the method has an inner function, like _submit for submit, it will call that method instead.

doc.queue_action('send_emails', emails=email_list, message='Howdy')
doc.get_children() 
Only available on tree DocTypes (inherited from NestedSet).

Returns a generator that yields an instance of NestedSet for each child record.

for child_doc in doc.get_children():
 print(child_doc.name)
It can also be applied recursively:

for child_doc in doc.get_children():
 print(child_doc.name)
 for grandchild_doc in child_doc.get_children():
 print(grandchild_doc.name)
doc.get_parent() 
Only available on tree DocTypes (inherited from NestedSet).

Returns an instance of NestedSet for the parent record.

parent_doc = doc.get_parent()
grandparent_doc = parent_doc.get_parent()
doc.db_insert() 
Serialize and insert a document into database. Warning: This bypasses all validations and controller methods that might be required to run before and after inserting. When in doubt use doc.insert() instead.

doc = frappe.get_doc(doctype="Controller", data="")
doc.db_insert()
doc.db_update() 
Serialize and update a document into database. Warning: This bypasses all validations and controller methods that might be required to run before and after updating. When in doubt use doc.save() instead.

doc = frappe.get_last_doc("User")
doc.last_active = now()
doc.db_update()

Database API 
frappe.db.get_list 
frappe.db.get_list(doctype, filters, or_filters, fields, order_by, group_by, start, page_length)

Also aliased to frappe.get_list
Returns a list of records from a doctype table. ORM Wrapper for a SELECT query. Will also apply user permissions for the records for the session user. Only returns the document names if the fields keyword argument is not given. By default this method returns a list of dicts, but, you can pluck a particular field by giving the pluck keyword argument:

frappe.db.get_list('Employee')

# output
[{'name': 'HR-EMP-00008'},
 {'name': 'HR-EMP-00006'},
 {'name': 'HR-EMP-00010'},
 {'name': 'HR-EMP-00005'}
]

# with pluck
frappe.db.get_list('Employee', pluck='name')

# output
['HR-EMP-00008',
 'HR-EMP-00006',
 'HR-EMP-00010',
 'HR-EMP-00005'
]

Combining filters and other arguments:

frappe.db.get_list('Task',
    filters={
        'status': 'Open'
    },
    fields=['subject', 'date'],
    order_by='date desc',
    start=10,
    page_length=20,
    as_list=True
)

# output
(('Update Branding and Design', '2019-09-04'),
('Missing Documentation', '2019-09-02'),
('Fundraiser for Foundation', '2019-09-03'))

# Tasks with date after 2019-09-08
frappe.db.get_list('Task', filters={
    'date': ['>', '2019-09-08']
})

# Tasks with date between 2020-04-01 and 2021-03-31 (both inclusive)
frappe.db.get_list('Task', filters=[[
    'date', 'between', ['2020-04-01', '2021-03-31']
]])

# Tasks with subject that contains "test"
frappe.db.get_list('Task', filters={
    'subject': ['like', '%test%']
})

# Count number of tasks grouped by status
frappe.db.get_list('Task',
    fields=['count(name) as count', 'status'],
    group_by='status'
)
# output
[{'count': 1, 'status': 'Working'},
 {'count': 2, 'status': 'Overdue'},
 {'count': 2, 'status': 'Open'},
 {'count': 1, 'status': 'Filed'},
 {'count': 20, 'status': 'Completed'},
 {'count': 1, 'status': 'Cancelled'}]

frappe.db.get_all 
frappe.db.get_all(doctype, filters, or_filters, fields, order_by, group_by, start, page_length)

Also aliased to frappe.get_all
Same as frappe.db.get_list but will fetch all records without applying permissions.

frappe.db.get_value 
frappe.db.get_value(doctype, name, fieldname) or frappe.db.get_value(doctype, filters, fieldname)

Also aliased to frappe.get_value and frappe.db.get_values
Returns a document's field value or a list of values.

# single value
subject = frappe.db.get_value('Task', 'TASK00002', 'subject')

# multiple values
subject, description = frappe.db.get_value('Task', 'TASK00002', ['subject', 'description'])

# as dict
task_dict = frappe.db.get_value('Task', 'TASK00002', ['subject', 'description'], as_dict=1)
task_dict.subject
task_dict.description

# with filters, will return the first record that matches filters
subject, description = frappe.db.get_value('Task', {'status': 'Open'}, ['subject', 'description'])

frappe.db.get_single_value 
frappe.db.get_single_value(doctype, fieldname)

Returns a field value from a Single DocType.

timezone = frappe.db.get_single_value('System Settings', 'timezone')

frappe.db.set_value 
frappe.db.set_value(doctype, name, fieldname, value)

Also aliased to frappe.db.update
Sets a field's value in the database, does not call the ORM triggers but updates the modified timestamp (unless specified not to).

# update a field value
frappe.db.set_value('Task', 'TASK00002', 'subject', 'New Subject')

# update multiple values
frappe.db.set_value('Task', 'TASK00002', {
    'subject': 'New Subject',
    'description': 'New Description'
})

# update without updating the `modified` timestamp
frappe.db.set_value('Task', 'TASK00002', 'subject', 'New Subject', update_modified=False)

This method won't call ORM triggers like validate and on_update. Use this method to update hidden fields or if you know what you are doing.

frappe.db.exists 
frappe.db.exists(doctype, name)

Returns true if a document record exists.

Pass doctype and docname:

frappe.db.exists("User", "jane@example.org", cache=True)

Pass a dict of filters including the "doctype" key:

frappe.db.exists({"doctype": "User", "full_name": "Jane Doe"})

Pass the doctype and a dict of filters:

frappe.db.exists("User", {"full_name": "Jane Doe"})

frappe.db.count 
frappe.db.count(doctype, filters)

Returns number of records for a given doctype and filters.

# total number of Task records
frappe.db.count('Task')

# total number of Open tasks
frappe.db.count('Task', {'status': 'Open'})

frappe.db.delete 
frappe.db.delete(doctype, filters)

Delete doctype records that match filters. This runs a DML command, which means it can be rolled back. If no filters specified, all the records of the doctype are deleted.

frappe.db.delete("Route History", {
    "modified": ("<=", last_record_to_keep[0].modified),
    "user": user
})

frappe.db.delete("Error Log")
frappe.db.delete("__Test Table")

You may pass the doctype name or an internal table name. Conventionally, internal tables in Frappe are prefixed with __. The API follows this. The above commands run an unconditional DELETE query over tables tabError Log and __Test Table.

frappe.db.truncate 
frappe.db.truncate(doctype)

Truncate a table in the database. This runs a DDL command TRUNCATE TABLE, a commit is triggered before the statement is executed. This action cannot be rolled back. You may want to use this for clearing out log tables periodically.

frappe.db.truncate("Error Log")
frappe.db.truncate("__Test Table")

The above commands run a TRUNCATE query over tables tabError Log and __Test Table.

frappe.db.commit 
frappe.db.commit()

Commits current transaction. Calls SQL COMMIT.

In most cases you don't need to commit manually. Refer Frappe's Database transaction model below.

frappe.db.savepoint 
frappe.db.savepoint(save_point)

Create a named savepoint to which you can later roll back to.

frappe.db.rollback 
frappe.db.rollback()

Rollbacks current transaction. Calls SQL ROLLBACK.

Frappe will automatically run frappe.db.rollback() if an exception is thrown during a Web Request of type POST or PUT. Use this if you have to rollback early in a transaction.

frappe.db.rollback(save_point="save_point_name")

Rollback to a specific savepoint instead rolling back full transactions. This rollback won't undo changes done to filesytem and any other rollback watchers.

frappe.db.sql 
frappe.db.sql(query, values, as_dict)

Execute an arbitrary SQL query. This may be useful for complex server side reports with join statements, adjusting the database to new features, etc.

Example:

values = {'company': 'Frappe Technologies Inc'}
data = frappe.db.sql("""
    SELECT
        acc.account_number
        gl.debit
        gl.credit
    FROM `tabGL Entry` gl
        LEFT JOIN `tabAccount` acc
        ON gl.account = acc.name
    WHERE gl.company = %(company)s
""", values=values, as_dict=0)

Avoid using this method as it will bypass validations and integrity checks. It's always better to use frappe.get_doc, frappe.db.get_list, etc., if possible.

frappe.db.multisql 
frappe.db.multisql({'mariadb': mariadb_query, 'postgres': postgres_query})

Execute the suitable SQL statement for any supported database engine.

frappe.db.rename_table 
frappe.db.rename_table(old_name, new_name)

Executes a query to change table name. Specify the DocType or internal table's name directly to rename the table.

Example:

frappe.db.rename_table("__internal_cache", "__temporary_cache")
frappe.db.rename_table("todo", "ToDo")

The second example should be used only if you understand the ramifications of it.

Don't use this to rename DocType tables. Use frappe.rename_doc for that instead

frappe.db.describe 
frappe.db.describe(doctype)

Returns a tuple of the table description for given DocType.

frappe.db.change_column_type 
frappe.db.change_column_type(doctype, column, new_type)

Changes the type of column for specified DocType.

frappe.db.add_index 
frappe.db.add_index(doctype, fields, index_name)

Creates indexes for doctypes for the specified fields.

Note: if you want an index on a TEXT or a BLOB field, you must specify a fixed length to do that.

Example:

frappe.db.add_index("Notes", ["id(10)", "content(500)"], index_name)

frappe.db.add_unique 
frappe.db.add_unique(doctype, fields, constraint_name=None)

Creates unique constraint for doctypes for the specified fields.

Example:

frappe.db.add_unique("DoctypeName",["field1","field2"])

Database transaction hooks 
Frappe provides hooks for running callbacks before/after transaction commands like commit/rollback are issued. These hooks are useful for:

Rolling back changes that are done outside of the database if the transaction is rolled back
Flushing changes outside of the database only if the transaction is committed.
These hooks are :

frappe.db.before_commit.add(func: Callable)
frappe.db.after_commit.add(func: Callable)
frappe.db.before_rollback.add(func: Callable)
frappe.db.after_rollback.add(func: Callable)
Example usage:

def create_file(self):
    self.write_file()
    # This ensures rollback if DB transaction is rolledback
    frappe.db.after_rollback.add(self.rollback_file)

def rollback_file(self):
    self.delete_file()
Database transaction model 
Frappe's database abstractions implement a sane transaction model by default. So in most cases, you won't have to deal with SQL transactions manually. A broad description of this model is described below:

Web requests 
While performing POST or PUT, if any writes were made to the database, they are committed at end of the successful request.
AJAX calls made using frappe.call are POST by default unless changed.
GET requests do not cause an implicit commit.
Any uncaught exception during handling of request will rollback the transaction.
Background/scheduled Jobs 
Calling a function as background or scheduled job will commit the transaction after successful completion.
Any uncaught exception will cause rollback of the transaction.
Patches 
Successful completion of the patch's execute function will commit the transaction automatically.
Any uncaught exception will cause rollback of the transaction.
Unit tests 
Transaction is committed after running one test module. Test module means any python test file like test_core.py.
Transaction is also committed after finishing all tests.
Any uncaught exception will exit the test runner, hence won't commit.
Note: If you're catching exceptions anywhere, then database abstraction does not know that something has gone wrong hence you're responsible for the correct rollback of the transaction.

Jinja API 
These are the whitelisted methods that frappe provides to use them in Jinja Templates.

frappe.format 
frappe.format(value, df, doc)

Formats a raw value (stored in database) to a user presentable format. For example, convert 2019-09-08 to 08-09-2019

Usage

{{ frappe.format('2019-09-08', {'fieldtype': 'Date'}) }}

09-08-2019
frappe.format_date 
frappe.format_date(date_string)

Formats date into a human readable long format.

Usage

{{ frappe.format_date('2019-09-08') }}

September 8, 2019
frappe.get_url 
frappe.get_url()

Returns the site url

Usage

{{ frappe.get_url() }}

https://frappe.io
frappe.get_doc 
frappe.get_doc(doctype, name)

Returns a document by its name.

Usage


 {% set doc = frappe.get_doc('Task', 'TASK00002') %}
 {{ doc.title }} - {{ doc.status }}



 Buy Eggs - Open

frappe.get_all 
frappe.get_all(doctype, filters, fields, order_by, start, page_length, pluck)

Returns a list of all records of a DocType. Only returns the document names if the fields argument is not given.

Signature

frappe.get_all(doctype, filters, fields, order_by, start, page_length)
Usage


 {% set tasks = frappe.get_all('Task', filters={'status': 'Open'}, fields=['title', 'due_date'], order_by='due_date asc') %}
 {% for task in tasks %}

### {{ task.title }}


Due Date: {{ frappe.format_date(task.due_date) }}



 {% endfor %}




### Redesign Website


Due Date: September 8, 2019




### Add meta tags on websites


Due Date: September 22, 2019




frappe.get_list 
frappe.get_list(doctype, filters, fields, order_by, start, page_length)

Similar to frappe.get_all but will filter records for the current session user based on permissions.

frappe.db.get_value 
frappe.db.get_value(doctype, name, fieldname)

Returns a single field value (or a list of values) from a document.

Usage



 {% set company_abbreviation = frappe.db.get_value('Company', 'TennisMart', 'abbr') %}
 {{ company_abbreviation }}


 {% set title, description = frappe.db.get_value('Task', 'TASK00002', ['title', 'description']) %}
 ### {{ title }}


{{ description }}






TM

frappe.db.get\single\value 
frappe.db.get_single_value(doctype, fieldname)

Returns a field value from a Single DocType.

Usage



 {% set timezone = frappe.db.get_single_value('System Settings', 'time_zone') %}
 {{ timezone }}





 Asia/Kolkata


frappe.get\system\settings 
frappe.get_system_settings(fieldname)

Returns a field value from System Settings.

Usage


 {% if frappe.get_system_settings('country') == 'India' %}
 Pay via Razorpay
 {% else %}
 Pay via PayPal
 {% endif %}



Pay via Razorpay

frappe.get_meta 
frappe.get_meta(doctype)

Returns a doctype meta. It contains information like fields, title\_field, image_field, etc.

Usage



 {% set meta = frappe.get_meta('Task') %}
 Task has {{ meta.fields | len }} fields.
 {% if meta.get_field('status') %}
 It also has a Status field.
 {% endif %}





 Task has 18 fields. It also has a Status field.


frappe.get_fullname 
frappe.get_fullname(user_email)

Returns the fullname of the user email passed. If user is not passed, assumes current logged in user.

Usage


The fullname of faris@erpnext.com is {{ frappe.get_fullname('faris@erpnext.com') }}
The current logged in user is {{ frappe.get_fullname() }}



The fullname of faris@erpnext.com is Faris Ansari
The current logged in user is John Doe

frappe.render_template 
frappe.render_template(template_name, context)

Render a jinja template string or file with context.

Usage



 {{ frappe.render_template('templates/includes/footer/footer.html', {}) }}


{{ frappe.render_template('{{ foo }}', {'foo': 'bar'}) }}








bar



frappe._ 
frappe._(string) or _(string)

Usage


{{ _('This string should get translated') }}





इस तार का अनुवाद होना चाहिए



frappe.session.user 
Returns the current session user

frappe.session.csrf_token 
Returns the current session's CSRF token

frappe.form_dict 
If the template is being evaluated in a web request, frappe.form_dict is a dict of query parameters, else it is None.

frappe.lang 
Current language used by the translation function. Two letter, lowercase code.

Request Lifecycle 
The user of a web application can visit different URLs like /about, /posts or /api/resources. Each request is handled based on the following request types.

API requests that start with /api are handled by rest API handler.
File downloads like backups (/backups), public files (/files), and private files (/private/files) are handled separately to respond with a downloadable file.
Web page requests like /about, /posts are handled by the website router. This is explained further on this page.
Learn more about API requests and Static Files in detail.

Request pre-processing 
A few things happen before the routing rules are triggered. These include preprocessing the request initializing the recorder and the rate limiter.

Path Resolver 
Once the request reaches to website router from app.py it is passed through the path resolver.

Path resolver does the following operations:

Redirect Resolution 
Path resolver tries to resolve any possible redirect for an incoming request path. Path resolver gets redirect rules for website_redirects hook and route redirects from website settings.

Route Resolution 
If there are no redirects for incoming requests path resolver tries to resolve the route to get the final endpoint based on rules from website\routing\rules hook and dynamic route set in documents of DocType with has_web_view enabled.

Renderer Selection 
Once the final endpoint is obtained it is passed through all available Page Renderers to check which page renderer can render the given path. A first page renderer to return True for can_render request will be used to render the path.

Page Renderer 
A page renderer takes care of rendering or responding with a page for a given endpoint. A page renderer is implemented using a python class. A page renderer class needs to have two methods i.e., can_render and render.

Path resolver calls can_render to check if a renderer instance can render a particular path. Once a renderer returns True from can_render, it will be that renderer class's responsibility to render the path.

Example page renderer class 
from frappe.website.page_renderers.base_renderer import BaseRenderer

class PageRenderer(BaseRenderer):
 def can_render(self):
 return True

 def render(self):
 response_html = "Response"
 return self.build_response(response_html)

Following are the standard page renderers which handle all the generic types of web pages.

StaticPage 
Using StaticPage you can serve PDFs, images, etc., from the www folder of any app installed on the site. Any file that is not one of the following types html, md, js, xml, css, txt or py is considered to be a static file. The preferred way of serving static files would be to add them to the public folder of your frappe app. That way it will be served by NGINX directly leveraging compression and caching while also reducing latency.

TemplatePage 
The TemplatePage looks up the www folder in all apps, if it is an HTML or markdown file, it is returned, in case it is a folder, the index.html or index.md file in the folder is returned.

WebformPage 
The WebformPage tries to render web form in the Web Form list if the request path matches with any of the available Web Form's routes.

DocumentPage 
The DocumentPage tries to render a document template if it is available in /templates folder of the DocType. The template file name should be the same as the DocType name. Example: If you want to add a document template for User doctype, the templates folder of User DocType should have user.html. The folder structure will look like doctype/user/templates/user.html

ListPage 
If a DocType has a list template in /templates folder of the DocType, the ListPage will render it. Please check Blog Post templates folder for implementation reference.

PrintPage 
The PrintPage renders a print view for a document. It uses standard print format unless a different print format is set for a DocType via default_print_format.

NotFoundPage 
The NotFoundPage renders a standard not found page and responds with 404 status code.

NotPermittedPage 
The NotPermittedPage renders standard permission denied page with 403 status code.

Adding a custom page renderer 
If you have any other requirements which are not handled by Standard Page renderers a custom page renderer can be added via page_renderer [hook]

# in hooks.py of your custom app

page_renderer = "path.to.your.custom_page_renderer.CustomPage"

A Page renderer class needs to have two methods i.e., can_render and render

Path resolver calls can_render to check if a renderer instance can render a particular path. Once a renderer returns True from can_render, it will be that renderer class's responsibility to render the path.

Note: Custom page renderers get priority and it's can_render method will be called before Standard Page Renderers.

Example:


from frappe.website.utils import build_response
from frappe.website.page_renderers.base_renderer import BaseRenderer

class CustomPage(BaseRenderer):
 def can_render(self):
 return True

 def render(self):
 response_html = "Custom Response"
 return self.build_response(response_html)

Note: You can also extend Standard Page Renderers to override or to use some standard functionalities.


Language Resolution 
Here, let's take a look into how language in Frappe is resolved, and how you may be able to use them in your Frappe apps or scripts.

The language for your session depends on the value of frappe.lang. This is resolved in the following order:

Form Dict > _lang
Cookie > preferred\_language _[Guest User only]_
Request Header > Accept-Language _[Guest User only]_
User document > language
System Settings > language
Form Dict: _lang 
The Form Dict's _lang parameter has the highest priority. Setting this will update all translatable components in given request. Frappe uses this mechanism in certain places to handle Email Templates and Print views.

Cookie: preferred_language 
Although, it may not be practical to pass a ?_lang=ru in every request. If you want persistent yet temporary language setting, you can set the preferred_language key in cookies. Frappe utilizes this for the website language switcher. This method may be used to persist language based on the client.

Only considered for Guest Users. Ignored for logged in users.

Request Header: Accept-Language 
Another relatively cleaner, and standard way to manage languages is using the Accept-Language header. If the previous two methods aren't set, Frappe starts resolving this header's values, which have an ordered set of a range of acceptable languages by the client. You can check out the Mozilla Docs on this topic for more clarity perhaps.

Only considered for Guest Users. Ignored for logged in users.

User & System Settings 
The User document has a language field that sets the session language for said user. This setting persists across devices, clients. This allows a particular user to view the website, and Desk in a language of their choice. Say for instance, a user sets their language as "Russian" on a "French" site, when they login, the site would be translated to Russian automatically.

The language field in the System Settings sets the language for the entire site. It has the lowest priority and is the fallback language for all sessions.


Utility Functions 
Frappe Framework comes with various utility functions to handle common operations for managing site-specific DateTime management, date and currency formatting, PDF generation, and much more.

These utility methods can be imported from the frappe.utils module (and its nested modules like frappe.utils.logger and frappe.utils.data) in any Python file of your Frappe App. This list is not at all exhaustive, you can take a peek at the Framework codebase to see what's available.

now 
now()

Returns the current datetime in the format yyyy-mm-dd hh:mm:ss

from frappe.utils import now

now() # '2021-05-25 06:38:52.242515'
getdate 
getdate(string_date=None)

Converts string_date (yyyy-mm-dd) to datetime.date object. If no input is provided, current date is returned. Throws an exception if string_date is an invalid date string.

from frappe.utils import getdate

getdate() # datetime.date(2021, 5, 25)
getdate('2000-03-18') # datetime.date(2000, 3, 18)
today 
today()

Returns current date in the format yyyy-mm-dd.

from frappe.utils import today

today() # '2021-05-25'
add\to\date 
add_to_date(date, years=0, months=0, weeks=0, days=0, hours=0, minutes=0, seconds=0, as_string=False, as_datetime=False)

`date`: A string representation or `datetime` object, uses the current `datetime` if `None` is passed
`as_string`: Return as string
`as_datetime`: If `as_string` is True and `as_datetime` is also True, returns a `datetime` string otherwise just the `date` string.
This function can be quite handy for doing date/datetime deltas, for instance, adding or substracting certain number of days from a particular date/datetime.

from datetime import datetime # from python std library
from frappe.utils import add_to_date

today = datetime.now().strftime('%Y-%m-%d')
print(today) # '2021-05-21'

after_10_days = add_to_date(datetime.now(), days=10, as_string=True)
print(after_10_days) # '2021-05-31'

add_to_date(datetime.now(), months=2) # datetime.datetime(2021, 7, 21, 15, 31, 18, 119999)
add_to_date(datetime.now(), days=10, as_string=True, as_datetime=True) # '2021-05-31 15:30:23.757661'
add_to_date(None, years=6) # datetime.datetime(2027, 5, 21, 15, 32, 31, 652089)
pretty_date 
pretty_date(iso_datetime)

Takes an ISO time and returns a string representing how long ago the date represents. Very common in communication applications like instant messengers.

from frappe.utils import pretty_date, now, add_to_date

pretty_date(now()) # 'just now'

# Some example outputs:

# 1 hour ago
# 20 minutes ago
# 1 week ago
# 5 years ago
format_duration 
format_duration(seconds, hide_days=False)

Converts the given duration value in seconds (float) to duration format.

from frappe.utils import format_duration

format_duration(50) # '50s'
format_duration(10000) # '2h 46m 40s'
format_duration(1000000) # '11d 13h 46m 40s'

# Convert days to hours
format_duration(1000000, hide_days=True) # '277h 46m 40s'
comma_and 
comma_and(some_list, add_quotes=True)

Given a list or tuple some_list, returns a string of the format 1st item, 2nd item, .... and last item. This function uses frappe._, so you don't have to worry about the translations for the word and. If add_quotes is False, returns the items without quotes, with quotes otherwise. If the type of some_list passed as an argument is something other than a list or tuple, it (some_list) is returned as it is.

from frappe.utils import comma_and

comma_and([1, 2, 3]) # "'1', '2' and '3'"
comma_and(['Apple', 'Ball', 'Cat'], add_quotes=False) # 'Apple, Ball and Cat'
comma_and('abcd') # 'abcd'
There is also a comma_or function which is similar to comma_and except the separator, which is or in the case of comma_or.

money\in\words 
money_in_words(number, main_currency=None, fraction_currency=None)

`number`: A floating point money amount
`main_currency`: Uses this as the main currency. If not given, tries to fetch from default settings or uses `INR` if not found there.
This function returns string in words with currency and fraction currency.

from frappe.utils import money_in_words

money_in_words(900) # 'INR Nine Hundred and Fifty Paisa only.'
money_in_words(900.50) # 'INR Nine Hundred and Fifty Paisa only.'
money_in_words(900.50, 'USD') # 'USD Nine Hundred and Fifty Centavo only.'
money_in_words(900.50, 'USD', 'Cents') # 'USD Nine Hundred and Fifty Cents only.'
validate\json\string 
validate_json_string(string)

Raises frappe.ValidationError if the given string is a valid JSON (JavaScript Object Notation) string. You can use a try-except block to handle a call to this function as shown the code snippet below.

import frappe
from frappe.utils import validate_json_string

# No Exception thrown
validate_json_string('[]')
validate_json_string('[{}]')
validate_json_string('[{"player": "one", "score": 199}]')

try:
 # Throws frappe.ValidationError
 validate_json_string('invalid json')
except frappe.ValidationError:
 print('Not a valid JSON string')
random_string 
random_string(length)

This function generates a random string containing length number of characters. This can be useful for cryptographic or secret generation for some cases.

from frappe.utils import random_string

random_string(40) # 'mcrLCrlvkUdkaOe8m5xMI8IwDB8lszwJsWtZFveQ'
random_string(6) # 'htrB4L'
random_string(6) #'HNRirG'
unique 
unique(seq)

seq: An iterable / Sequence

This function returns a list of elements of the given sequence after removing the duplicates. Also, preserves the order, unlike: list(set(seq)).

from frappe.utils import unique

unique([1, 2, 3, 1, 1, 1]) # [1, 2, 3]
unique('abcda') # ['a', 'b', 'c', 'd']
unique(('Apple', 'Apple', 'Banana', 'Apple')) # ['Apple', 'Banana']
get_pdf 
get_pdf(html, options=None, output=None)

`html`: HTML string to render
`options`: An optional `dict` for configuration
`output`: A optional `PdfFileWriter` object.
This function uses pdfkit and pyPDF2 modules to generate PDF files from HTML. If output is provided, appends the generated pages to this object and returns it, otherwise returns a byte stream of the PDF.

For instance, generating and returning a PDF as response to a web request:

import frappe
from frappe.utils.pdf import get_pdf

@frappe.whitelist(allow_guest=True)
def generate_invoice():
 cart = [{
 'Samsung Galaxy S20': 10,
 'iPhone 13': 80
 }]

 html = 'Invoice from Star Electronics e-Store!
======================================

'

 # Add items to PDF HTML
 html += ''
 for item, qty in cart.items():
 html += f'2. {item} - {qty}
'
 html += '
'

 # Attaching PDF to response
 frappe.local.response.filename = 'invoice.pdf'
 frappe.local.response.filecontent = get_pdf(html)
 frappe.local.response.type = 'pdf'
get_abbr 
get_abbr(string, max_len=2)

Returns an abbrivated (initials only) version of the given string with a maximum of max_len letters. It is extensively used in Frappe Framework and ERPNext to generate thumbnail or placeholder images.

from frappe.utils import get_abbr

get_abbr('Gavin') # 'G'
get_abbr('Coca Cola Company') # 'CC'
get_abbr('Mohammad Hussain Nagaria', max_len=3) # 'MHN'
validate_url 
validate_url(txt, throw=False, valid_schemes=None)

`txt`: A string to check validity
`throw`: Weather to throw an exception if `txt` does not represent a valid URL, `False` by default
`valid_schemes`: A string or an iterable (list, tuple or set). If provided, checks the given URL's scheme against this.
This utility function can be used to check if a string represents a valid URL address.

from frappe.utils import validate_url

validate_url('google') # False
validate_url('https://google.com') # True
validate_url('https://google.com', throw=True) # throws ValidationError
validate\email\address 
validate_email_address(email_str, throw=False)

Returns a string containing the email address or comma-separated list of valid email addresses present in the given email_str. If throw is True, frappe.InvalidEmailAddressError is thrown in case of no valid email address in present in the given string else an empty string is returned.

from frappe.utils import validate_email_address

# Single valid email address
validate_email_address('rushabh@erpnext.com') # 'rushabh@erpnext.com'
validate_email_address('other text, rushabh@erpnext.com, some other text') # 'rushabh@erpnext.com'

# Multiple valid email address
validate_email_address(
 'some text, rushabh@erpnext.com, some other text, faris@erpnext.com, yet another no-emailic phrase.'
) # 'rushabh@erpnext.com, faris@erpnext.com'

# Invalid email address
validate_email_address('some other text') # ''
validate\phone\number 
validate_phone_number(phone_number, throw=False)

Returns True if phone_number (string) is a valid phone number. If phone_number is invalid and throw is True, frappe.InvalidPhoneNumberError is thrown.

from frappe.utils import validate_phone_number

# Valid phone numbers
validate_phone_number('753858375') # True
validate_phone_number('+91-75385837') # True

# Invalid phone numbers
validate_phone_number('invalid') # False
validate_phone_number('87345%%', throw=True) # InvalidPhoneNumberError
frappe.cache() 
cache()

Returns the redis connection, which is an instance of class RedisWrapper which is inherited from the redis.Redis class. You can use this connection to use the Redis cache to store/retrieve key-value pairs.

import frappe

cache = frappe.cache()

cache.set('name', 'frappe') # True
cache.get('name') # b'frappe'
frappe.sendmail() 
sendmail(recipients=[], sender="", subject="No Subject", message="No Message", as_markdown=False, template=None, args=None, **kwargs)

`recipients`: List of recipients
`sender`: Email sender. Default is current user or default outgoing account
`subject`: Email Subject
`message`: (or `content`) Email Content
`as_markdown`: Convert content markdown to HTML
`template`: Name of html template (jinja) from templates/emails folder
`args`: Arguments for rendering the template
For most cases, the above arguments are sufficient but there are many other keyword arguments that can be passed to this function. To see all the keyword arguments, please have a look the implementation of this function (frappe/__init__.py).

This function can be used to send email using user's default Email Account or global default Email Account.

import frappe

recipients = [
 'gavin@erpnext.com',
 'hussain@erpnext.com'
]

frappe.sendmail(
 recipients=recipients,
 subject=frappe._('Birthday Reminder'),
 template='birthday_reminder',
 args=dict(
 reminder_text=reminder_text,
 birthday_persons=birthday_persons,
 message=message,
 ),
 header=_('Birthday Reminder 🎂')
)
Sample Jinja template file:





 {% for person in birthday_persons %}
 {% if person.image %}
 ![]({{ person.image }} "{{ person.name }}")
 {% endif %}
 {% endfor %}


{{ reminder_text }}
{{ message }}




Attaching Files 
You can easily attach files to your email by passing a list of attachments to the sendmail function:

frappe.sendmail(
 ["faris@frappe.io", "hussain@frappe.io"],
 message="## hello, *bro*"
 attachments=[{"file_url": "/files/hello.png"}],
 as_markdown=True
)
Notice how attachments are a list of dictionaries having a key file_url. You can find this file_url in a File document's file_url field.

filelock 
File lock can be used to synchronize processes to avoid race conditions.

Example: Writing to a file can cause race condition if multiple writers are trying to write to a file. So we create a named lock so processes can see the lock and wait until it's avialable for writing.

from frappe.utils.synchronization import filelock

def update_important_config(config, file):
 with filelock("config_name"):
 json.dumps(config, file)
Responses 
Here, let's take a look into how responses are built in Frappe, and how you may be able to use them in your Frappe apps or scripts.

If you have already gone through the Router Documentation, you might've noticed the build_response function that Frappe internally utilizes to build responses depending on the type of the content. The logic that defines this behaviour is a part of the module frappe.utils.response, of which build_response is the meat and potatoes.

def build_response(response_type=None):
 if "docs" in frappe.local.response and not frappe.local.response.docs:
 del frappe.local.response["docs"]

 response_type_map = {
 "csv": as_csv,
 "txt": as_txt,
 "download": as_raw,
 "json": as_json,
 "pdf": as_pdf,
 "page": as_page,
 "redirect": redirect,
 "binary": as_binary,
 }

 return response_type_map[frappe.response.get("type") or response_type]()
The above snippet represents the current implementation of build_response which maps different functions that act as handlers for different content types. Let's take a deeper look into the response handler for the "download" response_type in Frappe v13.

def as_raw():
 response = Response()
 response.mimetype = (
 frappe.response.get("content_type")
 or mimetypes.guess_type(frappe.response["filename"])[0]
 or "application/unknown"
 )
 response.headers["Content-Disposition"] = (
 f'{frappe.response.get("display_content_as", "attachment")};'
 f' filename="{frappe.response["filename"].replace(" ", "_")}"'
 ).encode("utf-8")
 response.data = frappe.response["filecontent"]
 return response
Depending on the value of the Content-Disposition header, the browser receiving the response may behave differently. If unset, the value defaults to "attachment".

If frappe.response.display_content_as is set to "inline", it indicates that the content is expected to be displayed inline in the browser, that is, as a Web page or as part of a Web page, while "attachment" means the contents are to be downloaded and saved locally.

To create an API endpoint that would directly download the file you require, you could craft something like the following to download the file directly.

@frappe.whitelist(allow_guest=False)
def download(name):
 file = frappe.get_doc("File", name)
 frappe.response.filename = file.file_name
 frappe.response.filecontent = file.get_content()
 frappe.response.type = "download"
 frappe.response.display_content_as = "attachment"

Search 
Searching in Frappe is managed by the Search module. It is a wrapper for Whoosh a full text search library written in Python.

You can extend the FullTextSearch class to create a search class for a specific requirement. For example the WebsiteSearch is a wrapper for indexing public facing web pages and exposing a search.

The FullTextSearch class 
Each FullTextSearch (FTS) instance holds a Schema defined by the class itself. That means, a specific FTS implementation will have it's specific schema. You can create a new implementation if you wish to index with a different schema. Along with this the FTS class has other controllers to facilitate creating, updating and querying the index.

Extending the FTS class 
When initializing a FTS based class, you need to provide an index name. On instantiation, the following params are initialized - index_name: name of the index provided. - index_path: path of the index in the sites folder - schema: return by the get_schema function - id: id used to recognize the document in the index

Once instantiated you can run the build function. It gets all the documents from get_items_to_index, the documents are a list of frappe._dict (frappe dicts) conforming to the defined schema. These documents are then added to the index and written to the file.

You can search the index using the search method of the FTS class. These functions are documented in the API reference here.

An example implementation for blog will look like the following:

class BlogWrapper(FullTextSearch):
 # Default Schema
 # def get_schema(self):
 # return Schema(name=ID(stored=True), content=TEXT(stored=True))

 # def get_id(self):
 # return "name"

 def get_items_to_index(self):
 docs = []
 for blog_name in get_all_blogs():
 docs.append(get_document_to_index(blog_name))
 return docs

 def get_document_to_index(self, name):
 blog = frappe.get_doc("Blog Post", name)
 return frappe._dict(name=name, content=blog.content)

 def parse_result(self, result):
 return result["name"]
get_items_to_index: Get all routes to be indexed, this includes the static pages in www/ and routes from published documents
get_document_to_index: Render a page and parse it using BeautifulSoup
parse_result: all the search results are parsed using this function

Hooks 
Hooks allow you to "hook" into functionality and events of core parts of the Frappe Framework. This page documents all of the hooks provided by the framework.

Jump to list of all available hooks in Frappe.

How does hooks work? 
Hooks are places in the core code that allow an app to override the standard implementation or extend it. Hooks are defined in hooks.py of your app.

Let's learn by example. Add the following hooks in your app's hooks.py.

test_string = "value"
test_list = ["value"]
test_dict = {
 "key": "value"
}
Now, open the python console by running the command bench --site sitename console and run the following lines:

❯ bench --site sitename console
Apps in this namespace:
frappe, frappe_docs

In [1]: frappe.get_hooks("test_string")
Out[1]: ["value"]

In [2]: frappe.get_hooks("test_dict")
Out[2]: {"key": ["value"]}

In [3]: frappe.get_hooks("test_list")
Out[3]: ["value"]
When you call frappe.get_hooks, it will convert all the values in a list. This means that if the hook is defined in multiple apps, the values will be collected from those apps. This is what enables the cascading nature of hooks.

Now, the hook value can be consumed in different ways. For example, for including JS assets using app_include_js, all of the values are included. But for overriding whitelisted method, the last value in the list is used.

So the implementation of the hook is totally dependent on how the author of the feature intended it to be used.

How are conflicting hooks resolved? 
Hooks are resolved using "last writer wins" strategy. Last installed app on site will have highest priority over others.

When the hook overrides existing behaviour like overriding a class then only overrides from last app will work.
When the hook extends behaviour then extensions will be applied in order of installation on the site.
If you need to change this order you can do so by going to "Installed Applications" page and clicking on "Update Hooks Resolution Order"

App Meta Data 
These are automatically generated when you create a new app. Most of the time you don't need to change anything here.

app_name - slugified name of the app
app_title - presentable app name
app_publisher
app_description
app_version
app_icon
app_color
Javascript / CSS Assets 
The following hooks allow you to inject static JS and CSS assets in various parts of your site.

Desk 
These hooks allow you to inject JS / CSS in desk.html which renders the Desk.

# injected in desk.html
app_include_js = "assets/js/app.min.js"
app_include_css = "assets/js/app.min.css"

# All of the above support a list of paths too
app_include_js = ["assets/js/app1.min.js", "assets/js/app2.min.js"]
Portal 
These hooks allow you to inject JS / CSS in web.html which renders the Portal.

# injected in the web.html
web_include_js = "assets/js/app-web.min.js"
web_include_css = "assets/js/app-web.min.css"
# All of the above support a list of paths too
web_include_js = ["assets/js/web1.min.js", "assets/js/web2.min.js"]
Web Form 
These hooks allow you to add inject static JS and CSS assets in web_form.html which is used to render Web Forms. These will work only for Standard Web Forms.

webform_include_js = {"ToDo": "public/js/custom_todo.js"}
webform_include_css = {"ToDo": "public/css/custom_todo.css"}
For user created Web Forms, you can directly write the script in the form itself.

Page 
These hooks allow you to inject JS assets in Standard Desk Pages.

page_js = {"page_name" : "public/js/file.js"}
For e.g., Background Jobs is a standard page that is part of Core module in Frappe Framework. To add custom behaviour in that page you can add a JS file in your custom app custom_app/public/js/custom_background_jobs.js and add the following line in your hooks file.

custom_app/hooks.py

page_js = {"background_jobs": "public/js/custom_background_jobs.js"}
Sounds 
Frappe ships with a set of audio notifications for events like a success action, document submission, error, etc. You can add your own sounds using the sounds hook.

app/hooks.py

sounds = [
 {"name": "ping", "src": "/assets/app/sounds/ping.mp3", "volume": 0.2}
]
You can play your added sound using the client utility method:

frappe.utils.play_sound("ping")
Install Hooks 
These hooks allow you to run code before and after installation of your app. For example, ERPNext has these defined.

# python module path
before_install = "app.setup.install.before_install"
after_install = "app.setup.install.after_install"
after_sync = "app.setup.install.after_sync"
app/setup/install.py

# will run before app is installed on site
def before_install():
 pass

# will run after app is installed on site
def after_install():
 pass

# will run after app fixtures are synced
def after_sync():
 pass
Uninstall Hooks 
These hooks allow you to run code before and after uninstallation of your app.

app/hooks.py

before_uninstall = "app.setup.uninstall.before_uninstall"
after_uninstall = "app.setup.uninstall.after_uninstall"
app/setup/uninstall.py

# will run before app is uninstalled from site
def before_uninstall():
 pass

# will run after app is uninstalled from site
def after_uninstall():
 pass
Migrate Hooks 
These hooks allow you to run code before and after a migration is run on your site via the command bench --site sitename migrate.

app/hooks.py

before_migrate = "app.migrate.before_migrate"
after_migrate = "app.migrate.after_migrate"
app/migrate.py

def after_migrate():
 # run code after site migration
 pass
Test Hooks 
This hook allows you to run code before tests are run on a site. You can use this hook to add seed data to your database which will be available to your tests.

app/hooks.py

before_tests = "app.tests.before_tests"
app/migrate.py

def before_tests():
 # add seed data to the database
 pass
File Hooks 
These hooks allows you to change the implementation of handling user uploaded files.

app/hooks.py

before_write_file = "app.overrides.file.before_write"
write_file = "app.overrides.file.write_file"
delete_file_data_content = "app.overrides.file.delete_file"
app/overrides/file.py

# will run before file is written to disk
def before_write():
 pass

# will override the implementation of writing file to disk
# can be used to upload files to a CDN instead of writing
# the file to disk
def write_file():
 pass


# will override the implementation of deleting file from disk
# can be used to delete uploaded files from a CDN instead of
# deleting file from disk
def delete_file():
 pass
Email Hooks 
These hooks allows you to change the default email module implementation of sending emails and setting default sender address.

app/hooks.py

override_email_send = "app.overrides.email.send"
get_sender_details = "app.overrides.email.get_sender_details"
By default frappe uses the currently logged in users name and id as sender details on all emails. This can be overriden with get_sender_details hook. And if you want to extend the email modules functionality by using a thirdy party server or app for sending emails then you can use override_email_send hook. This hook will send all the email information (sender, recipient, content(mime)) to a function in custom_app.

app/overrides/email.py

# will be edited as "John Doe "
def get_sender_details():
 return "John Doe", "johndoe@gmail.com"

# self - EmailQueue object refrence for updating status
def send(self, sender, recipient, msg):
 # smtp or http request
 self.update_status("Sending")
Note: You'll have to handle the status change of email queue in your custom app depending on the webhook response you get from your mail provider/server

Extend Bootinfo 
After a successful login, the Desk is injected with a dictionary of global values called bootinfo. The bootinfo is available as a global object in Javascript as frappe.boot.

The bootinfo dict contains a lot of values including:

System defaults
Notification status
Permissions
User settings
Language and timezone info
You can add global values that makes sense for your app via the extend_bootinfo hook.

# python module path
extend_bootinfo = "app.boot.boot_session"
The method is called with one argument bootinfo, on which you can directly add/update values.

app/boot.py

def boot_session(bootinfo):
 bootinfo.my_global_key = "my_global_value"
Now, you can access the value anywhere in your client side code.

console.log(frappe.boot.my_global_key)
Website Context 
When a Portal Page is rendered, a dictionary is built with all of the possible variables that the page might need to render. This dict is also known as context. You can use these hooks to add or modify values in this dict.

app/hooks.py

website_context = {
 "favicon": "/assets/app/image/favicon.png"
}
update_website_context = "app.overrides.website_context"
The website_context hook is a simple dict of key value pairs. Use this hook for simple value overrides.

You can use the update_website_context hook for more complex scenarios as it allows you to manipulate the context dict in a python method. The method is called with one argument, which is the context dict. You can either modify the context directly by mutating it or return a dict that will be merged with context.

app/overrides.py

def website_context(context):
 context.my_key = "my_value"
Website Controller Context 
Frappe ships with standard web pages like /404 and /about. If you want to extend the controller context for these pages you can use the extend_website_page_controller_context hook.

app/hooks.py

extend_website_page_controller_context = {
 "frappe.www.404": "app.pages.context_404"
}
The above hook configuration will allow you to extend the context of the 404 page so that you can add your own keys or modify existing ones.

app/pages.py

def context_404(context):
 # context of the 404 page
 context.my_key = "my_value"
Website Clear Cache 
Frappe Framework caches a lot of static web pages for fast subsequent rendering. If you have created web pages that use cached values, and you want to invalidate the cache, this hook is place to do it.

app/hooks.py

website_clear_cache = "app.overrides.clear_website_cache"
The method is called with one argument path. path is set when cache is being cleared for one route, and is None when cache is cleared for all routes. You need to handle this case if your cache is page specific.

app/overrides.py

def clear_website_cache(path=None):
 if path:
 # clear page related cache
 else:
 # clear all cache
Website Redirects 
Website Redirects allow you to define redirects from one route to another. Frappe will generate a 304 Redirect response when the source URL is requested and redirect to the target URL. You can redirect plain URLs or you can use regex to match your URLs.

app/hooks.py

website_redirects = [
 {"source": "/compare", "target": "/comparison"},
 {"source": "/docs(/.*)?", "target": "https://docs.tennismart.com/\1"},
 {"source": r'/items/item\?item_name=(.*)', "target": '/items/\1', match_with_query_string=True},
]
The above configuration will result in following redirects:

/compare to /comparison
/docs/getting-started to https://docs.tennismart.com/getting-started
/docs/help to https://docs.tennismart.com/help
/items/item?item_name=racket to https://docs.tennismart.com/items/racket
Website Route Rules 
Website Route Rules allow you to map URLs to custom controllers. This is commonly used to generate clean URLs for pages.

Let's say you want to have /projects route to display list of projects. This can be done by creating a projects.html and projects.py in www folder.

You also want to have /project/ route to show a project page where name is the dynamic. To do this you can use the website_route_rules hook.

app/hooks.py

website_route_rules = [
 {"from_route": "/projects/", "to_route": "app/projects/project"},
]
Now, you can create your controller files in app/projects folder.

app/projects/project.py

def get_context(context):
 project_name = frappe.form_dict.name
 project = frappe.get_doc("Project", project_name)
 context.project = project
app/projects/project.html

{{ project.title }}
===================


{{ project.description }}


Website 404 
Frappe renders a default /404 route when a page is not found. You can change this using the website_catch_all hook.

app/hooks.py

website_catch_all = "not_found"
The above configuration will render /not_found when a 404 is occurred. It is upto you to implement the template www/not_found.html and controller www/not_found.py.

Default Homepage 
Homepage is the page which is rendered when you visit the root URL (/) of your site. There are multiple ways to configure what page is rendered as the default homepage.

By default, the homepage is index. So, frappe will try to render index.html from www folder. This can be overridden using the homepage hook.

app/hooks.py

homepage = "homepage"
The above configuration will load the www/homepage.html as the default homepage.

You can also have role based homepage by using the role_home_page hook.

app/hooks.py

role_home_page = {
 "Customer": "orders",
 "Supplier": "bills"
}
The above configuration will make /orders the default homepage for users with the Customer role and /bills for users with the Supplier role.

You can have even more control over the logic by using the get_website_user_home_page hook.

app/hooks.py

get_website_user_home_page = "app.website.get_home_page"
app/website.py

def get_home_page(user):
 if is_projects_user(user):
 return "projects"
 if is_partner(user):
 return "partner-dashboard"
 return "index"
If all of these hooks are defined, the get_website_user_home_page will have higher priority over the others, and role_home_page will have higher priority over homepage.

Portal Sidebar 
Some Portal views are shown with a sidebar with links to quickly jump to pages. These sidebar items can be customized via hooks.

app/hooks.py

portal_menu_items = [
 {"title": "Dashboard", "route": "/dashboard", "role": "Customer"},
 {"title": "Orders", "route": "/orders", "role": "Customer"},
]
The above configuration will add two sidebar links for users with the role Customer.

Portal Sidebar

These sidebar items are hardcoded in your app so they are not customizable from Desk. For e.g., if you want to hide a sidebar link temporarily you will have to make changes in your code.

There is another hook called standard_portal_menu_items which allows you to do that. The sidebar links set in standard_portal_menu_items hook will be synced with the database.

app/hooks.py

standard_portal_menu_items = [
 {"title": "Dashboard", "route": "/dashboard", "role": "Website Manager"},
 {"title": "Orders", "route": "/orders", "role": "Website Manager"},
]
The above configuration will sync sidebar items to the Portal Settings which can later be edited by any System User.

Portal Settings

Brand HTML 
This hook allows you to customize the brand logo in the navbar of your website.

app/hooks.py

brand_html = '![](tennismart.png) TennisMart'
If the brand_html is defined, it will override the default brand html in the navbar. It is not recommended to use hooks to change your brand logo, unless you want to version control it, otherwise you can use Website Settings to change it.

Base Template 
When a web page is rendered, it extends templates/base.html by default. You can override the base template by overriding the base_template hook.

app/hooks.py

base_template = "app/templates/my_custom_base.html"
You can also customize base templates based on routes. For e.g., if you want to use a different base template for all the routes that start with docs/* then you can use the base_template_map hook. The key must be a regex that matches the route. All other routes will fallback to the default base template.

app/hooks.py

base_template_map = {
 r"docs.*": "app/templates/doc_template.html"
}
Integrations 
These hooks allow you to customize behaviour of 3rd-party integrations in Frappe.

Braintree Success Page 
This hook allows you to override the default redirect URL on successful payment of Braintree transaction.

app/hooks.py

braintree_success_page = "app.integrations.braintree_success_page"
The method is called with one argument data which has the meta data of the payment.

app/integrations.py

def braintree_success_page(data):
 # data.reference_doctype
 # data.reference_docname
 return "/thank-you"
Calendars 
The calendar hook is a list of doctype names which are shown as menu items for quick navigation from the Calendar page in Desk.

app/hooks.py

calendars = ["Appointment"]
Event Menu Shortcuts

Clear Cache 
This hook allows you to clear your app specific cache values when the global cache is being cleared by frappe.

app/hooks.py

clear_cache = "app.cache.clear_cache"
You can use this hook to clear your app specific cache. The method is called without any arguments.

app/cache.py

def clear_cache():
 frappe.cache().hdel("app_specific_cache")
Default Mail Footer 
If you want to set the default footer of all the emails that are sent out by Frappe, you can use the default_mail_footer hook.

app/hooks.py

default_mail_footer = """

 Sent via [TennisMart](https://tennismart.com)

"""
Now, all the emails will have Sent via TennisMart in the footer.

Session Hooks 
These hooks are triggered over the login lifecycle of a user. on_login is triggered immediately after a successful login, on_session_creation is triggered after the session is setup, on_logout is triggered after the user logs out.

app/hooks.py

on_login = "app.overrides.successful_login"
on_session_creation = "app.overrides.allocate_free_credits"
on_logout = "app.overrides.clear_user_cache"
The method will be called with one argument login_manager.

app/overrides.py

def allocate_free_credits(login_manager):
 # allocate free credits to frappe.session.user
 pass
Auth Hooks 
These hooks are triggered during request authentication. Custom headers, Authorization headers can be validated here, user is verified and mapped to the request using frappe.set_user(). Use frappe.request and frappe.* to validate request and map user.

app/hooks.py

auth_hooks = ["app.overrides.validate_custom_jwt"]
The method will be called during request authentication.

app/overrides.py

def validate_custom_jwt():
 # validate jwt from header, verify signature, set user from jwt.
 pass
Use this method to check for incoming request header, verify the header and map the user to the request. If header verification fails DO NOT throw error to continue with other hooks. Unverified request is treated as "Guest" request by default. You may use third party server, shared database or any alternative of choice to verify and map request and user.

Fixtures 
Fixtures are database records that are synced using JSON files when you install and update your site.

Let's say you want to create a set of categories in the database whenever you install your app. To do that, create the set of categories in your local site, and add the doctype name in the fixtures hook.

fixtures = [
 # export all records from the Category table
 "Category"
]
Now, run the following command:

bench --site sitename export-fixtures
This command will create a JSON file for each doctype which will contain the data to generate list of records. You can test this by creating a new site and by installing your app on that site.

You can also add conditions for exporting records.

fixtures = [
 # export all records from the Category table
 "Category",
 # export only those records that match the filters from the Role table
 {"dt": "Role", "filters": [["role_name", "like", "Admin%"]]},
]
Some fields are for internal use only. They will be set and kept up-to-date by the system automatically. These will not get exported: modified_by, creation, owner, idx, lft and rgt. For child table records, the following fields will not get exported: docstatus, doctype, modified and name.

Document Hooks 
Modify List Query 
You can customize how list of records are queried for a DocType by adding custom match conditions using the permission_query_conditions hook. This match condition must be a valid WHERE clause fragment for an SQL query.

app/hooks.py

permission_query_conditions = {
 "ToDo": "app.permissions.todo_query",
}
The method is called with a single argument user which can be None. The method should return a string that is a valid SQL WHERE clause.

app/permissions.py

def todo_query(user):
 if not user:
 user = frappe.session.user
 # todos that belong to user or assigned by user
 return "(`tabToDo`.owner = {user} or `tabToDo`.assigned_by = {user})".format(user=frappe.db.escape(user))
Now, if you use the frappe.db.get_list method, your WHERE clause will be appended to the query.

todos = frappe.db.get_list("ToDo", debug=1)

# output
'''
select `tabToDo`.`name`
from `tabToDo`
where ((`tabToDo`.owner = 'john@doe.com' or `tabToDo`.assigned_by = 'john@doe.com'))
order by `tabToDo`.`modified` DESC
'''
This hook will only affect the result of frappe.db.get_list method and not frappe.db.get_all.

Document Permissions 
You can modify the behaviour of doc.has_permission document method for any DocType and add custom permission checking logic using the has_permission hook.

app/hooks.py

has_permission = {
 "Event": "app.permissions.event_has_permission",
}
The method will be passed the doc, user and permission_type as arguments. It should return True or a False value. If None is returned, it will fallback to default behaviour.

app/permissions.py

def event_has_permission(doc, user=None, permission_type=None):
 # when reading a document allow if event is Public
 if permission_type == "read" and doc.event_type == "Public":
 return True

 # when writing a document allow if event owned by user
 if permission_type == "write" and doc.owner == user:
 return True

 return False
Override DocType Class 
You can override/extend the class for standard doctypes by using the override_doctype_class hook.

app/hooks.py

override_doctype_class = {
 "ToDo": "app.overrides.todo.CustomToDo"
}
app/overrides/todo.py

from frappe.desk.doctype.todo.todo import ToDo

class CustomToDo(ToDo):
 def on_update(self):
 self.my_custom_code()
 super().on_update()

 def my_custom_code(self):
 pass
It is recommended that you extend the standard class of the doctype, otherwise you will have to implement all of the core functionality.

Override Form Scripts 
You can override/extend Standard Form Scripts by using the doctype_js hook.

app/hooks.py

doctype_js = {
 "ToDo": "public/js/todo.js",
}
app/public/js/todo.js

frappe.ui.form.on("Todo", {
 refresh: function(frm) {
 frm.trigger("my_custom_code");
 },
 my_custom_code: function(frm){
 console.log(frm.doc.name)
 }
});
The events/functions defined in app/public/todo.js will extend those in the standard form script of ToDo doctype.

CRUD Events 
You can hook into various CRUD events of any doctype using the doc_events hook.

app/hooks.py

doc_events = {
 "*": {
 # will run after any DocType record is inserted into database
 "after_insert": "app.crud_events.after_insert_all"
 },
 "ToDo": {
 # will run before a ToDo record is inserted into database
 "before_insert": "app.crud_events.before_insert_todo",
 }
}
The method will be passed the doc and the method name as arguments.

app/crud_events.py

def after_insert_all(doc, method=None):
 pass

def before_insert_todo(doc, method=None):
 pass
See Controller Hooks for a list of all available hooks.

Override Whitelisted Methods 
Whitelisted Methods are python methods that are accessible on a REST endpoint and consumed by a client. You can override standard whitelisted methods that are part of the core framework using the override_whitelisted_methods hook.

app/hooks.py

override_whitelisted_methods = {
 "frappe.client.get_count": "app.whitelisted.custom_get_count"
}
The method should have the same signature as the original method.

app/whitelisted.py

def custom_get_count(doctype, filters=None, debug=False, cache=False):
 # your custom implementation of the standard get_count method provided by frappe
 pass
Ignore Links on Delete 
To ignore links to specific DocTypes when deleting documents, you can specify them in the ignore_links_on_delete hook like so:

app/hooks.py

ignore_links_on_delete = ["Communication", "ToDo"]
Form Timeline 
The timeline section of form view of a document shows an audit trail of actions performed on that document like views, value changes, comments and related communications, etc.

Apart from these standard actions, there might arise a situation where you need to add your own custom actions. You can do this via additional_timeline_content hook.

additional_timeline_content: {
 # show in each document's timeline
 "*": ["app.timeline.all_timeline"]
 # only show in ToDo's timeline
 "ToDo": ["app.timeline.todo_timeline"]
}
The method will be passed the doctype and docname as arguments. You can perform queries and return actions related to that document as a list of dicts as shown in the example. Each dict in the list must have a creation value which will be used to sort the item in the timeline.

def todo_timeline(doctype, docname):
 # this method should return a list of dicts
 return [
 {
 # this will be used to sort the content in the timeline
 "creation": "22-05-2020 18:00:00",
 # this JS template will be rendered in the timeline
 "template": "custom_timeline_template",
 # this data will be passed to the template.
 "template_data": {"key": "value"},
 },
 ...
 ]
Scheduler Events 
You can use Scheduler Events for running tasks periodically in the background using the scheduler_events hook.

app/hooks.py

scheduler_events = {
 "hourly": [
 # will run hourly
 "app.scheduled_tasks.update_database_usage"
 ],
}
app/scheduled_tasks.py

def update_database_usage():
 pass
After changing any scheduled events in hooks.py, you need to run bench migrate for changes to take effect.

Available Events 
hourly, daily, weekly, monthly

These events will trigger every hour, day, week and month respectively.

hourly_long, daily_long, weekly_long, monthly_long

Same as above but these jobs are run in the long worker suitable for long running jobs.

all

The all event is triggered every 60 seconds. This can be configured via the scheduler_tick_interval key in common_site_config.json

cron

A valid cron string that can be parsed by croniter.

Usage Examples:

scheduler_events = {
 "daily": [
 "app.scheduled_tasks.manage_recurring_invoices"
 ],
 "daily_long": [
 "app.scheduled_tasks..take_backups_daily"
 ],
 "cron": {
 "15 18 * * *": [
 "app.scheduled_tasks..delete_all_barcodes_for_users"
 ],
 "*/6 * * * *": [
 "app.scheduled_tasks..collect_error_snapshots"
 ],
 "annual": [
 "app.scheduled_tasks.collect_error_snapshots"
 ]
 }
}
Jinja Customization 
Frappe provides a list of global utility methods in Jinja templates. To add your own methods and filters you can use the jinja hook.

app/hooks.py

jinja = {
 "methods": [
 "app.jinja.methods",
 "app.utils.get_fullname"
 ],
 "filters": [
 "app.jinja.filters",
 "app.utils.format_currency"
 ]
}
app/jinja/methods.py

def sum(a, b):
 return a + b

def multiply(a, b):
 return a * b
If the path is a module path, all the methods in that module will be added.

app/utils.py

def get_fullname(user):
 first_name, last_name = frappe.db.get_value("User", user, ["first_name", "last_name"])
 return first_name + " " + last_name

def format_currency(value, currency):
 return currency + " " + str(value)
Now, you can use these utilities in your Jinja templates like so:

Hi, {{ get_fullname(frappe.session.user) }}
============================================


Your account balance is {{ account_balance | format_currency("INR") }}


1 + 2 = {{ sum(1, 2) }}


Prevent Auto Cancellation of Linked Documents 
To prevent documents of a specific DocType from being automatically cancelled on the cancellation of any linked documents you can use the auto_cancel_exempted_doctypes hook.

app/hooks.py

auto_cancel_exempted_doctypes = ["Payment Entry"]
In the above example, if any document (for e.g Sales Invoice) that is linked with Payment Entry is cancelled, it will skip the auto-cancellation of the linked Payment Entry document.

Notification configurations 
The notification configuration hook is used to customize the items shown in the Notification dropdown in Desk. It can be configured by the notification_config hook.

app/hooks.py

notification_config = "app.notification.get_config"
The method is called without any arguments.

app/notification.py

def get_config():
 return {
 "for_doctype": {
 "Issue": {"status":"Open"},
 "Issue": {"status":"Open"},
 },
 "for_module_doctypes": {
 "ToDo": "To Do",
 "Event": "Calendar",
 "Comment": "Messages"
 },
 "for_module": {
 "To Do": "frappe.core.notifications.get_things_todo",
 "Calendar": "frappe.core.notifications.get_todays_events",
 "Messages": "frappe.core.notifications.get_unread_messages"
 }
 }
The above configuration has three parts:

for_doctype part of the above configuration marks any "Issue" or "Customer Issue" as unread if its status is Open
for_module_doctypes maps doctypes to module's unread count.
for_module maps modules to functions to obtain its unread count. The functions are called without any argument.
Required Apps 
When building apps, you might create apps that build on top of other apps. To make sure dependent apps are installed when someone installs your app, you can use the required_apps hook.

app/hooks.py

required_apps = ["erpnext"]
The above configuration will make sure erpnext is installed when someone installs your app.

User Data Protection & Privacy 
User Data Privacy features like personal data download and personal data deletion come out of the box in Frappe. What constitutes as personal data may be defined by the App publisher in the application's hooks.py file as user_data_fields.

app/hooks.py

user_data_fields = [
 {"doctype": "Access Log"},
 {"doctype": "Comment", "strict": True},
 {
 "doctype": "Contact",
 "filter_by": "email_id",
 "rename": True,
 },
 {"doctype": "Contact Email", "filter_by": "email_id"},
 {
 "doctype": "File",
 "filter_by": "attached_to_name",
 "redact_fields": ["file_name", "file_url"],
 },
 {"doctype": "Email Unsubscribe", "filter_by": "email", "partial": True},
]
DocTypes that have user data should be mapped under this hook using the above format. Upon data deletion or download requests from users, this hook will be utilized to map over the specified DocTypes. The options available to modify documents are:

Field	Description
doctype	DocType that contains user data.
filter_by	Docfield to filter the documents by. If unset, defaults to owner.
partial	If set, all text fields are parsed and user's full name and username references will be redacted.
redact_fields	Fields that have to be redacted. If unspecified, it considers partial data redaction from all text fields.
rename	If document name contains user data, set this field to rename document to anonymize it.
strict	If set to True, any user data will be redacted from all documents of current DocType. If unset, it defaults to False which means it only filters through documents in which user is the owner.
Note: Personal Data Download only utilizes the doctype and filter_by fields defined in user_data_fields

Related Topics:

Personal Data Deletion
Personal Data Download
Signup Form Template 
If you want to add additional fields to the signup form you can use this hook. Create a template file which contains the custom signup form. Pass this template to the custom signup hook.

signup_form_template = "school/templates/signup-form.html"
Note: If you want custom fields in signup form, it will require additional fields in the user doctype. You will have to add these fields using fixtures. Also you will have to write your own submit handler for this signup form and a function on the server side which will signup the user. This way you can also write validations for the custom fields you add.

List of available hooks 
Hook Name	Explanation
additional_timeline_content	Form Timeline
after_install	Install Hooks
after_migrate	Migrate Hooks
after_sync	Install Hooks
app_include_css	Desk Assets
app_include_js	Desk Assets
app_logo_url	App Meta Data
app_title	App Meta Data
auto_cancel_exempted_doctypes	Prevent Auto Cancellation
base_template_map	Base Template
base_template	Base Template
before_install	Install Hooks
before_migrate	Migrate Hooks
before_tests	Test Hooks
before_write_file	File Hooks
bot_parsers	_Deprecated_
braintree_success_page	Braintree Success Page
brand_html	Brand HTML
calendars	Calendars
clear_cache	Clear Cache
communication_doctypes	
default_mail_footer	Default Mail Footer
delete_file_data_content	File Hooks
doc_events	Document CRUD Events
doctype_js	Override Form Scripts
domains	
dump_report_map	_Deprecated_
extend_bootinfo	Extend Bootinfo
extend_website_page_controller_context	Website Controller Context
filters_config	
fixtures	Fixtures
get_site_info	
get_translated_dict	
get_website_user_home_page	Default Homepage
has_permission	Document Permissions
has_website_permission	
home_page	Default Homepage
jenv	Jinja Customization
leaderboards	
look_for_sidebar_json	
make_email_body_message	
notification_config	Notification configuration
on_login	Session Hooks
on_logout	Session Hooks
on_session_creation	Session Hooks
override_doctype_class	Override DocType Class
override_doctype_dashboards	
override_whitelisted_methods	Override Whitelisted Methods
ignore_links_on_delete	Ignore Links on Delete
permission_query_conditions	Modify List Query
portal_menu_items	Portal Sidebar
required_apps	Required Apps
role_home_page	Default Homepage
scheduler_events	Scheduler Events
setup_wizard_complete	
setup_wizard_exception	
setup_wizard_requires	
setup_wizard_stages	
setup_wizard_success	
signup_form_template	Signup Form Template
sounds	Sounds
standard_portal_menu_items	Portal Sidebar
standard_queries	
template_apps	
translated_languages_for_website	
translator_url	
treeviews	DocTypes that use TreeView as the default view (instead of ListView)
update_website_context	Website Context
user_privacy_documents	_Deprecated_ (Use user_data_fields hook)
user_data_fields	User Data Protection & Privacy
web_include_css	Portal Assets
web_include_js	Portal Assets
website_catch_all	Website 404
website_clear_cache	Website Clear Cache
website_context	Website Context
website_generators	_Deprecated_ (Use Has Web View in DocType instead)
website_redirects	Website Redirects
website_route_rules	Website Route Rules
website_user_home_page	_Deprecated_ (Use homepage hook)
welcome_email	
write_file_keys	_Deprecated_
write_file	File Hooks
