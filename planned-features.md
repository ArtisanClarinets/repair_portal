# Planned Feature: Handwritten Intake Form Recognition

This feature allows technicians to fill out a printed intake form by hand and import the data into the Repair Portal via photo or scan.

---

## 🧾 Phase 1: Printable Intake Template (PDF)
- **Purpose**: Capture customer and instrument data offline during walk-ins
- **Fields Included**:
  - Customer Name, Phone, Email
  - Instrument Category, Make, Model, Serial
  - Accessories, Condition Notes
  - Consent Text + Signature
- **Format**: A4 PDF with OCR-friendly layout (open boxes, clear labels)
- **Implementation**: PDF generated using `frappe.utils.print_format.download_pdf()` or static template in `/public/pdf_templates`

## 🖼️ Phase 2: OCR Import Functionality
- **Upload Form**: Custom DocType button: “Import Handwritten Intake”
- **Input**: Image or PDF of completed form
- **Backend Processing**:
  - Convert image to text via OCR (e.g. Tesseract or Google Vision API)
  - Regex + ML text parsing to extract field values
  - Validation step for technician to confirm values
- **Mapped DocTypes**:
  - `Customer Consent Form`
  - `Instrument Intake Form`

## ⚙️ Backend Tools
- `pytesseract` for OCR (fallback to Google Cloud Vision for accuracy)
- Custom Python controller in Frappe for processing
- Temporary File storage using Frappe’s File system

## 👤 User Flow
1. Print intake PDF
2. Customer completes form by hand
3. Technician uploads image to ERPNext
4. OCR extracts fields
5. Technician reviews and confirms parsed data
6. System creates relevant DocTypes automatically

## 🔐 Privacy & Security
- Uploaded images stored securely under Customer Folder
- Images marked private in File DocType
- Data discarded after successful import unless user saves explicitly

## 📅 Status: PLANNED
- PDF template pending
- OCR integration scoped for Frappe v15 compatibility
- Requires manual QA before release

---

## Future Enhancements
- Barcode for form ID
- QR code for customer self-verification
- Form versioning
- AI handwriting model finetuned on clarinet shop data

## 🔄 Last Updated
June 2025

---

This plan enables robust intake for environments without digital access, while still integrating cleanly into the ERP system.