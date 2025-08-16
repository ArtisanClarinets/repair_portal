Here’s a complete, production-ready README.md you can drop next to serials.py. It documents purpose, API, return types, edge cases, and includes copy-paste examples for controllers, patches, and tests—aligned to the code we’ve been using across your intake and inspection flows.

Instrument Serial Utilities (serials.py)

Location (recommended):

/opt/frappe/erp-bench/apps/repair_portal/repair_portal/utils/serials.py


Purpose:
Single source of truth for musical instrument serial numbers in The Clarinet Wizard stack. This module:

Normalizes user-entered serials (preserves leading zeros, uppercases, strips punctuation).

Resolves raw/legacy serial tokens → Instrument Serial Number (ISN) records.

Idempotently creates ISN records when missing.

Optionally links ISNs to Instrument and syncs the Instrument.serial_no field (works whether that field is Link→ISN or legacy Data).

Provides safe helpers for controllers (intake, inspection, etc.).

This module never creates ERPNext Serial No (stock) records.

Design Goals

Idempotent & Deterministic: Re-calling creation helpers won’t duplicate rows.

Schema-Agnostic: Works whether Instrument.serial_no is a Link to ISN (modern) or Data (legacy).

Back-Compat: If a user pastes a legacy ERPNext “Serial No” name, we convert/ensure an ISN instead.

Low Surprise: Inputs like bb-0123 a normalize to BB0123A (leading zeros preserved).

“Fortune-500” Hardening: Clear exceptions, explicit returns, small surface area.

Quick Start
1) Import

Use the preferred path first; fallback if needed (keeps things resilient if app layout shifts):

try:
    from repair_portal.repair_portal.utils.serials import (
        normalize_serial,
        find_by_serial,
        ensure_instrument_serial,
        attach_to_instrument,
    )
except Exception:
    from repair_portal.utils.serials import (
        normalize_serial,
        find_by_serial,
        ensure_instrument_serial,
        attach_to_instrument,
    )

2) Ensure an ISN exists from any token
raw = " 1test "
isn_name = ensure_instrument_serial(
    serial_input=raw,           # raw user text, ERP Serial name, or already an ISN name
    instrument=None,            # or an Instrument name to link immediately
    link_on_instrument=False,   # True to set Instrument.serial_no
    status="Active",            # ISN.status literal
)
# -> returns the ISN docname (e.g., "ISN-0001" or the actual name), never None (throws on fatal)

3) Resolve an ISN without creating
row = find_by_serial("1test")
# -> dict or None, fields: {"name": <isn_name>, "instrument": <Instrument.name or None>, "normalized_serial": "1TEST", ...}

4) Link an existing ISN to an Instrument
attach_to_instrument(isn_name="ISN-0001", instrument="INST-0005", link_on_instrument=True)
# - Links ISN.instrument
# - If Instrument.serial_no is Link to ISN, sets that field to the ISN name
# - If Instrument.serial_no is Data, writes the raw serial token

API Reference
normalize_serial(s: str | None) -> str | None

Behavior: Uppercases; strips all non-alphanumeric; preserves leading zeros.

Examples:

" Bb-0123 a " → "BB0123A"

None or "" → None

find_by_serial(serial_input: str) -> dict | None

Resolves a token (raw stamped text, legacy ERP “Serial No” name, or ISN name) to an existing ISN row without creating anything.

Returns: dict with at least:

name: ISN docname

instrument: linked Instrument name or None

normalized_serial: normalized token

Returns None if no ISN matches.

Never throws unless DB/connectivity issues.

ensure_instrument_serial(serial_input: str, instrument: str | None = None, link_on_instrument: bool = False, status: str = "Active") -> str

Idempotently gets or creates the Instrument Serial Number and optionally links it to an Instrument.

Arguments:

serial_input – raw/legacy token (e.g., "1test" or ISN-xxxx).

instrument – Instrument name to link (None to skip).

link_on_instrument – If True, sets Instrument.serial_no appropriately (Link→ISN or Data).

status – ISN.status literal: "Active" | "Deprecated" | "Replaced" | "Error".

Returns: ISN docname (string).

Raises: frappe.ValidationError on empty/unusable input.

Guarantees:

If an ISN already exists for the normalized token, returns its name.

If not, creates one with:

serial set to the original input (trimmed),

normalized_serial set via normalize_serial,

status set as requested.

attach_to_instrument(isn_name: str, instrument: str, link_on_instrument: bool = True) -> dict

Ensures the two-way linkage:

Sets ISN.instrument = instrument.

If link_on_instrument:

If Instrument.serial_no is Link→ISN, assigns the ISN docname.

If Data, writes the raw serial token stored on the ISN.

Returns: {"ok": True, "instrument": "...", "isn": "..."}
Raises: frappe.DoesNotExistError for missing docs.

Controller Integration Patterns
Clarinet Intake (after_insert)

Create/resolve the ISN once and reuse:

serial_no_input = (self.serial_no or "").strip()
isn_name = None
if serial_no_input:
    row = find_by_serial(serial_no_input)
    isn_name = row["name"] if row else ensure_instrument_serial(serial_no_input, instrument=None, link_on_instrument=False)

# Create/find Instrument, then:
if isn_name and self.instrument:
    attach_to_instrument(isn_name=isn_name, instrument=self.instrument, link_on_instrument=True)

Instrument Inspection (before_validate)

Guarantee serial_no is an ISN docname before mandatory/link checks:

val = (self.serial_no or "").strip()
if val:
    row = find_by_serial(val)
    if row:
        self.serial_no = row["name"]
    else:
        self.serial_no = ensure_instrument_serial(val, instrument=getattr(self, "instrument", None), link_on_instrument=False)

Schema Expectations

Instrument Serial Number (DocType):

Fields: serial (Data), normalized_serial (Data), instrument (Link: Instrument), status (Select), verification_status, etc.

Instrument (DocType):

Field serial_no can be:

Link → Instrument Serial Number (preferred), or

Data (legacy; still supported by helpers).

Instrument Inspection (DocType):

Field serial_no should be Link → Instrument Serial Number (recommended).

If migrating from Link → Serial No (ERPNext), run the migration script (below) to backfill.

Migration (from ERPNext “Serial No” links to ISN)

Update DocField (Instrument Inspection.serial_no) to Link → Instrument Serial Number and remove fetch_from.

Backfill existing rows using this patch (already provided earlier):

/opt/frappe/erp-bench/apps/repair_portal/repair_portal/patches/v1_0/migrate_instrument_inspection_serial_to_isn.py


Register the patch in:

/opt/frappe/erp-bench/apps/repair_portal/repair_portal/patches.txt


Apply:

cd /home/frappe/frappe-bench
bench --site all migrate
bench --site all reload-doc repair_portal inspection instrument_inspection
bench --site all clear-cache
bench build
sudo supervisorctl restart frappe-bench-workers
sudo supervisorctl restart frappe-bench-web

Error Handling & Common Messages

LinkValidationError (was):
“Could not find Instrument Serial Number: 1TEST”
➜ Fixed by ensuring serial_no is an ISN docname before insert (ensure_instrument_serial or find_by_serial).

MandatoryError (was):
“[Instrument Inspection]: serial_no”
➜ Occurs if the field still points to ERPNext “Serial No”. Migrate the field to Link → Instrument Serial Number, or temporarily ignore_mandatory=True during insert (not recommended long-term).

Long error title (was):
frappe.log_error title exceeds 140 chars.
➜ Always call with title="Short", message="Long text...".

Copy-Paste Test Snippets
Frappe Console: smoke test creation
# bench --site yoursite console

from frappe import get_doc
from repair_portal.utils.serials import ensure_instrument_serial, find_by_serial, attach_to_instrument

# 1) Ensure ISN from raw
isn = ensure_instrument_serial("1test", instrument=None, link_on_instrument=False)
print("ISN:", isn)

# 2) Create an Instrument and link it
instr = get_doc({"doctype": "Instrument", "instrument_type": "B♭ Clarinet", "brand": "Buffet"})
instr.insert(ignore_permissions=True)
attach_to_instrument(isn, instr.name, link_on_instrument=True)

# 3) Resolve back
print(find_by_serial("1test"))

Unit-ish test (minimal)
def _assert(b, msg="assertion failed"):
    assert b, msg

name = ensure_instrument_serial("bb-0001", instrument=None, link_on_instrument=False)
row  = find_by_serial("BB0001")
_assert(row and row["name"] == name)

# Create an Instrument and link
import frappe
inst = frappe.get_doc({"doctype": "Instrument", "brand": "Selmer", "instrument_type": "A Clarinet"})
inst.insert(ignore_permissions=True)
attach_to_instrument(name, inst.name, link_on_instrument=True)

# Instrument.serial_no sync (Link→ISN or Data) is handled inside attach_to_instrument

Performance Notes

Lookups are indexed by normalized_serial for O(log N) queries at scale.

ensure_instrument_serial avoids duplicates by checking normalized value first.

Troubleshooting

Nothing links to the Instrument:
Ensure attach_to_instrument(..., link_on_instrument=True) is called after the Instrument exists.

Instrument.serial_no is Data but you want Link:

Add a Link field, migrate values from Data → Link via normalized lookup to ISN, then remove the Data field.

Helpers work fine during the interim.

Users paste ERP “Serial No” names:
The helpers accept that string and create/resolve an ISN (no ERP stock serials are created).

Security & Permissions

Helpers use insert(ignore_permissions=True) only for the ISN (controlled code path).

If you need stricter behavior, wrap calls in your own service layer and remove ignore_permissions as needed.

Changelog

2025-08-14: Initial public docs aligning with intake & inspection ISN-first flow; added migration guidance and examples.

License

Internal use for The Clarinet Wizard / MRW Artisan Instruments.
If you redistribute, preserve these notices.