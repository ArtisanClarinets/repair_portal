#!/usr/bin/env python3
"""
 shopify_to_erpnext_v15.py
 -------------------------
 Import Shopify product CSV → ERPNext v15 (Items + Variants).

 • Uses token-based auth (API Key + API Secret) via simple requests.Session.
 • Auto-creates Item Attributes *and* missing Attribute Values.
 • Adds mandatory v15 fields (e.g. stock_uom).
 • Idempotent: skips anything that already exists.
"""

import csv
import json
import os
import sys
from pathlib import Path
from typing import Dict, List

import requests

# ── 1.  CONNECTION DETAILS ──────────────────────────────────────────────────────
ERPNEXT_URL      = os.getenv("ERPNEXT_URL",      "https://erp.artisanclarinets.com")
ERPNEXT_API_KEY  = os.getenv("ERPNEXT_API_KEY",  "8de5f0ab8e9f450")
ERPNEXT_API_SEC  = os.getenv("ERPNEXT_API_SECRET", "cf25a10c7dae5d4")

# ── 2.  INPUT CSV ───────────────────────────────────────────────────────────────
CSV_FILE         = Path("shopify/shopify_clarinets.csv")

# ── 3.  SESSION INITIALISATION ─────────────────────────────────────────────────
sess = requests.Session()
sess.headers.update({
    "Authorization": f"token {ERPNEXT_API_KEY}:{ERPNEXT_API_SEC}",
    "Content-Type":  "application/json"
})
sess.timeout = 20        # seconds


# ── 4.  HELPER WRAPPERS AROUND REST END-POINTS ─────────────────────────────────
def doc_exists(doctype: str, name: str) -> bool:
    """Quick existence check (GET /api/resource/DocType/name)."""
    url = f"{ERPNEXT_URL}/api/resource/{doctype}/{name}"
    r = sess.get(url)
    return r.status_code == 200


def create_doc(doctype: str, payload: Dict) -> Dict | None:
    """Insert a document and return the created JSON data (or None on failure)."""
    url = f"{ERPNEXT_URL}/api/resource/{doctype}"
    r = sess.post(url, json=payload)
    if r.ok:
        return r.json()["data"]
    print(f"❌  {doctype} insert failed → {r.status_code}: {r.text}")
    return None


def update_doc(doctype: str, name: str, payload: Dict) -> bool:
    url = f"{ERPNEXT_URL}/api/resource/{doctype}/{name}"
    r = sess.put(url, json=payload)
    if r.ok:
        return True
    print(f"❌  {doctype} update failed → {r.status_code}: {r.text}")
    return False


# ── 5.  ATTRIBUTE MANAGEMENT ───────────────────────────────────────────────────
def ensure_attribute_and_value(attr_name: str, value: str | None = None) -> None:
    """
    • Create Item Attribute if missing.
    • Ensure the passed 'value' is listed under item_attribute_values.
    """
    doctype = "Item Attribute"
    if not doc_exists(doctype, attr_name):
        create_doc(doctype, {
            "doctype": doctype,
            "attribute_name": attr_name,
            "item_attribute_values": (
                [{"attribute_value": value}] if value else []
            )
        })
        return

    if value:
        # Make sure the value is present
        url = f"{ERPNEXT_URL}/api/resource/{doctype}/{attr_name}"
        current = sess.get(url).json()["data"]
        existing_vals = {v["attribute_value"] for v in current.get("item_attribute_values", [])}
        if value not in existing_vals:
            current["item_attribute_values"].append({"attribute_value": value})
            update_doc(doctype, attr_name, {
                "item_attribute_values": current["item_attribute_values"]
            })


# ── 6.  MAIN IMPORT LOGIC ──────────────────────────────────────────────────────
def process_products(products: Dict[str, List[Dict]]):
    for handle, rows in products.items():
        template_row = rows[0]
        is_template  = any(r.get("Option1 Name") and r.get("Option1 Name") != "Title" for r in rows)

        if is_template:
            template_code = template_row["Handle"]
            if doc_exists("Item", template_code):
                print(f"⏭️  Template '{template_code}' exists, skipping.")
                continue

            # Build attribute list
            attributes = []
            for i in range(1, 4):
                attr = template_row.get(f"Option{i} Name")
                if not attr:
                    continue
                ensure_attribute_and_value(attr)       # no value yet – template only
                attributes.append({"attribute": attr})

            item_template = {
                "doctype":        "Item",
                "item_code":      template_code,
                "item_name":      template_row["Title"],
                "item_group":     template_row.get("Product Category") or "All Item Groups",
                "brand":          template_row.get("Vendor"),
                "description":    template_row.get("Body (HTML)"),
                "stock_uom":      "Nos",               # mandatory in v15
                "has_variants":   1,
                "variant_based_on": "Item Attribute",
                "attributes":     attributes
            }
            print(f"➕  Creating template {template_code} ...")
            if not create_doc("Item", item_template):
                continue
            print(f"✅  Template '{template_code}' created.")

            # Variants
            for row in rows:
                if not row.get("Variant SKU"):
                    continue
                variant_code = row["Variant SKU"]
                if doc_exists("Item", variant_code):
                    print(f"  ⏭️  Variant '{variant_code}' exists.")
                    continue

                variant_attrs = []
                for i in range(1, 4):
                    attr_name  = row.get(f"Option{i} Name")
                    attr_value = row.get(f"Option{i} Value")
                    if attr_name and attr_value:
                        ensure_attribute_and_value(attr_name, attr_value)
                        variant_attrs.append({
                            "attribute":       attr_name,
                            "attribute_value": attr_value
                        })

                variant_doc = {
                    "doctype":     "Item",
                    "item_code":   variant_code,
                    "item_name":   row["Title"],
                    "item_group":  row.get("Product Category") or "All Item Groups",
                    "brand":       row.get("Vendor"),
                    "stock_uom":   "Nos",
                    "variant_of":  template_code,
                    "attributes":  variant_attrs
                }
                print(f"  ➕  Creating variant {variant_code} ...")
                if create_doc("Item", variant_doc):
                    print(f"  ✅  Variant '{variant_code}' created.")
        else:
            # Stand-alone item
            item_code = template_row.get("Variant SKU") or template_row["Handle"]
            if doc_exists("Item", item_code):
                print(f"⏭️  Item '{item_code}' exists.")
                continue

            item_doc = {
                "doctype":     "Item",
                "item_code":   item_code,
                "item_name":   template_row["Title"],
                "item_group":  template_row.get("Product Category") or "All Item Groups",
                "brand":       template_row.get("Vendor"),
                "description": template_row.get("Body (HTML)"),
                "stock_uom":   "Nos",
                "has_variants": 0
            }
            print(f"➕  Creating item {item_code} ...")
            if create_doc("Item", item_doc):
                print(f"✅  Item '{item_code}' created.")


# ── 7.  ENTRY-POINT ────────────────────────────────────────────────────────────
def main() -> None:
    # 1. Quick connectivity check
    ping = sess.get(f"{ERPNEXT_URL}/api/method/frappe.auth.get_logged_user")
    if not ping.ok:
        print("❌  Cannot authenticate. Check API key/secret and user permissions.")
        sys.exit(1)
    print(f"🔐  Authenticated as: {ping.json().get('message')}")

    # 2. Read Shopify CSV
    if not CSV_FILE.exists():
        print(f"❌  CSV file not found: {CSV_FILE}")
        sys.exit(1)

    products: Dict[str, List[Dict]] = {}
    with CSV_FILE.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            products.setdefault(row["Handle"], []).append(row)

    print(f"📦  {len(products)} unique product handles found.")
    process_products(products)
    print("\n🎉  Import complete.")


if __name__ == "__main__":
    main()