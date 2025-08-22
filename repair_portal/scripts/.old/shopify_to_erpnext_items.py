#!/usr/bin/env python3
"""
shopify_to_erpnext_items.py · Shopify CSV → ERPNext “Item” import (v15-safe)

Run:
  python shopify_to_erpnext_items.py \
    --input    /path/to/shopify_clarinets.csv \
    --template /path/to/Item.csv \
    --output   /path/to/erpnext_items_from_shopify.csv
"""

import argparse
import csv
import sys
from pathlib import Path


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def lb_to_g(lb: float) -> float:  # pounds → grams
    return round(lb * 453.592, 3)


def kg_to_g(kg: float) -> float:  # kilograms → grams
    return round(kg * 1000, 3)


def safe_float(val, default=0.0):
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def first_present(names, header_set):
    """Return the first column name that actually exists in the template."""
    return next((n for n in names if n in header_set), None)


# --------------------------------------------------------------------------- #
def convert(shopify_csv: Path, item_template_csv: Path, output_csv: Path):
    # 1) Grab ERPNext template header so we stay 100 % compliant
    with item_template_csv.open(newline='', encoding='utf-8-sig') as f:
        template_header = next(csv.reader(f))
    header_set = set(template_header)

    # 2) Map only to columns that really exist
    F = lambda *c: first_present(c, header_set)  # shorthand

    COL = {
        'code': F('Item Code'),
        'name': F('Item Name'),
        'group': F('Item Group'),
        'desc': F('Description'),
        'uom': F('Default Unit of Measure'),
        'stock_flag': F('Maintain Stock'),
        'opening': F('Opening Stock'),
        'sell_rate': F('Standard Selling Rate'),
        'cost_rate': F('Valuation Rate', 'Standard Rate'),
        'barcode': F('Barcode (Barcodes)', 'Barcode'),
        'weight': F('Weight Per Unit'),
        'weight_uom': F('Weight UOM'),
    }

    # 3) Pull Shopify export (forward-fill product-level columns)
    with shopify_csv.open(newline='', encoding='utf-8-sig') as f:
        raw = list(csv.DictReader(f))

    ffill = ['Title', 'Body (HTML)', 'Type']
    last = {k: '' for k in ffill}
    shop_rows = []
    for r in raw:
        for k in ffill:  # forward fill
            last[k] = r[k] or last[k]
            r[k] = last[k]
        if r.get('Variant SKU'):  # only real SKUs
            shop_rows.append(r)

    # 4) Build ERPNext-ready rows
    erp_rows = []
    for s in shop_rows:
        row = dict.fromkeys(template_header, '')

        # ─ basic mappings ─ #
        if COL['code']:
            row[COL['code']] = s['Variant SKU']
        if COL['name']:
            row[COL['name']] = s['Title']
        if COL['group']:
            row[COL['group']] = s['Type']
        if COL['desc']:
            row[COL['desc']] = s['Body (HTML)']

        # ─ constants & flags ─ #
        if COL['uom']:
            row[COL['uom']] = 'Nos'
        if COL['stock_flag']:
            row[COL['stock_flag']] = 1

        # ─ inventory & pricing ─ #
        if COL['opening']:
            row[COL['opening']] = safe_float(s.get('Variant Inventory Qty', 0))
        if COL['sell_rate']:
            row[COL['sell_rate']] = safe_float(s.get('Variant Price', 0))
        if COL['cost_rate']:
            row[COL['cost_rate']] = safe_float(s.get('Cost per item', 0))

        # ─ barcode ─ #
        if COL['barcode'] and s.get('Variant Barcode'):
            row[COL['barcode']] = s['Variant Barcode']

        # ─ weight logic ─ #
        grams = safe_float(s.get('Variant Grams', 0))
        unit = (s.get('Variant Weight Unit') or '').lower()
        if unit == 'lb':
            grams = lb_to_g(safe_float(s.get('Variant Weight', 0)))
        elif unit == 'kg':
            grams = kg_to_g(safe_float(s.get('Variant Weight', 0)))
        if grams and COL['weight']:
            row[COL['weight']] = grams
            if COL['weight_uom']:
                row[COL['weight_uom']] = 'g'

        # ─ defaults for optional template flags ─ #
        if 'Disabled' in row:
            row['Disabled'] = 0
        if 'Has Variants' in row:
            row['Has Variants'] = 0
        if 'Is Fixed Asset' in row:
            row['Is Fixed Asset'] = 0

        erp_rows.append(row)

    # 5) Write to disk
    with output_csv.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=template_header)
        writer.writeheader()
        writer.writerows(erp_rows)

    print(f'✓ Wrote {len(erp_rows)} ERPNext items → {output_csv}')


# --------------------------------------------------------------------------- #
if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='Shopify → ERPNext Item CSV mapper')
    ap.add_argument('--input', required=True, type=Path, help='Shopify CSV export')
    ap.add_argument('--template', required=True, type=Path, help='ERPNext Item.csv template')
    ap.add_argument('--output', required=True, type=Path, help='Destination CSV')
    args = ap.parse_args()

    try:
        convert(args.input, args.template, args.output)
    except Exception as e:
        print('❌ Something went wrong:', e, file=sys.stderr)
        sys.exit(1)
