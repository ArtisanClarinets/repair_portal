from __future__ import annotations

import frappe


def after_submit_stock_entry(doc, method=None):
    """If a Stock Entry (Material Issue) references an RO in remarks or any item description,
    mirror its rows into the linked Repair Order's actual_materials.
    """
    # Find RO reference by scanning remarks or item descriptions for 'RO-...'
    ro_name = None
    if doc.remarks and "RO-" in doc.remarks:
        # naive extract: look for token starting with RO-
        for token in doc.remarks.split():
            if token.startswith("RO-"):
                ro_name = token.strip()
                break
    if not ro_name:
        for it in doc.get("items", []):
            if it.description and "RO-" in it.description:
                for token in it.description.split():
                    if token.startswith("RO-"):
                        ro_name = token.strip()
                        break
            if ro_name:
                break
    if not ro_name:
        return

    if not frappe.db.exists("Repair Order", ro_name):
        return

    # Mirror into RO.actual_materials
    from repair_portal.repair.doctype.repair_order.repair_order import (
        refresh_actuals_from_stock_entry,
    )

    refresh_actuals_from_stock_entry(ro_name, doc.name)
