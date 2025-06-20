# relative path: intake/ocr.py
# updated: 2025-06-20
# version: 0.5
# purpose: OCR import for Handwritten Intake forms
# dev notes: renamed function to avoid name shadowing

from __future__ import annotations
import re
from io import BytesIO
from typing import Optional

import frappe
from frappe.utils.file_manager import get_file

try:
    import pytesseract
    from PIL import Image
except Exception:  # pragma: no cover - optional dependency
    pytesseract = None
    Image = None


@frappe.whitelist(allow_guest=False, methods=["POST"])
def process_handwritten_intake(file_id: str) -> dict[str, str | None]:
    """Process an uploaded intake form via OCR and create a Clarinet Intake."""

    # role guard (must be done at run-time, not import-time)
    frappe.only_for(["Technician"])

    if not pytesseract or not Image:
        frappe.throw("OCR libraries not installed. Please install pytesseract and Pillow.")

    file_doc     = frappe.get_doc("File", file_id)
    file_content = get_file(file_doc.file_url)[1]

    image = Image.open(BytesIO(file_content))
    text  = pytesseract.image_to_string(image)

    data   = _parse_intake_text(text)
    intake = frappe.new_doc("Clarinet Intake")
    intake.update(data)
    intake.insert(ignore_permissions=True)

    return {"intake": intake.name, **data}


def _parse_intake_text(text: str) -> dict[str, str | None]:
    """Rudimentary parser extracting known fields from OCR text."""
    patterns = {
        "customer":        r"Customer\s*Name[:\-]?\s*(?P<value>.+)",
        "phone":           r"Phone[:\-]?\s*(?P<value>.+)",
        "email":           r"Email[:\-]?\s*(?P<value>.+)",
        "serial_number":   r"Serial\s*Number[:\-]?\s*(?P<value>\w+)",
        "make":            r"Make[:\-]?\s*(?P<value>.+)",
        "model":           r"Model[:\-]?\s*(?P<value>.+)",
        "condition_notes": r"Condition\s*Notes[:\-]?\s*(?P<value>.+)",
    }

    result = {k: None for k in patterns}
    for field, pattern in patterns.items():
        if (m := re.search(pattern, text, re.IGNORECASE)):
            result[field] = m.group("value").strip()
    return result