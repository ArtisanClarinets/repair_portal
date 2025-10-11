"""Central registry for cross-module constants."""

from __future__ import annotations

from enum import Enum
from functools import lru_cache
from typing import Iterable, List


class DocType(str, Enum):
    """Enumerated DocType names used across the app."""

    PLAYER_PROFILE = "Player Profile"
    REPAIR_ORDER = "Repair Order"
    REPAIR_LABOR_SESSION = "Repair Labor Session"
    REPAIR_QUOTATION = "Repair Quotation"
    REPAIR_SLA_POLICY = "Repair SLA Policy"
    REPAIR_PORTAL_SETTINGS = "Repair Portal Settings"
    REPAIR_SETTINGS = "Repair Settings"
    REPAIR_IMPORT_MAPPING = "Repair Import Mapping"
    REPAIR_QA_OUTCOME = "Repair QA Outcome"
    REPAIR_WARRANTY_ADJUSTMENT = "Repair Warranty Adjustment"
    MATERIAL_ISSUE = "Stock Entry"
    SALES_INVOICE = "Sales Invoice"
    SALES_ORDER = "Sales Order"
    CUSTOMER = "Customer"
    INSTRUMENT_PROFILE = "Instrument Profile"
    TOOL_USAGE_LOG = "Tool Usage Log"
    WARRANTY_STATUS = "Warranty Status"


class EventTopic(str, Enum):
    """Enumerated event topics for the application event bus."""

    REPAIR_ORDER_CREATED = "repair_order.created"
    REPAIR_ORDER_UPDATED = "repair_order.updated"
    REPAIR_ORDER_READY_FOR_QA = "repair_order.ready_for_qa"
    QA_PASSED = "repair_order.qa_passed"
    QA_FAILED = "repair_order.qa_failed"
    REPAIR_ORDER_COMPLETED = "repair_order.completed"
    REPAIR_ORDER_DELIVERED = "repair_order.delivered"
    SLA_STARTED = "sla.started"
    SLA_PAUSED = "sla.paused"
    SLA_RESUMED = "sla.resumed"
    SLA_BREACHED = "sla.breached"
    SLA_ESCALATED = "sla.escalated"
    INVENTORY_RESERVED = "inventory.reserved"
    INVENTORY_ISSUED = "inventory.issued"
    INVENTORY_RETURNED = "inventory.returned"
    INVENTORY_BACKORDERED = "inventory.backordered"
    BILLING_READY = "billing.ready"
    INVOICE_POSTED = "billing.invoice_posted"
    WARRANTY_ADJUSTED = "warranty.adjusted"
    CUSTOMER_MESSAGE_SENT = "customer.message_sent"


class QueueName(str, Enum):
    """Queue names used for async processing."""

    REPAIR_SLA = "Q_REPAIR_SLA"
    REPAIR_BILLING = "Q_REPAIR_BILLING"
    REPAIR_NOTIFY = "Q_REPAIR_NOTIFY"
    REPAIR_INVENTORY = "Q_REPAIR_INVENTORY"
    REPAIR_QA = "Q_REPAIR_QA"


class Role(str, Enum):
    """Application roles used throughout permissions checks."""

    TECHNICIAN = "Technician"
    REPAIR_MANAGER = "Repair Manager"
    QA = "QA"
    CUSTOMER_SERVICE = "Customer Service"
    ACCOUNTS = "Accounts"
    CUSTOMER = "Customer"


@lru_cache(maxsize=None)
def all_topics() -> List[str]:
    """Return all registered event topics as a list."""

    return [topic.value for topic in EventTopic]


@lru_cache(maxsize=None)
def all_roles() -> List[str]:
    """Return all registered application roles."""

    return [role.value for role in Role]


@lru_cache(maxsize=None)
def all_queues() -> List[str]:
    """Return all async queue names."""

    return [queue.value for queue in QueueName]


@lru_cache(maxsize=None)
def all_doctypes() -> List[str]:
    """Return all enumerated DocType names."""

    return [doctype.value for doctype in DocType]


def has_doctype(name: str) -> bool:
    """Check whether *name* is present in the DocType registry."""

    return name in all_doctypes()


def iter_topics(prefix: str | None = None) -> Iterable[str]:
    """Yield event topics, optionally filtered by *prefix*."""

    for topic in EventTopic:
        if prefix is None or topic.value.startswith(prefix):
            yield topic.value
