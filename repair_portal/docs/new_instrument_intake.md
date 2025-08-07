# 📦 New Instrument Intake Process

This guide explains how to process **new clarinets received from the manufacturer**, ensuring all inventory, serial, and instrument records are automatically created and linked.

---

## 🎯 Overview

**Steps to process new instruments:**

1. **Create a Purchase Receipt** in ERPNext.
2. **Create a Clarinet Intake** in Repair Portal.
3. **Perform QC Inspection** (optional).
4. **Submit the Clarinet Intake** to create Items and Serial Numbers.
5. **Confirm Instrument Profile linkage.**

---

## 📝 Step-by-Step Instructions

### 1️⃣ Create Purchase Receipt

ERPNext > **Buying > Purchase Receipt**

- Select your supplier.
- Add Item Codes for the clarinets.
- Enter Quantity, Warehouse, and Serial Numbers if known.
- **Save and Submit.**

✅ This records the receipt in stock.


---

### 2️⃣ Create Clarinet Intake

Repair Portal > **Intake > Clarinet Intake**

**Fields to Complete:**

| Field               | Example                    |
|---------------------|----------------------------|
| Intake Type         | Inventory                  |
| Purchase Receipt    | PR-0001                    |
| Purchase Order      | PO-0003                    |
| Warehouse           | Main Warehouse             |
| Serial Number       | CL-12345                   |
| QC Status           | Pass / Fail                |
| Stock Status        | Available / Hold           |

✅ Use QC Status = **Fail** if inspection fails.


---

### 3️⃣ Inspection (Optional)

If you want detailed QC:

- Create an **Inspection Report**.
- Document photos and failure reasons.
- Automatically generate **Non-Conformance Reports**.

✅ This is optional; you can simply set QC Status if preferred.


---

### 4️⃣ Submit Clarinet Intake

When you **Submit**, the system will:

- Create the **Item** (if not already existing).
- Create the **Serial No** linked to the Purchase Receipt and Warehouse.
- Update the **Instrument Profile** with status and linkage.
- If QC Status is Fail, set Stock Status = Hold.

✅ This step finalizes intake.


---

### 5️⃣ Instrument Profile

Linked Instrument Profile is updated:

- **Status:** Available / Hold / Under Repair.
- **Latest Intake:** Reference to this Clarinet Intake.

✅ Use the **Instrument Profile Workspace** to track readiness.


---

## 🧪 Example Timeline

1. **Purchase Receipt PR-0001**
   - 5 clarinets received into Main Warehouse.

2. **Clarinet Intake INT-0001**
   - Intake Type: Inventory
   - Serial Number: CL-12345
   - QC Status: Pass

3. **Submit**
   - Item and Serial No created.
   - Instrument Profile updated.

4. **Instrument Ready for Use.**


---

## 🛠 Tips for Testing

- Create a test Purchase Receipt.
- Submit a Clarinet Intake.
- Confirm:
  - `Item` exists.
  - `Serial No` exists.
  - `Instrument Profile` updated.

✅ Done! You are ready to process incoming clarinets efficiently.


---

_This guide is maintained in `repair_portal/docs/new_instrument_intake.md`_.