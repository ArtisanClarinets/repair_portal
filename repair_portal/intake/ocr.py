# relative path: intake/ocr.py
# updated: 2025-08-31
# version: 0.1
# purpose: OCR import for Handwritten Intake forms
# dev notes: uses pytesseract to parse uploaded intake images or PDFs and create Clarinet Intake records

from __future__ import annotations

import re
from io import BytesIO
from typing import Dict, Optional

import frappe
from frappe.utils.file_manager import get_file

try:
    import pytesseract
    from PIL import Image
except Exception:  # pragma: no cover - optional dependency
    pytesseract = None
    Image = None


@frappe.whitelist(allow_guest=False, methods=["POST"])
@frappe.only_for(["Technician"])
def import_handwritten_intake(file_id: str) -> Dict[str, Optional[str]]:
    """Process an uploaded intake form via OCR and create a Clarinet Intake."""

    if not pytesseract or not Image:
        frappe.throw("OCR libraries not installed. Please install pytesseract and Pillow.")

    file_doc = frappe.get_doc("File", file_id)
    file_content = get_file(file_doc.file_url)[1]

    image = Image.open(BytesIO(file_content))
    text = pytesseract.image_to_string(image)

    data = _parse_intake_text(text)
    intake = frappe.new_doc("Clarinet Intake")
    intake.update(data)
    intake.insert(ignore_permissions=True)

    return {"intake": intake.name, **data}


def _parse_intake_text(text: str) -> Dict[str, Optional[str]]:
    """Rudimentary parser extracting known fields from OCR text."""
    patterns = {
        "customer": r"Customer\s*Name[:\-]?\s*(?P<value>.+)",
        "phone": r"Phone[:\-]?\s*(?P<value>.+)",
        "email": r"Email[:\-]?\s*(?P<value>.+)",
        "serial_number": r"Serial\s*Number[:\-]?\s*(?P<value>\w+)",
        "make": r"Make[:\-]?\s*(?P<value>.+)",
        "model": r"Model[:\-]?\s*(?P<value>.+)",
        "condition_notes": r"Condition\s*Notes[:\-]?\s*(?P<value>.+)",
    }

    result = {key: None for key in patterns}
    for field, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result[field] = match.group("value").strip()
    return result
