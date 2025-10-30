# Approvals & Payments

## Overview
This document explains how customer approvals, deposits, and balance payments flow through the portal.

## Customer Approval Lifecycle
1. **Generate Quotation** – Create or update the ERPNext Quotation that represents the repair scope.
2. **Share Portal Link** – Direct the customer to `/customer_approval?reference_doctype=Quotation&reference_name=<quotation>`.
3. **Customer Decision** – Customer signs in, reviews the terms, and chooses *Approve* or *Decline*.
4. **Immutable Record** – The `Customer Approval` DocType locks after creation, storing signer identity, IP address, and a hashed signature string.
5. **Certificate Archive** – A PDF certificate is generated through the “Signed Approval Certificate” print format and attached to the record.
6. **Notifications** – Customer and repair managers receive confirmation emails using the `customer_approval_received` template.

## Deposits & Balance Payments
1. **Create Payment Request** – Issue ERPNext `Payment Request` documents linked to the same quotation.
2. **Portal Presentation** – The portal lists each outstanding request with a “Pay now” link that respects payment gateway routing.
3. **Gateway Callback** – When a payment request transitions to *Completed/Paid*, the hook `handle_payment_request_update` sends a receipt email via the `payment_received_notification` template.
4. **Idempotency** – Notification hooks set a flag on the in-memory document to avoid duplicate sends. Scheduler jobs can safely requeue without spamming customers.

## Error Handling
- Portal form validates signer name and terms consent; violations return inline alerts without losing form data.
- If the approval already exists, the portal displays a success message with a link to the existing certificate.
- Missing customer linkage throws a permission error via `ensure_customer_access` to prevent cross-account leaks.

## Operational Commands
- Use the runbook’s Phase 0 flow to migrate, build, and run tests before shipping approvals or payments updates.
- To simulate a payment event in a controlled environment, update a payment request to `Completed` and run the following inside
  a bench console session:

  ```python
  import frappe
  from repair_portal.repair_portal.doctype.customer_approval import payment_hooks

  doc = frappe.get_doc("Payment Request", "<name>")
  payment_hooks.handle_payment_request_update(doc, "on_update")
  ```
- For a full demo (customer, quotation, payment request, approval, and simulated payment) execute
  `bench --site $SITE execute repair_portal.tools.approval_demo.run`.
