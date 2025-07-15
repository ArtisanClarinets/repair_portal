# repair_portal/api/technician_dashboard.py
# Date: 2025-07-14
# Version: 2.0 - Refactored for unified Repair Order
# Purpose: API endpoint to fetch all data for the technician dashboard (now only Repair Order)

import frappe
from frappe import _

@frappe.whitelist()
def get_dashboard_data(technician=None):
    """
    Fetches all necessary data for the technician's dashboard, including
    assigned repairs, KPIs, and recent activity.
    """
    if not technician:
        technician = frappe.session.user

    if "Technician" not in frappe.get_roles(technician):
        frappe.throw(_("User does not have the Technician role."), frappe.PermissionError)

    # 1. Get KPIs from Repair Order
    kpis_result = frappe.db.sql(
        """
        SELECT
            IFNULL(SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END), 0) as open_repairs,
            IFNULL(SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END), 0) as in_progress_repairs,
            IFNULL(SUM(CASE WHEN promise_date < CURDATE() AND status NOT IN ('Closed', 'Resolved', 'Cancelled') THEN 1 ELSE 0 END), 0) as overdue_repairs
        FROM `tabRepair Order`
        WHERE technician_assigned = %(technician)s
        """,
        {"technician": technician},
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
            "technician_assigned": technician,
            "status": ["not in", ["Closed", "Resolved", "Cancelled"]],
        },
        fields=[
            "name",
            "customer",
            "instrument_category",
            "issue_description",
            "status",
            "priority_level",
            "promise_date",
        ],
        order_by="promise_date asc",
        limit=20,
    )

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
        WHERE ro.technician_assigned = %(technician)s
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
