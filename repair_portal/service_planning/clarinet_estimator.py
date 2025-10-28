"""Clarinet estimator domain logic shared between portal and tests."""

from __future__ import annotations

import io
import json
from dataclasses import dataclass
from typing import Iterable, List, Sequence

import frappe
from frappe import _, throw
from frappe.model.document import Document
from frappe.utils import flt
from frappe.utils.file_manager import save_file

from repair_portal.customer.security import customers_for_user, ensure_customer_access


INSTRUMENT_FAMILIES = [
    "B\u266d Clarinet",
    "A Clarinet",
    "E\u266d Clarinet",
    "C Clarinet",
    "Bass Clarinet",
]


@dataclass(frozen=True)
class PricingRule:
    name: str
    instrument_family: str
    region_id: str
    region_label: str
    component_type: str
    task_description: str
    part_item: str | None
    part_quantity: float
    labor_hours: float
    labor_rate: float
    family_multiplier: float
    rush_multiplier: float
    eta_days: int
    priority: int
    notes: str | None


@dataclass
class UploadedPhoto:
    filename: str
    content: bytes
    caption: str | None = None


@dataclass
class EstimatorResult:
    estimate_name: str
    artifact_name: str
    total: float
    eta_days: int
    line_items: List[dict]


def get_pricing_rules(instrument_family: str) -> List[PricingRule]:
    """Return pricing rules for the given family ordered by priority."""

    if instrument_family not in INSTRUMENT_FAMILIES:
        throw(_("Unsupported instrument family: {0}").format(instrument_family))

    rows = frappe.get_all(
        "Clarinet Estimator Pricing Rule",
        filters={"instrument_family": instrument_family, "is_active": 1},
        fields=[
            "name",
            "instrument_family",
            "region_id",
            "region_label",
            "component_type",
            "task_description",
            "part_item",
            "part_quantity",
            "labor_hours",
            "labor_rate",
            "family_multiplier",
            "rush_multiplier",
            "eta_days",
            "priority",
            "notes",
        ],
        order_by="priority asc, region_label asc, component_type asc",
    )

    return [
        PricingRule(
            name=row["name"],
            instrument_family=row["instrument_family"],
            region_id=row["region_id"],
            region_label=row["region_label"],
            component_type=row["component_type"],
            task_description=row["task_description"],
            part_item=row.get("part_item"),
            part_quantity=flt(row.get("part_quantity") or 0),
            labor_hours=flt(row.get("labor_hours") or 0),
            labor_rate=flt(row.get("labor_rate") or 0),
            family_multiplier=flt(row.get("family_multiplier") or 1),
            rush_multiplier=flt(row.get("rush_multiplier") or 1),
            eta_days=int(row.get("eta_days") or 0),
            priority=int(row.get("priority") or 0),
            notes=row.get("notes"),
        )
        for row in rows
    ]


def group_rules_by_region(rules: Sequence[PricingRule]) -> dict[str, List[PricingRule]]:
    grouped: dict[str, List[PricingRule]] = {}
    for rule in rules:
        grouped.setdefault(rule.region_id, []).append(rule)
    return grouped


def lookup_item_rate(item_code: str) -> float:
    doc = frappe.get_cached_doc("Item", item_code)
    for field in ("standard_rate", "last_purchase_rate", "valuation_rate"):
        value = flt(getattr(doc, field, 0))
        if value:
            return value
    throw(_("Item {0} is missing a selling rate.").format(item_code))


def _build_line_items(
    selected_rules: Iterable[PricingRule],
    expedite: bool,
) -> tuple[List[dict], List[dict], float, int]:
    line_items: List[dict] = []
    selections: List[dict] = []
    total = 0.0
    eta_days = 0

    for rule in selected_rules:
        part_amount = 0.0
        part_rate = 0.0
        if rule.part_item:
            part_rate = lookup_item_rate(rule.part_item)
            quantity = rule.part_quantity or 1.0
            part_amount = flt(quantity * part_rate)
            line_items.append(
                {
                    "region_id": rule.region_id,
                    "component_type": rule.component_type,
                    "line_role": "Part",
                    "description": _("{0} – {1} (Part)").format(rule.task_description, rule.region_label),
                    "part_code": rule.part_item,
                    "quantity": quantity,
                    "hours": 0,
                    "rate": part_rate,
                    "amount": part_amount,
                }
            )

        labor_amount = 0.0
        adjusted_rate = 0.0
        if rule.labor_hours:
            if not rule.labor_rate:
                throw(_("Labor rate missing for {0}").format(rule.task_description))
            adjusted_rate = flt(rule.labor_rate * rule.family_multiplier)
            if expedite:
                adjusted_rate = flt(adjusted_rate * rule.rush_multiplier)
            labor_amount = flt(rule.labor_hours * adjusted_rate)
            line_items.append(
                {
                    "region_id": rule.region_id,
                    "component_type": rule.component_type,
                    "line_role": "Labor",
                    "description": _("{0} – {1} Labor").format(rule.task_description, rule.region_label),
                    "part_code": None,
                    "quantity": rule.labor_hours,
                    "hours": rule.labor_hours,
                    "rate": adjusted_rate,
                    "amount": labor_amount,
                }
            )

        eta_days = max(eta_days, rule.eta_days)
        line_total = flt(part_amount + labor_amount)
        total += line_total
        selections.append(
            {
                "region_id": rule.region_id,
                "region_label": rule.region_label,
                "component_type": rule.component_type,
                "task_description": rule.task_description,
                "part_item": rule.part_item,
                "part_quantity": rule.part_quantity,
                "part_rate": part_rate,
                "labor_hours": rule.labor_hours,
                "labor_rate": adjusted_rate,
                "line_total": line_total,
                "notes": rule.notes,
            }
        )

    if expedite and eta_days:
        eta_days = max(2, eta_days - 2)

    return line_items, selections, flt(total), eta_days


def _resolve_customer(user: str) -> str:
    linked = customers_for_user(user)
    if not linked:
        throw(_("Portal user is not linked to a Customer."))
    if len(linked) > 1:
        frappe.logger().warning("Portal user %s linked to multiple customers; using first", user)
    return linked[0]


def _find_existing_estimate(customer: str, instrument_serial: str) -> Document | None:
    name = frappe.db.get_value(
        "Repair Estimate",
        {"customer": customer, "instrument_serial": instrument_serial, "docstatus": 0},
    )
    if name:
        return frappe.get_doc("Repair Estimate", name)
    return None


def _find_or_create_artifact(estimate_name: str) -> Document | None:
    existing = frappe.db.get_value(
        "Clarinet Pad Map Artifact",
        {"repair_estimate": estimate_name},
    )
    if existing:
        return frappe.get_doc("Clarinet Pad Map Artifact", existing)
    return None


def process_estimate_submission(
    *,
    user: str,
    instrument_family: str,
    serial: str,
    condition_score: int,
    expedite: bool,
    selections: Sequence[str],
    notes: str | None,
    photo_uploads: Sequence[UploadedPhoto],
) -> EstimatorResult:
    """Create/update a Repair Estimate and linked Pad Map Artifact."""

    if not selections:
        throw(_("Select at least one region on the diagram."))
    if not serial:
        throw(_("Serial number is required."))
    if condition_score < 0 or condition_score > 100:
        throw(_("Condition score must be between 0 and 100."))

    customer = _resolve_customer(user)
    ensure_customer_access(customer, user)

    all_rules = get_pricing_rules(instrument_family)
    if not all_rules:
        throw(_("No pricing rules configured for {0}").format(instrument_family))

    grouped_rules = group_rules_by_region(all_rules)
    selected_rule_rows: List[PricingRule] = []
    for region_id in selections:
        region_rules = grouped_rules.get(region_id)
        if not region_rules:
            throw(_("Region {0} is not configured for {1}").format(region_id, instrument_family))
        selected_rule_rows.extend(region_rules)

    line_items, selection_rows, total, eta_days = _build_line_items(selected_rule_rows, expedite)

    estimate = _find_existing_estimate(customer, serial)
    if estimate is None:
        estimate = frappe.get_doc({"doctype": "Repair Estimate"})
    estimate.customer = customer
    estimate.instrument_family = instrument_family
    estimate.instrument_serial = serial
    estimate.condition_score = condition_score
    estimate.rush_service = 1 if expedite else 0
    estimate.estimator_notes = notes
    estimate.eta_days = eta_days
    estimate.set("line_items", [])
    for item in line_items:
        estimate.append("line_items", item)
    estimate.save(ignore_permissions=False)

    artifact = _find_or_create_artifact(estimate.name)
    if artifact is None:
        artifact = frappe.get_doc({"doctype": "Clarinet Pad Map Artifact"})
        artifact.customer = customer
        artifact.repair_estimate = estimate.name
        artifact.instrument_family = instrument_family
        artifact.instrument_serial = serial
        artifact.condition_score = condition_score
        artifact.rush_service = 1 if expedite else 0
        artifact.eta_days = eta_days
        artifact.estimated_total = total
        artifact.notes = notes
        artifact.flags.ignore_validate = True
        artifact.flags.ignore_mandatory = True
        artifact.insert(ignore_permissions=False)
        artifact.flags.ignore_validate = False
        artifact.flags.ignore_mandatory = False
    else:
        ensure_customer_access(artifact.customer, user)

    artifact.customer = customer
    artifact.repair_estimate = estimate.name
    artifact.instrument_family = instrument_family
    artifact.instrument_serial = serial
    artifact.condition_score = condition_score
    artifact.rush_service = 1 if expedite else 0
    artifact.eta_days = eta_days
    artifact.estimated_total = total
    artifact.notes = notes

    instrument_profile = frappe.db.get_value(
        "Instrument Profile",
        {"serial_no": serial},
        "name",
    )
    if instrument_profile:
        artifact.instrument_profile = instrument_profile
        estimate.instrument_profile = instrument_profile

    artifact.set("selections", [])
    for row in selection_rows:
        artifact.append("selections", row)

    if photo_uploads:
        artifact.set("photos", [])
        for upload in photo_uploads:
            content = upload.content
            if isinstance(content, io.BytesIO):
                content = content.getvalue()
            saved = save_file(
                upload.filename,
                content,
                artifact.doctype,
                artifact.name,
                is_private=1,
            )
            artifact.append(
                "photos",
                {
                    "file": saved.name,
                    "caption": upload.caption or upload.filename,
                },
            )
    elif not artifact.photos:
        throw(_("At least one photo is required."))

    artifact.save()
    estimate.pad_map_artifact = artifact.name
    estimate.total_cost = total
    estimate.save()

    return EstimatorResult(
        estimate_name=estimate.name,
        artifact_name=artifact.name,
        total=total,
        eta_days=eta_days,
        line_items=line_items,
    )


def serialize_rules_for_portal(instrument_family: str) -> dict:
    rules = get_pricing_rules(instrument_family)
    grouped = group_rules_by_region(rules)
    regions: dict[str, dict] = {}
    for region, rows in grouped.items():
        if not rows:
            continue
        label = rows[0].region_label
        components = []
        for r in rows:
            part_rate = lookup_item_rate(r.part_item) if r.part_item else 0.0
            components.append(
                {
                    "component_type": r.component_type,
                    "task_description": r.task_description,
                    "part_item": r.part_item,
                    "part_quantity": r.part_quantity,
                    "part_rate": part_rate,
                    "labor_hours": r.labor_hours,
                    "labor_rate": r.labor_rate,
                    "family_multiplier": r.family_multiplier,
                    "rush_multiplier": r.rush_multiplier,
                    "eta_days": r.eta_days,
                    "notes": r.notes,
                }
            )
        regions[region] = {
            "label": label,
            "components": components,
        }
    return {
        "instrument_family": instrument_family,
        "regions": regions,
    }


def parse_selections(value: str | Sequence[str]) -> List[str]:
    if isinstance(value, (list, tuple)):
        return [str(v) for v in value]
    try:
        parsed = json.loads(value)
    except (TypeError, json.JSONDecodeError):
        throw(_("Invalid selections payload."))
    if not isinstance(parsed, list):
        throw(_("Selections payload must be a list."))
    return [str(v) for v in parsed]
