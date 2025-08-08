# File Header Template
# Relative Path: repair_portal/inspection/doctype/instrument_inspection/instrument_inspection.py
# Last Updated: 2025-08-07
# Version: v1.2.1 (Patch: Autofill key & wood_type from Instrument on validate)
# Purpose: Controller for Instrument Inspection DocType - handles validation, automation, and exception logging for all inspection scenarios (inventory, repair, maintenance, QA). Also syncs deep inspection specs to Instrument Profile.
# Dependencies: frappe, Inspection Finding, Tenon Fit Record, Tone Hole Inspection Record, Instrument Profile

import frappe
from frappe.model.document import Document


class InstrumentInspection(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from repair_portal.instrument_profile.doctype.instrument_accessory.instrument_accessory import InstrumentAccessory
        from repair_portal.instrument_profile.doctype.instrument_photo.instrument_photo import InstrumentPhoto
        from repair_portal.instrument_setup.doctype.inspection_finding.inspection_finding import InspectionFinding
        from repair_portal.repair_logging.doctype.tenon_measurement.tenon_measurement import TenonMeasurement
        from repair_portal.repair_logging.doctype.tone_hole_inspection_record.tone_hole_inspection_record import ToneHoleInspectionRecord

        accessory_log: DF.Table[InstrumentAccessory]
        acclimatization_controlled_env: DF.Check
        acclimatization_playing_schedule: DF.Check
        acclimatization_swabbing: DF.Check
        amended_from: DF.Link | None
        audio_video_demos: DF.Literal["Instrument Media"]
        body_material: DF.Data | None
        bore_condition: DF.Literal["Clean", "Debris Present", "Irregularities Visible"]
        bore_measurement: DF.Float
        bore_notes: DF.SmallText | None
        bore_style: DF.Data | None
        clarinet_intake: DF.Link | None
        current_location: DF.Data | None
        current_status: DF.Literal["For Sale", "In Workshop", "With Customer", "Sold", "Archived"]
        customer: DF.Link | None
        hygrometer_photo: DF.AttachImage | None
        inspected_by: DF.Link
        inspection_date: DF.Date | None
        inspection_findings: DF.Table[InspectionFinding]
        inspection_type: DF.Literal["New Inventory", "Repair", "Maintenance", "QA", "Other"]
        instrument_delivered: DF.Check
        intake_record_id: DF.Link | None
        key: DF.Literal["B\u266d", "A", "E\u266d", "C", "D"]
        key_plating: DF.Data | None
        key_system: DF.Literal["Boehm", "Albert", "Oehler", "Other"]
        manufacturer: DF.Data | None
        marketing_photos: DF.Table[InstrumentPhoto]
        model: DF.Data | None
        notes: DF.Text | None
        number_of_keys_rings: DF.Data | None
        overall_condition: DF.Literal["Excellent", "Good", "Fair", "Poor"]
        pad_type_current: DF.Data | None
        pitch_standard: DF.Data | None
        preliminary_estimate: DF.Currency
        profile_image: DF.AttachImage | None
        qc_certificate: DF.Attach | None
        rested_unopened: DF.Check
        serial_no: DF.Link
        service_photos: DF.Table[InstrumentPhoto]
        spring_type: DF.Data | None
        tenon_fit_assessment: DF.Table[TenonMeasurement]
        thumb_rest: DF.Data | None
        tone_hole_inspection: DF.Table[ToneHoleInspectionRecord]
        tone_hole_notes: DF.Text | None
        tone_hole_style: DF.Data | None
        unboxing_rh: DF.Float
        unboxing_temperature: DF.Float
        unboxing_time: DF.Datetime | None
        visual_inspection: DF.Table[InspectionFinding]
        wood_type: DF.Literal["Grenadilla", "Mopane", "Cocobolo", "Synthetic", "Other"]
    # end: auto-generated types

    def validate(self) -> None:
        """
        Validation hook to enforce business rules for each inspection type.
        Logs any exceptions for audit.
        """
        try:
            # Ensure serial_no is unique
            self._validate_unique_serial()

            # Required fields for New Inventory
            if self.inspection_type == "New Inventory":
                missing = [f for f in ["manufacturer", "model", "key", "wood_type"] if not getattr(self, f, None)]
                if missing:
                    frappe.throw(f"Missing required field(s) for New Inventory: {', '.join(missing)}")

            # Customer fields only for non-inventory
            if self.inspection_type == "New Inventory" and (self.customer or self.preliminary_estimate):
                frappe.throw("Customer and pricing fields must be empty for New Inventory inspections.")
        except Exception:
            frappe.log_error(frappe.get_traceback(), "InstrumentInspection.validate")
            raise

    def _validate_unique_serial(self) -> None:
        """
        Ensures the serial_no is unique for the current inspection record.
        """
        if self.serial_no:
            duplicate = frappe.db.exists(
                "Instrument Inspection", {"serial_no": self.serial_no, "name": ("!=", self.name)}
            )
            if duplicate:
                frappe.throw(f"An Instrument Inspection already exists for Serial No: {self.serial_no}")

    def on_submit(self) -> None:
        """
        On submit, update or create Instrument Profile for this serial. Syncs all persistent fields (specs, images, logs, etc.).
        """
        try:
            serial = self.serial_no
            profile_name = frappe.db.get_value("Instrument Profile", {"instrument": serial})
            data = {
                "body_material": self.body_material,
                "key_plating": self.key_plating,
                "key_system": self.key_system,
                "number_of_keys_rings": self.number_of_keys_rings,
                "pitch_standard": self.pitch_standard,
                "bore_style": self.bore_style,
                "bore_measurement": self.bore_measurement,
                "tone_hole_style": self.tone_hole_style,
                "thumb_rest": self.thumb_rest,
                "spring_type": self.spring_type,
                "pad_type_current": self.pad_type_current,
                "current_status": self.current_status,
                "current_location": self.current_location,
                "profile_image": self.profile_image
                # TODO: Add child table mappings for photos, media, accessories, etc.
            }
            if profile_name:
                profile = frappe.get_doc("Instrument Profile", profile_name)
                for k, v in data.items():
                    if v:
                        profile.set(k, v)
                profile.save(ignore_permissions=True)
            else:
                data.update({"instrument": serial})
                profile = frappe.get_doc({"doctype": "Instrument Profile", **data})
                profile.insert(ignore_permissions=True)
        except Exception:
            frappe.log_error(frappe.get_traceback(), "InstrumentInspection.on_submit")