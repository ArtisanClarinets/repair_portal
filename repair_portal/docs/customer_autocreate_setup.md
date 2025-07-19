# Customer Auto-Create Setup

**File:** `repair_portal/customer/events/utils.py`  
**Created:** 2025-06-29  
**Version:** v1.0  
**Author:** MRW Artisan Instruments ERP Team

---

## Purpose

This guide documents the complete setup and implementation of an automated process to **create a Customer record automatically whenever a new User is inserted** in the Frappe system.

This is designed to enforce a 1:1 mapping between `User` and `Customer`, ensuring consistency across the portal and desk environment.

---

## Overview

**Trigger:**
- **Event:** `User.after_insert`
- **Handler:** `create_customer()`

**Behavior:**
- Checks if a `Customer` already exists for the new User.
- If not, attempts to locate a `Customer` record matching the User's email.
- Creates and inserts a new `Customer` linked to the User (and Customer, if found).
- Commits the record so the Client can immediately access their profile upon first login.

---

## File Structure

```
repair_portal/
  customer/
    events/
      utils.py         # Hook implementation
  hooks.py             # Hook registration
```

---

## Hook Registration

In `hooks.py`:

```python
# User creation auto-creates Customer
doc_events = {
    "User": {
        "after_insert": "repair_portal.customer.events.utils.create_customer"
    }
}
```

---

## utils.py Implementation

**Path:** `repair_portal/customer/events/utils.py`

```python
import frappe

def create_customer(doc, method=None):
    """
    Create a Customer as soon as a User record is created.

    Args:
        doc: The new User document
        method: Hook signature compatibility
    """
    if frappe.db.exists("Customer", {"linked_user": doc.name}):
        return

    customer = frappe.db.get_value(
        "Customer",
        {"email_id": doc.email},
        ["name", "customer_name"],
        as_dict=True,
    )

    profile = frappe.get_doc({
        "doctype": "Customer",
        "linked_user": doc.name,
        "client_name": doc.full_name or doc.first_name,
        "email": doc.email,
        "customer": customer.name if customer else None
    })

    profile.insert(ignore_permissions=True)
    frappe.db.commit()
```

---

## Workflow Integration

This process works together with the `Customer` workflow:

- **States:** Draft, Active, Archived
- **Transitions:** Activate Profile, Archive, Re-Activate
- **State Field:** `profile_status`

Upon creation, the profile defaults to `Draft` status.

---

## Validation & Activation

During lifecycle operations, `customer.py` ensures:

- Only one `Customer` per `User`
- Required data present on linked `Customer`
- Automatic creation of `Player Profile` on activation
- Optional welcome emails sent to the linked customer

---

## Bench Commands After Setup

Run these commands to apply changes:

```
cd /opt/frappe/erp-bench
source env/bin/activate
bench --site erp.artisanclarinets.com migrate
bench --site erp.artisanclarinets.com clear-cache
bench --site erp.artisanclarinets.com clear-website-cache
```

---

## Notes

- This auto-create process is safe to run repeatedly because it first checks for existing Customers.
- You may adapt the logic to create a `Customer` if none is found.
- Bulk back-fill for existing Users can be implemented with `bench execute` using a similar script.

---

## Related Files

- `customer.py` (lifecycle methods)
- `customer.json` (DocType definition)
- `player_profile.json` (child Doctype definition)
- `customer_setup.json` (Workflow definition)

---

✅ **Setup Complete: This module is production-ready.**