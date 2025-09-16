# Path: repair_portal/repair_portal/instrument_setup/doctype/clarinet_template_task/clarinet_template_task.py
# Version: v1.0
# Date: 2025-08-12
# Purpose: Child rows on Setup Template used to seed Clarinet Setup Task docs.
# Copyright (c) 2025, DT and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ClarinetTemplateTask(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from repair_portal.instrument_setup.doctype.clarinet_template_task_depends_on.clarinet_template_task_depends_on import ClarinetTemplateTaskDependsOn

        default_priority: DF.Literal["Low", "Medium", "High", "Urgent"]
        depends_on: DF.Table[ClarinetTemplateTaskDependsOn]
        description: DF.SmallText | None
        exp_duration_mins: DF.Int
        exp_start_offset_days: DF.Int
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
        sequence: DF.Int
        subject: DF.Data
    # end: auto-generated types
    pass
