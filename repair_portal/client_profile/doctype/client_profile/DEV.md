# Developer Guide: Client Profile

**Path:** `repair_portal/client_profile/doctype/client_profile/`
**Last Updated:** 2025-07-16

---

## 📘 Overview
The `Client Profile` Doctype represents a top-level CRM entity for Artisan Clarinets clients. It is the primary gateway for managing customer data, associated instruments, linked players, repair activity, and quality metrics.

This guide documents the structure, lifecycle events, automation logic, and downstream dependencies for future developers.

---

## 🧩 Fields Summary

| Field Name                 | Type     | Purpose                                     |
|---------------------------|----------|---------------------------------------------|
| `client_name`             | Data     | Required full name of the client            |
| `display_name`            | Data     | Optional alternate display name             |
| `customer`                | Link     | Linked ERPNext Customer (auto-created)      |
| `email`                   | Data     | Used for Contact creation                   |
| `phone`                   | Data     | Used for Contact creation                   |
| `billing_address`         | Link     | Links to an existing Address Doctype        |
| `primary_contact`         | Link     | Links to the created Contact (if any)       |
| `type`                    | Select   | Individual / Institution / Organization     |
| `preferred_contact_method`| Select   | Email / Phone / SMS                         |
| `preferred_payment_method`| Select   | Card / Check / Bank Transfer                |
| `credit_terms`            | Data     | Freeform note, copied to Customer Details   |
| `credit_limit`            | Currency | Maps to ERPNext `credit_limit`              |

---

## 🧠 Automation Summary

### `on_submit()`
- Triggered when the Client Profile is submitted.
- Calls `create_customer()` **only if** `self.customer` is empty.

### `create_customer()`
Creates a new ERPNext `Customer` with:
- `customer_name`: from `display_name` or fallback to `client_name`
- `customer_type`: from `type` field, defaults to "Individual"
- `credit_terms`: stored in `customer_details`

Also:
- Creates `Contact` if `email` or `phone` is present
- Links existing `billing_address` to the Customer
- Assigns the resulting Customer name to `self.customer`

### `on_update()`
Refreshes child tables by syncing records that reference `client_profile`:
- Instrument Profile → `owned_instruments`
- Player Profile → `linked_players`
- Repair Log → `repair_logs`
- Leak Test → `leak_tests`
- Intonation Session → `tone_sessions`
- Clarinet Inspection → `qa_findings`
- Clarinet Setup Log → `setup_logs`

Each table is cleared and repopulated to reflect the current related state.

---

## 🧪 Testing Tips
- Use the Submit action from the Client Profile UI.
- Confirm that a Customer and optional Contact are created in ERPNext.
- Reopen the profile to verify linked child tables update correctly.

---

## 🔗 Dependencies
- `Customer`, `Contact`, `Address` (ERPNext Core)
- `Instrument Profile`, `Player Profile`, `Repair Log`, `Leak Test`, `Intonation Session`, `Clarinet Inspection`, `Clarinet Setup Log`

---

## 🧹 TODOs & Enhancements
- Auto-generate primary address if none is provided
- Create customer group dynamically based on type (if needed)
- Add field validations for `email` and `phone`

---

Happy developing! 🎷