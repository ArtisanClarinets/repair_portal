# Path: repair_portal/repair_portal/instrument_profile/doctype/instrument_serial_number/instrument_serial_number.py
# Version: v2.1 (serial-only; uses utils/serials)
# Date: 2025-08-14
# Purpose: Strict serial-number handling. All instrument details belong to the Instrument DocType.
# This controller delegates normalization & linkage helpers to repair_portal.utils.serials
# so there's a single source of truth across the app.

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime

# Utilities (single source of truth for normalization and linkage)
from repair_portal.utils.serials import (
    normalize_serial as util_normalize_serial, # type: ignore
    attach_to_instrument as util_attach_isn,
    candidates as util_candidates,
)


class InstrumentSerialNumber(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from frappe.types import DF

        duplicate_of: DF.Link | None
        erpnext_serial_no: DF.Link | None
        instrument: DF.Link | None
        normalized_serial: DF.Data | None
        notes: DF.SmallText | None
        photo: DF.AttachImage | None
        scan_code: DF.Data | None
        serial: DF.Data
        serial_source: DF.Literal["Stamped", "Engraved", "Etched", "Label/Sticker", "Handwritten", "Unknown"] | None
        status: DF.Literal["Active", "Deprecated", "Replaced", "Error"]
        verification_status: DF.Literal["Unverified", "Verified by Technician", "Customer Reported", "Disputed"]
        verified_by: DF.Link | None
        verified_on: DF.Datetime | None
    # end: auto-generated types

    # -------- Lifecycle --------
    def before_insert(self):
        # Ensure normalized form exists as early as possible
        self._normalize()

    def validate(self):
        self._normalize()
        self._validate_requireds()
        self._validate_uniqueness()
        self._set_verification_meta()

    def after_insert(self):
        # If instrument is set, ensure Instrument.serial_no points to this ISN
        if self.instrument:
            try:
                util_attach_isn(isn_name=self.name, instrument=self.instrument, link_on_instrument=True) # type: ignore
            except Exception:
                # Non-fatal: log for admin review
                frappe.log_error(frappe.get_traceback(), "InstrumentSerialNumber.after_insert: attach Instrument link failed")

    def on_update(self):
        # Keep Instrument link in sync if user linked instrument after creation
        if self.instrument:
            try:
                util_attach_isn(isn_name=self.name, instrument=self.instrument, link_on_instrument=True) # type: ignore
            except Exception:
                frappe.log_error(frappe.get_traceback(), "InstrumentSerialNumber.on_update: attach Instrument link failed")

    # -------- Helpers --------
    def _normalize(self):
        # Use utils.normalize_serial as canonical implementation
        self.normalized_serial = util_normalize_serial(getattr(self, "serial", None))

    def _validate_requireds(self):
        if not self.serial:
            frappe.throw(_("Serial Number is required."))
        if not self.normalized_serial:
            frappe.throw(_("Normalized Serial could not be derived from the Serial Number."))

    def _validate_uniqueness(self):
        """
        Enforce sane uniqueness (no component dimension in this schema):
          - If the same Instrument already has this normalized serial, block.
          - Across different Instruments:
              • If Instruments share the same Brand (Instrument.brand), block (true duplicate for that maker).
              • Otherwise allow but advise using 'Duplicate Of' (different makers can share serial patterns).
          - If Instrument is not set:
              • If an unlinked record with the same normalized serial exists, block (ambiguous duplicate).
              • If only linked records exist, allow with advisory.
        """
        # Find possible collisions for this normalized serial
        if not self.normalized_serial:
            return
        candidates = frappe.get_all(
            "Instrument Serial Number",
            filters={"normalized_serial": self.normalized_serial},
            fields=["name", "instrument"],
            limit=100,
        )
        # Remove self from candidates
        candidates = [c for c in candidates if c.get("name") != self.name]

        if not candidates:
            return

        if self.instrument:
            # Block same-instrument duplicates
            same_instr = [c for c in candidates if c.get("instrument") == self.instrument]
            if same_instr:
                frappe.throw(
                    _("Duplicate serial for this Instrument already exists: {0}").format(same_instr[0]["name"])
                )

            # Compare brands across instruments
            my_brand = frappe.db.get_value("Instrument", self.instrument, "brand")
            for c in candidates:
                other_instr = c.get("instrument")
                if not other_instr:
                    # Unlinked twin: advisory
                    frappe.msgprint(
                        _("Another unlinked serial record exists with the same serial number: {0}").format(c["name"]),
                        alert=True,
                        indicator="orange",
                    )
                    continue
                other_brand = frappe.db.get_value("Instrument", other_instr, "brand")
                if my_brand and other_brand and my_brand == other_brand:
                    frappe.throw(
                        _("Duplicate serial for brand '{0}' detected across instruments: {1}").format(my_brand, c["name"])
                    )
            # Otherwise permitted (different brands). UI can optionally set duplicate_of.
            return

        # No Instrument set: block exact unlinked duplicate
        unlinked = [c for c in candidates if not c.get("instrument")]
        if unlinked:
            frappe.throw(
                _("A serial record with the same value already exists without an Instrument: {0}").format(unlinked[0]["name"])
            )

        # Only linked candidates exist — allow, but advise
        frappe.msgprint(
            _("Serial already exists on other instrument(s). Consider linking this record or using 'Duplicate Of'."),
            alert=True,
            indicator="orange",
        )

    def _set_verification_meta(self):
        if self.verification_status == "Verified by Technician":
            if not self.verified_by:
                self.verified_by = frappe.session.user
            if not self.verified_on:
                self.verified_on = now_datetime()

    # -------- Public API --------
    @frappe.whitelist()
    def attach_to_instrument(self, instrument: str):
        """Link this serial to an Instrument (and set Instrument.serial_no when available)."""
        if not frappe.db.exists("Instrument", instrument):
            frappe.throw(_("Instrument '{0}' not found.").format(instrument))
        util_attach_isn(isn_name=self.name, instrument=instrument, link_on_instrument=True) # type: ignore
        # Reflect linkage locally if not already set
        if self.instrument != instrument:
            self.instrument = instrument
            self.save(ignore_permissions=True)
        return {"ok": True, "instrument": instrument}

    @frappe.whitelist()
    def find_similar(self, limit: int = 20):
        """Return possible matches by normalized_serial, excluding self."""
        if not self.serial:
            return []
        rows = util_candidates(self.serial, limit=limit)
        # Exclude self
        rows = [r for r in (rows or []) if r.get("name") != self.name]
        return rows
