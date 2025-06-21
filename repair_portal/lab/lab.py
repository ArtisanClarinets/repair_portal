# File: repair_portal/repair_portal/lab/lab.py
# Updated: 2025-06-20
# Version: 1.0
# Purpose: Shared logic and utilities for the Lab module

import frappe


def get_repair_summary():
    return frappe.db.count("Custom Doctype")