"""Controller for Clarinet Estimator Pricing Rule."""

from __future__ import annotations

from frappe import _, throw
from frappe.model.document import Document
from frappe.utils import flt


class ClarinetEstimatorPricingRule(Document):
    """Pricing component that maps diagram regions to parts and labor presets."""

    def validate(self) -> None:  # noqa: D401
        if not self.region_id:
            throw(_("Region ID is required."))
        if not self.region_label:
            throw(_("Region Label is required."))
        if flt(self.part_quantity or 0) < 0:
            throw(_("Part Quantity cannot be negative."))
        if flt(self.labor_hours or 0) < 0:
            throw(_("Labor Hours cannot be negative."))
        if flt(self.labor_rate or 0) < 0:
            throw(_("Labor Rate cannot be negative."))
        if flt(self.family_multiplier or 0) <= 0:
            throw(_("Family Multiplier must be greater than zero."))
        if flt(self.rush_multiplier or 0) <= 0:
            throw(_("Rush Multiplier must be greater than zero."))
        if (self.part_item and not self.part_quantity) or (not self.part_item and self.part_quantity not in (None, 0)):
            throw(_("Provide both Part Item and Part Quantity for parts mapping."))
        if self.eta_days is not None and self.eta_days < 0:
            throw(_("ETA Days cannot be negative."))
        if self.priority is not None and self.priority < 0:
            throw(_("Priority cannot be negative."))
