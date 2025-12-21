# repair_portal/api/technician_dashboard.py
# Date: 2025-07-14
# Version: 2.0 - Refactored for unified Repair Order
# Purpose: API endpoint to fetch all data for the technician dashboard (now only Repair Order)

import frappe
from frappe import _
from frappe.utils import nowdate


@frappe.whitelist(allow_guest=False)
def get_dashboard_data(technician=None):
    """
    Fetches all necessary data for the technician's dashboard, including
    assigned repairs, KPIs, and recent activity.
    """
    if not technician:
        technician = frappe.session.user

    if technician != frappe.session.user:
        # Check for privileged roles
        allowed_roles = {"Repair Manager", "System Manager"}
        if not set(frappe.get_roles()).intersection(allowed_roles):
            frappe.throw(_("Insufficient permissions to view this dashboard."), frappe.PermissionError)

    if "Technician" not in frappe.get_roles(technician):
        frappe.throw(_("User does not have the Technician role."), frappe.PermissionError)

    # 1. Get KPIs from Repair Order
    kpis_result = frappe.db.sql(
        """
        SELECT
            IFNULL(SUM(CASE WHEN workflow_state IN ('Draft', 'In Progress') THEN 1 ELSE 0 END), 0) AS open_repairs,
            IFNULL(SUM(CASE WHEN workflow_state = 'In Progress' THEN 1 ELSE 0 END), 0) AS in_progress_repairs,
            IFNULL(SUM(CASE WHEN target_delivery IS NOT NULL AND target_delivery < %(today)s AND workflow_state NOT IN ('Delivered', 'Closed') THEN 1 ELSE 0 END), 0) AS overdue_repairs
        FROM `tabRepair Order`
        WHERE assigned_technician = %(technician)s
        """,
        {"technician": technician, "today": nowdate()},
        as_dict=True,
    )
    kpis = (
        list(kpis_result)[0]
        if kpis_result
        else {"open_repairs": 0, "in_progress_repairs": 0, "overdue_repairs": 0}
    )

    # 2. Get list of currently assigned repairs (not closed/resolved/cancelled)
    assigned_repairs = frappe.get_list(
        "Repair Order",
        filters={
            "assigned_technician": technician,
            "workflow_state": ["not in", ["Delivered", "Closed"]],
        },
        fields=[
            "name",
            "customer",
            "instrument_profile",
            "workflow_state",
            "priority",
            "target_delivery",
            "remarks",
        ],
        order_by="target_delivery asc",
        limit=20,
    )

    if assigned_repairs:
        instrument_names = [row.instrument_profile for row in assigned_repairs if row.instrument_profile]
        instrument_meta = {
            doc.name: doc
            for doc in frappe.get_all(
                "Instrument Profile",
                filters={"name": ["in", instrument_names]},
                fields=["name", "headline", "instrument_category", "serial_no"],
            )
        }
        for row in assigned_repairs:
            instrument = instrument_meta.get(row.instrument_profile)
            if instrument:
                parts = [instrument.headline, instrument.instrument_category, instrument.serial_no]
                row["instrument_label"] = " • ".join(filter(None, parts)) or instrument.name
            else:
                row["instrument_label"] = row.instrument_profile

    # 3. Get recent activity feed (last 5 pulse updates for this tech's repairs)
    recent_activity = frappe.db.sql(
        """
        SELECT
            pu.repair_order,
            pu.status,
            pu.note,
            pu.timestamp
        FROM `tabPulse Update` pu
        JOIN `tabRepair Order` ro ON pu.repair_order = ro.name
        WHERE ro.assigned_technician = %(technician)s
        ORDER BY pu.timestamp DESC
        LIMIT 5
        """,
        {"technician": technician},
        as_dict=True,
    )

    return {
        "kpis": kpis,
        "assigned_repairs": assigned_repairs,
        "recent_activity": recent_activity,
    }
