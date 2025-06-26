# relative path: repair/dashboard_chart_source/turnaround_time.py
# updated: 2025-06-27
# version: 1.0
# purpose: Calculate average turnaround time from intake to closure.

import frappe
from frappe.utils import getdate

def get_data():
    closed_orders = frappe.get_all("Repair Order", filters={"status": "Closed"}, fields=["intake", "modified"])

    total_days = 0
    count = 0
    for order in closed_orders:
        intake = frappe.db.get_value("Clarinet Intake", order.intake, "received_date")
        if intake:
            delta = (getdate(order.modified) - getdate(intake)).days
            total_days += delta
            count += 1

    average_days = round(total_days / count, 1) if count else 0
    return {"average_turnaround_days": average_days, "total_repairs": count}