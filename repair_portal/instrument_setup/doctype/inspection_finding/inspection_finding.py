# File: repair_portal/repair_portal/instrument_setup/doctype/inspection_finding/inspection_finding.py
# Updated: 2025-06-12
# Version: 1.1
# Purpose: Clarinet Inspection Finding (Child Table); tracks inspection issues and recommended actions

from frappe.model.document import Document


class InspectionFinding(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        action_required: DF.Literal["Repair", "Replace", "Monitor"]
        component: DF.Literal["Key", "Pad", "Tenon", "Corks", "Bumpers", "Other"]
        issue_type: DF.Literal["Crack", "Bent Key", "Pad Leak", "Cork Wear", "Plating Wear", "Other"]
        location: DF.Literal["Mouthpiece", "Barrel/Neck", "Upper Joint", "Lower Joint", "Bell", "Other"]
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
        photo: DF.AttachImage | None
        recommendation: DF.Text
        severity: DF.Literal["Low", "Medium", "High", "Critical"]
    # end: auto-generated types
    pass
