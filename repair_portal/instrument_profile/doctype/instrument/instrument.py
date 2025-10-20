# Path: repair_portal/instrument_profile/doctype/instrument/instrument.py
# Date: 2025-10-02
# Version: 1.3.0
# Description: Optimized Instrument DocType controller with ISN-aware duplicate checks, reduced DB calls, and backward-compatible serial number handling
# Dependencies: frappe, frappe.model.naming, Instrument Category, repair_portal.utils.serials

from __future__ import annotations

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

# Single source of truth for resolving raw → ISN (if available)
try:
    from repair_portal.utils.serials import find_by_serial as isn_find_by_serial  # type: ignore
except Exception:

    def isn_find_by_serial(serial_input: str):
        return None


# Cache for active instrument category to minimize DB lookups
_active_category_cache: str | None = None


class Instrument(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from repair_portal.instrument_profile.doctype.instrument_accessory.instrument_accessory import (
            InstrumentAccessory,
        )

        accessory_id: DF.Table[InstrumentAccessory]
        attachments: DF.AttachImage | None
        body_material: DF.Data | None
        brand: DF.Link | None
        clarinet_type: DF.Literal[
            "B\u266d Clarinet",
            "A Clarinet",
            "E\u266d Clarinet",
            "Bass Clarinet",
            "Alto Clarinet",
            "Contrabass Clarinet",
            Other,
        ]
        current_status: DF.Literal[Active, "Needs Repair", "Awaiting Parts", "In Service", Archived]
        customer: DF.Link | None
        instrument_category: DF.Link | None
        instrument_id: DF.Data | None
        instrument_type: DF.Literal[
            "B\u266d Clarinet",
            "A Clarinet",
            "Bass Clarinet",
            "E\u266d Clarinet",
            "Alto Clarinet",
            "Contrabass Clarinet",
            Other,
        ]
        key_plating: DF.Literal[Silver, Nickel, Gold, Other]
        keywork_plating: DF.Data | None
        model: DF.Data | None
        notes: DF.SmallText | None
        pitch_standard: DF.Data | None
        serial_no: DF.Data
        year_of_manufacture: DF.Int
    # end: auto-generated types
    """Instrument Document Model with optimized validation and naming."""

    from typing import TYPE_CHECKING

    def validate(self):
        """
        Validation logic executed on every save.
        Optimized to avoid unnecessary DB calls and duplicate operations.
        """
        # Only check for duplicate serial number if it's a new document or serial number changed
        if self.is_new() or self.has_value_changed("serial_no"):
            self.check_duplicate_serial_no()
            self.set_instrument_id()

        # Validate instrument category
        self.ensure_valid_instrument_category()

    def autoname(self):
        """
        Generate a name for the document using series.
        Runs only once, avoids duplicate calls inside validate.
        """
        if not self.name:
            self.name = make_autoname("INST-.####")

    def check_duplicate_serial_no(self):
        """
        Ensure serial_no is unique across all Instrument records,
        considering that serial_no may be:
          - a Link to Instrument Serial Number (ISN),
          - a legacy Link/Data to ERPNext Serial No,
          - a raw stamped string (Data).

        Strategy:
          1) Always block if another Instrument has the same 'serial_no' value.
          2) If our serial_no is a Link to ISN:
               - also block if another Instrument stores the ISN's raw serial string as Data.
          3) If our serial_no is a raw string (Data):
               - resolve to ISN; if found, also block if another Instrument stores that ISN name as Link.
        """
        if not self.serial_no:  # type: ignore
            return

        fieldtype = _get_instrument_serial_field_type()
        current_value = str(self.serial_no).strip()  # type: ignore

        # (1) Strict equality check (covers Link=Link and Data=Data exact)
        same = frappe.db.exists("Instrument", {"serial_no": current_value, "name": ["!=", self.name]})
        if same:
            frappe.log_error(f"Duplicate Serial Number (exact match): {current_value} in Instrument {same}.")
            frappe.throw(
                f"Serial Number {current_value} already exists in another Instrument record ({same})."
            )

        # (2) If this is a Link to ISN, also guard against another Instrument that saved the ISN's *raw* serial as Data
        if fieldtype == "Link" and frappe.db.exists("Instrument Serial Number", current_value):
            try:
                isn_raw = frappe.db.get_value("Instrument Serial Number", current_value, "serial")
                if isn_raw:
                    conflict = frappe.db.exists(
                        "Instrument", {"serial_no": isn_raw, "name": ["!=", self.name]}
                    )
                    if conflict:
                        frappe.log_error(
                            f"Duplicate Serial Number (ISN link vs raw): ISN={current_value}, raw='{isn_raw}' "
                            f"already present on Instrument {conflict}."
                        )
                        frappe.throw(
                            f"Serial Number already exists on another Instrument ({conflict}). "
                            f"Conflicting raw serial: {isn_raw}"
                        )
            except Exception:
                frappe.log_error(
                    frappe.get_traceback(),
                    "Instrument.check_duplicate_serial_no ISN/raw cross-check failed",
                )

        # (3) If this is a raw string (Data), try to resolve to ISN and guard against another Instrument that stored the ISN name
        if fieldtype != "Link":
            try:
                isn_row = isn_find_by_serial(current_value)
                if isn_row and isn_row.get("name"):
                    conflict = frappe.db.exists(
                        "Instrument", {"serial_no": isn_row["name"], "name": ["!=", self.name]}
                    )
                    if conflict:
                        frappe.log_error(
                            f"Duplicate Serial Number (raw vs ISN link): raw='{current_value}', ISN={isn_row['name']} "
                            f"already present on Instrument {conflict}."
                        )
                        frappe.throw(
                            f"Serial Number already exists on another Instrument ({conflict}). "
                            f"Conflicting ISN: {isn_row['name']}"
                        )
            except Exception:
                frappe.log_error(
                    frappe.get_traceback(),
                    "Instrument.check_duplicate_serial_no raw/ISN cross-check failed",
                )

    def ensure_valid_instrument_category(self):
        """
        Validate instrument_category link. If invalid, patch with first active category if available.
        Uses cached value to reduce DB calls.
        """
        global _active_category_cache

        if self.instrument_category and not frappe.db.exists("Instrument Category", self.instrument_category):
            if not _active_category_cache:
                _active_category_cache = frappe.db.get_value(
                    "Instrument Category", {"is_active": 1}, "name"
                )  # type: ignore
            if _active_category_cache:
                self.instrument_category = _active_category_cache
            else:
                frappe.throw(
                    "Instrument Category is invalid and no active category found. Please select a valid category."
                )

    def set_instrument_id(self):
        """
        Generate a unique instrument_id using the pattern INST-####-{serial_no}.
        Only regenerate if serial_no is set and changed or instrument_id is empty.
        """
        try:
            if self.serial_no:  # type: ignore
                if (not self.instrument_id) or (
                    self.instrument_id and not str(self.instrument_id).endswith(str(self.serial_no))  # type: ignore
                ):  # type: ignore
                    next_seq = make_autoname("INST-.####")
                    self.instrument_id = f"{next_seq}-{self.serial_no}"  # type: ignore
        except Exception as e:
            frappe.log_error(
                f"Instrument ID Auto-generation failed: {str(e)}", "Instrument: set_instrument_id"
            )
            frappe.throw("Unable to generate Instrument ID. Please contact your administrator.")


# -----------------------
# Internals
# -----------------------


def _get_instrument_serial_field_type() -> str | None:
    """
    Return the fieldtype of Instrument.serial_no ('Link' | 'Data' | None).
    """
    try:
        meta = frappe.get_meta("Instrument")
        df = meta.get_field("serial_no")
        return getattr(df, "fieldtype", None) if df else None
    except Exception:
        return None
