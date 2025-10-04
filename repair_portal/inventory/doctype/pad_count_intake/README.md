## Doctype: Pad Count Intake

### 1. Overview and Purpose

**Pad Count Intake** is a doctype in the **Inventory** module that manages and tracks related business data.

**Module:** Inventory
**Type:** Master/Standard Document

This doctype is used to:
- Store and manage master or reference data
- Provide configuration or lookup information
- Support other business processes in the application

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `title` | Data | Default: `Clarinet Pad Intake`. Friendly name for this intake. Use something meaningful like 'Bb Clarinet Pads – Bench 2 – 2025‑08‑20'. |
| `photo` | Attach Image | **Required**. Upload a top‑down photo of the pads on a matte dark background. Keep the ArUco marker flat in the same plane. Shortest image side ≥ 2000 px. Avoid glare and blur. |
| `processed_preview` | Attach Image | Read-only. Auto‑generated overlay showing detected pads. Review the green circles to confirm the count before approval. |
| `detections_meta` | Attach | Read-only. JSON file with detection details (x, y, r, confidence, method, quality metrics). Useful for audit and troubleshooting. |
| `item` | Link (Item) | **Required**. ERPNext Item to update (must be a Stock Item). Example: 'Clarinet Pad – 10 mm'. |
| `warehouse` | Link (Warehouse) | **Required**. Warehouse where stock will be adjusted. The Company is inferred automatically from this warehouse. |
| `company` | Link (Company) | Read-only. Company owning the selected Warehouse. Filled automatically. |
| `uom` | Link (UOM) | Default: `Nos`. Unit of Measure for the inventory update, typically 'Nos' or 'Each'. |
| `detected_count` | Int | Read-only. Auto count from image processing. Always verify against the Processed Preview before approving. |
| `approved_count` | Int | **Required**. Human‑verified final count. This drives the inventory delta by default. Edit if the preview missed or over‑counted any pads. |
| `inventory_action` | Select (Increase
Decrease
No Change) | **Required**. Default: `Increase`. Choose how stock should be adjusted: Increase (Material Receipt), Decrease (Material Issue), or No Change (for review only). |
| `inventory_delta` | Int | Quantity to post to stock. Defaults to Approved Count. You may override for partial postings or adjustments. |
| `review_status` | Select (Pending Review
Approved
Needs Fix) | Default: `Pending Review`. Workflow state: Pending Review → Approved (ready to post) or Needs Fix (retake photo, adjust settings, or reprocess). |
| `flags_quality_ok` | Check | Read-only. Auto quality gate. Unchecked means blur/lighting/perspective are sub‑optimal—consider retaking the photo. |
| `notes` | Small Text | Free‑form notes for this intake (e.g., photo conditions, pad sizes mix, any anomalies). |
| `min_radius` | Int | Default: `10`. Minimum pad radius in pixels. If using Auto Pixel Radius from mm, this updates automatically after processing. |
| `max_radius` | Int | Default: `60`. Maximum pad radius in pixels. If using Auto Pixel Radius from mm, this updates automatically after processing. |
| `dp` | Float | Default: `1.2`. Hough Circles inverse ratio of accumulator to image resolution. 1.2–2.0 is typical; lower can improve sensitivity. |
| `param1` | Int | Default: `100`. Canny high threshold for Hough pre‑processing. Raise to reduce noise; lower to detect faint edges. |
| `param2` | Int | Default: `30`. Hough accumulator threshold. Higher = fewer detections (more strict). Lower if pads are missed. |
| ... | ... | *10 more fields* |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`pad_count_intake.py`) implements the following:

**Lifecycle Hooks:**
- **`before_save()`**: Executes logic before the document is saved

**Custom Methods:**
- `generate_shooting_kit()`: Custom business logic method
- `process_image()`: Custom business logic method
- `approve_count()`: Custom business logic method
- `update_inventory()`: Custom business logic method
- `detect_pads()`: Custom business logic method
- `order_pts()`: Custom business logic method
- `draw_single_page()`: Custom business logic method
- `draw_grid_page()`: Custom business logic method

#### Frontend Logic (JavaScript)

The JavaScript file (`pad_count_intake.js`) provides:

- **Custom Buttons**: Adds custom action buttons to the form

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Item** doctype via the `item` field (Item)
- Links to **Warehouse** doctype via the `warehouse` field (Warehouse)
- Links to **Company** doctype via the `company` field (Company)
- Links to **UOM** doctype via the `uom` field (UOM)
- Has child table **Pad Count Log** stored in the `count_logs` field
- Links to **Stock Entry** doctype via the `stock_entry` field (Stock Entry)

### 5. Critical Files Overview

- **`pad_count_intake.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`pad_count_intake.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`pad_count_intake.js`**: Client-side script for form behavior, custom buttons, and UI interactions

---

*Last updated: 2025-10-04*
