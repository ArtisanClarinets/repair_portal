# File: instrument_profile/report/instrument_service_history/instrument_service_history.py
# Updated: 2025-06-14
# Version: 1.0
# Purpose: Script Report for Instrument Service History

import frappe


def execute(filters=None):
    columns = [
        {"label": "Date", "fieldname": "date", "fieldtype": "Date", "width": 100},
        {"label": "Service Type", "fieldname": "service_type", "fieldtype": "Data", "width": 120},
        {"label": "Description", "fieldname": "description", "fieldtype": "Data", "width": 220},
        {"label": "Performed By", "fieldname": "performed_by", "fieldtype": "Data", "width": 140},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 90},
        {"label": "Notes", "fieldname": "notes", "fieldtype": "Data", "width": 160},
    ]
    conditions = {}
    if filters:
        if filters.get("instrument_profile"):
            conditions["instrument_profile"] = filters["instrument_profile"]
        if filters.get("serial_number"):
            conditions["serial_number"] = filters["serial_number"]
        if filters.get("date_from"):
            conditions["date"] = [">=", filters["date_from"]]
        if filters.get("date_to"):
            conditions["date"] = ["<=", filters["date_to"]]
    data = frappe.get_all(
        "Service Log",
        filters=conditions,
        fields=["date", "service_type", "description", "performed_by", "status", "notes"],
    )
    return columns, data
