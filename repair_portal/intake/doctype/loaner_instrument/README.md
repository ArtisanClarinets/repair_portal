# Loaner Instrument (`loaner_instrument`)

## Purpose
The Loaner Instrument DocType manages instruments temporarily issued to customers while their own instrument is under repair. It tracks issuance, expected return dates, and automatically generates digital loaner agreements.

## Schema Summary
- **DocType Type:** Submittable
- **Workflow States:** Controlled by `loaner_status`
  - `Issued` → Default on creation
  - `Returned` → Marked when instrument is returned
  - `Overdue` → System or user can flag overdue returns
- **Key Fields:**
  - `loaner_serial` (Data, Required): Unique loaner serial number
  - `item_code` (Link → Item): ERPNext Item reference
  - `issued_to` (Link → Customer): Customer borrowing the instrument
  - `issued_date` (Date, Required): Loaner start date
  - `expected_return_date` (Date): Anticipated return date
  - `returned` (Check): Boolean toggle when instrument returned
  - `loaner_status` (Select): Status field (Issued, Returned, Overdue)

## Business Rules
- Loaner instruments must have a unique `loaner_serial`.
- PDF agreements are automatically generated when an instrument is issued.
- Returned instruments must toggle the `returned` checkbox and set `loaner_status` to Returned.
- Overdue instruments should be monitored for follow-up actions.

## Python Controller Logic
File: `loaner_instrument.py`

- **Class:** `LoanerInstrument(Document)`
- **Hooks:**
  - `after_insert()`: Automatically generates loaner agreement if instrument is issued.
- **Methods:**
  - `generate_loaner_agreement()`: Creates a PDF contract and attaches to the document.

### Example Logic
```python
context = {"doc": self, "customer": frappe.get_doc("Customer", self.issued_to)}
html = render_template("repair_portal/intake/templates/loaner_agreement_template.html", context)
pdf = get_pdf(html)
filename = f"LoanerAgreement_{self.name}.pdf"
save_file(filename, pdf, self.doctype, self.name, is_private=1)
```

**Error Handling:**
- Logs traceback with `frappe.log_error()`.
- User notified: `"There was an error generating the loaner agreement PDF. Please contact support."`

## Client-Side Script
- None currently.
- Potential enhancements:
  - Dashboard indicator for overdue instruments.
  - Auto-popup to confirm loaner return.

## Integration Points
- **Customer**: Loaner is linked to a customer record.
- **Item**: Each loaner references an Item master.
- **PDF Templates**: Uses Jinja2 loaner agreement template for contract generation.
- **File Manager**: Stores loaner agreement as a private file.

## Validation Standards
- `loaner_serial`: Required, must be unique.
- `issued_date`: Required.
- `loaner_status`: Must be one of Issued, Returned, Overdue.
- PDF generation errors are logged for audit.

## Usage Examples
- **New Loaner Issue:**  
  `loaner_serial: LN-2025-001, issued_to: John Doe, issued_date: 2025-08-16, expected_return_date: 2025-09-01, loaner_status: Issued`  
  → Auto-generates loaner agreement.
- **Return Processing:**  
  Mark `returned = 1`, update `loaner_status = Returned`.

## Changelog
- **2025-08-16**: Documentation created.
- **2025-07-17**: Added PDF auto-generation with robust error handling.

## Dependencies
- **Frappe Framework**
- **ERPNext Item**
- **Customer**
- **File Manager** (for PDF storage)
- **Jinja2 Templates**