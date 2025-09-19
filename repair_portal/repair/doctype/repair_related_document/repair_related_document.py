# -*- coding: utf-8 -*-
# Relative Path: repair_portal/repair/doctype/repair_related_document/repair_related_document.py
# Purpose: Child table that normalizes cross-links from Repair Order (and others).
# Notes:
#   - Permissions are inherited from the parent document.
#   - Keep this class minimal; all logic should live on the parent (e.g., Repair Order).

from __future__ import annotations
import frappe
from frappe.model.document import Document

class RepairRelatedDocument(Document):
    pass
