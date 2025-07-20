# Clarinet Intake Doctype — Comprehensive Logic & Usage Guide

## **Purpose & Scope**
The Clarinet Intake doctype is the central entry point for all clarinets coming into the system—whether as new inventory for sale, customer repairs, or maintenance. It automates and enforces full traceability and quality for every instrument, from intake to sale or service completion.

---

## **Supported Intake Types**
- **New Inventory:** New clarinets being added to shop inventory (no customer linked).
- **Repair:** Customer-owned instruments received for repair (must link customer).
- **Maintenance:** Customer-owned instruments received for routine service (must link customer).

---

## **Field Logic & Required Data**
- **Dynamic required fields:** The set of required fields changes depending on the intake type, enforced on both the frontend and backend.
  - *New Inventory*: Requires item_code, item_name, manufacturer, acquisition source/cost, asking price, serial number, and key instrument details.
  - *Repair/Maintenance*: Requires customer, service request, stated issue, manufacturer, model, and serial number.
- **Validation** occurs both client-side and server-side before submit.

---

## **Automation & Record Creation**
### **Upon Intake Submission:**
1. **Item Creation/Update (Inventory):**
   - Creates or updates an ERPNext Item.
   - Maps: item code, item name, item group, brand, warehouse, supplier code, stock UOM—all from settings.
   - Sets custom clarinet fields (body, keywork, pitch, etc).
   - Applies brand mapping logic from settings JSON (if set).
2. **Item Price Records (Inventory):**
   - Creates/updates buying price (acquisition cost) and selling price (asking price) using price lists from settings.
3. **Serial No Creation:**
   - Always creates a Serial No for the instrument (linked to Item, assigned to inspection warehouse).
4. **Instrument Record Creation/Linkage:**
   - Finds or creates an Instrument document, always linked to Serial No and Item.
   - **NEW:** If an Intake is submitted with a serial number that does not match any Instrument, a new Instrument is automatically created and linked, with as much data prefilled as possible.
5. **Instrument Inspection:**
   - Always creates an Instrument Inspection linked to the intake and instrument.
   - Sets inspection type label from settings ("Initial Inspection" for inventory, "Arrival Inspection" for repair/maintenance).
6. **Clarinet Initial Setup (Inventory):**
   - Auto-creates a Clarinet Initial Setup record for each new inventory intake (linked to instrument and intake) if enabled in settings.
7. **Stock Validation & Notification:**
   - Warns (via Desk message) if Serial No or Item is not present in the inspection warehouse or actual stock is 0.
   - Notification toggles controlled via settings.

---

## **Workflow Logic (Recursive Overview)**
- **Intake Creation:**
  - User fills out the form, selects intake type.
  - Field requirements and validation adapt automatically.
- **On Submit:**
  - Controller loads all business logic from the Clarinet Intake Settings doctype.
  - For new inventory, creates or updates all linked ERPNext objects (Item, Item Prices, Serial No, Instrument, Inspection, Initial Setup) in correct order, with all relationships enforced.
  - For repair/maintenance, ensures instrument and inspection records are present and properly linked to the intake and customer.
  - If any linkage or data fails (e.g., missing instrument, stock, or serial), the user is notified immediately with actionable messages. All exceptions are logged for admin review.
- **Automation Recursion:**
  - Every newly created document (Item, Serial No, Instrument, Inspection, Setup) is immediately available for further automation downstream—e.g., assignment to customer, triggering QC, or setup tasks.
  - If an intake is edited and resubmitted, logic is idempotent: duplicate records are never created.
  - All future changes to business rules (warehouses, item groups, branding, labels, toggles) are handled instantly via the Clarinet Intake Settings doctype—**no code deploy needed**.

---

## **Settings-Driven Architecture**
- All core logic references the **Clarinet Intake Settings** doctype, a single-record Desk form managed by authorized users:
  - Default item group, warehouse, price lists, stock UOM
  - Automation toggles (auto-inspection, auto-setup, stock notifications)
  - Brand mapping (JSON), supplier code prefix, naming series
  - Custom inspection type labels (for inventory and repair)
- Any settings change is instantly reflected in all new intakes and automations.

---

## **User Interface Features**
- **Settings Button:** Visible on both the intake form (Actions menu) and intake list view menu for System Manager and Repair Manager roles—direct link to settings.
- **Dynamic field toggling:** Fields and required-ness change live based on intake type.
- **Immediate notifications:** Desk messages for any missing required data or stock issues.

---

## **Permissions & Security**
- **Doctype permissions** follow Frappe/ERPNext best practices.
- **Settings access** limited to authorized admin/manager roles.
- **No sensitive business logic is exposed to end users.**

---

## **Technical Details & Best Practices**
- **All controller logic** (clarinet_intake.py) is PEP8, commented, and settings-driven.
- **Frontend (clarinet_intake.js)** handles live validation, dynamic field rules, and navigation.
- **Settings controller** ensures JSON validation for brand mapping and safe pattern use.
- **All errors are logged** for audit and debugging.
- **Data integrity:** Intake record naming, linkage, and all automated relationships are validated at every step.
- **Idempotency:** Automation avoids duplicate objects if intake is resubmitted or edited.
- **Upgrade-friendly:** As Frappe/ERPNext evolves, core settings logic ensures business flexibility with no need for code changes.
- **Instrument Auto-Creation:** When a Clarinet Intake is submitted, the controller checks for an existing Instrument by serial number. If not found, it creates one automatically, ensuring every Intake always has a linked Instrument.

---

## **How to Use**
1. **Admins:** Configure all settings in "Clarinet Intake Settings" (found in the Intake module or via form/list view button).
2. **Users:** Open a new Clarinet Intake, select type, and fill all required data. Submit when ready.
3. **Automation:** All downstream records (Item, Prices, Serial, Instrument, Inspection, Setup) are created and linked automatically.
4. **Review notifications:** Address any missing stock or linkage issues as prompted in Desk.

---

## **File Index**
- **clarinet_intake.json**: Doctype schema
- **clarinet_intake.py**: Backend controller (settings-driven)
- **clarinet_intake.js**: Frontend logic, validation, settings navigation
- **clarinet_intake_settings.json/py**: Settings doctype & validation logic
- **README.md**: (This file)

---

## **Version**
- Frappe/ERPNext v15
- Last updated: 2025-07-20

---

## **Support & Documentation**
For questions, change requests, or onboarding support, contact the ERP team or refer to Desk module documentation. All technical debt and system enhancements are tracked in `/CHANGELOG.md`.
