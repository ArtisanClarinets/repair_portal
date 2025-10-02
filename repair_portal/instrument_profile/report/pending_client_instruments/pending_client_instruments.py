# Path: repair_portal/instrument_profile/report/pending_client_instruments/pending_client_instruments.py
# Date: 2025-10-02
# Version: 1.1.1
# Description: Server-side helper for the "Pending Client Instruments" query report - returns data for draft Client Instrument Profile submissions with filters for client name, status, and creation date range, keeping static type checkers happy.
# Dependencies: frappe (>=15.0.0)

from __future__ import annotationsader Template
# Relative Path: repair_portal/instrument_profile/report/pending_client_instruments/pending_client_instruments.py
# Last Updated: 2025-07-19
# Version: v1.1.1
# Purpose: Server-side helper for the “Pending Client Instruments” query report.
#          Returns data for the query report while keeping static type checkers happy.
# Dependencies: frappe (>=15.0.0)

from __future__ import annotations

from typing import Any, cast

import frappe

# Type alias for readability
Row = list[Any]


def execute(filters: dict[str, Any] | None = None) -> tuple[list[str], list[Row]]:
    """Entry point for Frappe Query Reports.

    Args:
        filters: Runtime filter values supplied by the report UI.

    Returns:
        A tuple containing an *empty* columns list (because columns are fully
        described in the accompanying JSON/SQL) and a list of rows.
    """

    filters = filters or {}

    raw_data = frappe.db.sql(
        """
        SELECT
            cip.name            AS `Instrument ID`,
            cip.client_name     AS `Client`,
            cip.instrument_type AS `Type`,
            cip.status          AS `Status`,
            cip.creation        AS `Created On`
        FROM `tabClient Instrument Profile` cip
        WHERE cip.docstatus = 0
          AND (%(client)s = '' OR cip.client_name = %(client)s)
          AND (%(status)s = '' OR cip.status = %(status)s)
          AND (%(created_from)s = '' OR cip.creation >= %(created_from)s)
          AND (%(created_to)s   = '' OR cip.creation <= %(created_to)s)
        ORDER BY cip.creation DESC
        """,
        filters,
        as_list=True,
    )

    # Explicitly cast to satisfy static type checkers (Pylance/mypy)
    data: list[Row] = cast(list[Row], raw_data)

    return [], data
