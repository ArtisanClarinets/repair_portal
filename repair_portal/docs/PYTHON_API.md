# Frappe Python API Reference

This document provides an in-depth reference of Frappe’s Python APIs, including Realtime Events, Background Jobs, Document APIs, Database APIs, Request Lifecycle, Utility Functions, and Hooks.

---

## Realtime (socket.io)

**Publish Realtime Events**
```python
frappe.publish_realtime('event_name', data={'key': 'value'})
```

**Publish Progress**
```python
frappe.publish_progress(25, title='Some title', description='Some description')
```

**Client-Side Listeners**
In JS:
```javascript
frappe.realtime.on('event_name', data => {
    console.log(data);
})
frappe.realtime.off('event_name');
```

---

## Background Jobs

**Enqueue a Function:**
```python
def long_running_job(param1, param2):
    # expensive tasks
    pass

frappe.enqueue(long_running_job, queue='short', param1='A', param2='B')
```

**Enqueue by Path:**
```python
frappe.enqueue('app.module.folder.long_running_job', queue='short', param1='A', param2='B')
```

**Enqueue Document Method:**
```python
frappe.enqueue_doc(
    doctype,
    name,
    'do_something',
    queue='long',
    timeout=4000,
    param='value'
)
```

---

## Document API

**Get Document:**
```python
doc = frappe.get_doc('Task', 'TASK00002')
```

**New Document:**
```python
doc = frappe.get_doc({
    'doctype': 'Task',
    'title': 'New Task'
})
doc.insert()
```

**Delete Document:**
```python
frappe.delete_doc('Task', 'TASK00002')
```

**Rename Document:**
```python
frappe.rename_doc('Task', 'OldName', 'NewName')
```

**Get Last Document:**
```python
task = frappe.get_last_doc('Task')
```

**Get Cached Doc:**
```python
doc = frappe.get_cached_doc('Task', 'TASK00002')
```

**Save Document:**
```python
doc.save()
```

**Reload Document:**
```python
doc.reload()
```

**Append Child Row:**
```python
doc.append('items', {'item_code': 'X', 'qty': 1})
```

**Add Comment:**
```python
doc.add_comment('Comment', text='Test comment')
```

**Run Background Method:**
```python
doc.queue_action('send_email', recipients=['a@example.com'])
```

---

## Database API

**Get List:**
```python
frappe.db.get_list('Task', filters={'status': 'Open'}, fields=['name', 'status'])
```

**Get All (ignore permissions):**
```python
frappe.db.get_all('Task')
```

**Get Value:**
```python
subject = frappe.db.get_value('Task', 'TASK00002', 'subject')
```

**Set Value:**
```python
frappe.db.set_value('Task', 'TASK00002', 'status', 'Closed')
```

**Exists:**
```python
frappe.db.exists('Task', 'TASK00002')
```

**Count:**
```python
count = frappe.db.count('Task', {'status': 'Open'})
```

**Delete Records:**
```python
frappe.db.delete('Task', {'status': 'Cancelled'})
```

**SQL Query:**
```python
frappe.db.sql("SELECT name FROM `tabTask`")
```

---

## Utility Functions

**Get Date:**
```python
from frappe.utils import getdate
getdate('2021-01-01')
```

**Today:**
```python
from frappe.utils import today
today()
```

**Add to Date:**
```python
from frappe.utils import add_to_date
add_to_date(today(), days=10)
```

**Pretty Date:**
```python
from frappe.utils import pretty_date
pretty_date('2021-01-01 12:00:00')
```

**Random String:**
```python
from frappe.utils import random_string
random_string(8)
```

**Money in Words:**
```python
from frappe.utils import money_in_words
money_in_words(123.45)
```

---

## Request Lifecycle

- **GET Requests:** No automatic commit.
- **POST/PUT:** Auto-commit on success.
- **Exceptions:** Auto-rollback.

---

## Hooks Examples

**Scheduler Events:**
```python
scheduler_events = {
    'daily': ['app.tasks.run_daily'],
    'cron': {
        '0 0 * * *': ['app.tasks.midnight_job']
    }
}
```

**Doc Events:**
```python
doc_events = {
    '*': {
        'on_update': 'app.events.log_update'
    }
}
```

**Override Doctype Class:**
```python
override_doctype_class = {
    'ToDo': 'app.overrides.todo.CustomToDo'
}
```

---

For detailed examples and additional APIs, refer to Frappe Framework Documentation.