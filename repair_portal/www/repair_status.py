# relative path: www/repair_status.py
# updated: 2025-06-27
# version: 1.0
# purpose: Repair portal page showing unified status + turnaround avg.

import frappe
from repair_portal.repair.dashboard_chart_source.turnaround_time import get_data

def get_context(context):
    stats = get_data()
    context.average_turnaround = stats.get("average_turnaround_days")
    context.total_repairs = stats.get("total_repairs")
    context.title = "Repair Status Overview"
    return context