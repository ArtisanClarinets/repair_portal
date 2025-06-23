# File: repair_portal/enhancements/report/defect_heatmap_report/defect_heatmap_report.py
# Updated: 2025-06-20
# Version: 1.0
# Purpose: Aggregated defect reporting by model for heat-map analysis

from collections import defaultdict

import frappe


def execute(filters=None):
    filters = filters or {}
    model = filters.get("model")

    raw_logs = frappe.db.get_all("Repair Log", fields=["model", "part", "defect_type"], filters={"model": model} if model else {})

    data_map = defaultdict(lambda: defaultdict(int))
    for row in raw_logs:
        key = (row["model"], row["part"])
        data_map[key][row["defect_type"]] += 1

    rows = []
    for (model, part), defects in data_map.items():
        for defect_type, count in defects.items():
            rows.append({
                "model": model,
                "part": part,
                "defect_type": defect_type,
                "count": count
            })

    columns = [
        {"label": "Model", "fieldname": "model", "fieldtype": "Data", "width": 150},
        {"label": "Part", "fieldname": "part", "fieldtype": "Data", "width": 150},
        {"label": "Defect Type", "fieldname": "defect_type", "fieldtype": "Data", "width": 200},
        {"label": "Count", "fieldname": "count", "fieldtype": "Int", "width": 100}
    ]
    return columns, rows