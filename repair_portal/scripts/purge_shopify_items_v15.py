#!/usr/bin/env python3
"""
 purge_shopify_items_v15.py
 --------------------------
Remove all Items + Item Attributes that were created by the
`shopify_to_erpnext_v15.py` import script.

!!! ⚠️  DANGER ZONE !!!
    • This *physically* deletes documents.  Take a fresh backup first.
    • Run in a non-production or staging site until you’re 100 % sure.

Environment
-----------
ERPNEXT_URL         → Site URL   (default: https://erp.artisanclarinets.com)
ERPNEXT_API_KEY     → API key
ERPNEXT_API_SECRET  → API secret
CSV_PATH            → Path to the same Shopify CSV (default: shopify/shopify_clarinets.csv)
DRY_RUN             → If set to "1" just print what *would* be deleted.
"""

import csv
import os
import sys
from pathlib import Path
from typing import Dict, List

import requests

# ── 1.  CONFIG ─────────────────────────────────────────────────────────────────
URL       = os.getenv("ERPNEXT_URL", "https://erp.artisanclarinets.com").rstrip("/")
API_KEY   = os.getenv("ERPNEXT_API_KEY")
API_SEC   = os.getenv("ERPNEXT_API_SECRET")
CSV_FILE  = Path(os.getenv("CSV_PATH", "shopify/shopify_clarinets.csv"))
DRY_RUN   = os.getenv("DRY_RUN") == "1"

if not (API_KEY and API_SEC):
    sys.exit("❌  ERPNEXT_API_KEY / ERPNEXT_API_SECRET are required.")

# ── 2.  SESSION ───────────────────────────────────────────────────────────────
sess = requests.Session()
sess.headers.update({
    "Authorization": f"token {API_KEY}:{API_SEC}",
    "Accept":        "application/json"
})
sess.timeout = 20


def delete_doc(doctype: str, name: str) -> bool:
    """DELETE /api/resource/<doctype>/<name>  (returns True on success)"""
    url = f"{URL}/api/resource/{doctype}/{name}"
    if DRY_RUN:
        print(f"DRY-RUN  would DELETE  {doctype} ‹{name}›")
        return True
    r = sess.delete(url)
    if r.ok:
        print(f"🗑️   Deleted {doctype} ‹{name}›")
        return True
    print(f"⚠️  Couldn’t delete {doctype} ‹{name}› → {r.status_code}: {r.text}")
    return False


# ── 3.  COLLECT CODES + ATTRIBUTES FROM CSV ───────────────────────────────────
if not CSV_FILE.exists():
    sys.exit(f"❌  CSV not found: {CSV_FILE}")

variants:   List[str] = []
templates:  List[str] = []
solo_items: List[str] = []
attributes: set[str] = set()

with CSV_FILE.open(encoding="utf-8") as f:
    for row in csv.DictReader(f):
        handle = row["Handle"]
        var_sku = row.get("Variant SKU")
        opt1    = row.get("Option1 Name")
        opt2    = row.get("Option2 Name")
        opt3    = row.get("Option3 Name")

        # attribute names
        for opt in (opt1, opt2, opt3):
            if opt and opt.lower() != "title":
                attributes.add(opt)

        # decide whether this row is a variant or standalone
        if var_sku:
            variants.append(var_sku)
        elif any(row.get(f"Option{i} Name") and row.get(f"Option{i} Name") != "Title"
                 for i in (1, 2, 3)):
            # template row
            templates.append(handle)
        else:
            solo_items.append(var_sku or handle)

print(f"🔍  Found {len(variants)} variants, {len(templates)} templates, "
      f"{len(solo_items)} stand-alone items and {len(attributes)} attributes.")

# ── 4.  KILL THE ITEMS (variants → templates → solos) ─────────────────────────
for code in variants:
    delete_doc("Item", code)

for code in templates:
    delete_doc("Item", code)

for code in solo_items:
    delete_doc("Item", code)

# ── 5.  TRY TO DROP ATTRIBUTES ────────────────────────────────────────────────
for attr in attributes:
    delete_doc("Item Attribute", attr)

print("\n🎯  Purge finished.  If anything is still present, it’s because "
      "ERPNext reported a link-constraint (open transactions, BOMs, etc.).")