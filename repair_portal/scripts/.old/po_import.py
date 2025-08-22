#!/usr/bin/env python3
"""
po_import.py · Buffet Crampon PDF → ERPNext v15 Purchase Orders
v2025-07-08·Dylan

Reads Buffet Crampon invoice PDFs, parses them via OCR, and creates
Purchase Orders in ERPNext v15. Supports both serialized instruments
and non-serialized parts, skipping duplicates safely.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

import pytesseract
import regex as re2
from pdf2image import convert_from_path

LOG = logging.getLogger('po_import')
logging.basicConfig(
    level=os.getenv('BUFFET_LOGLEVEL', 'INFO').upper(),
    format='%(asctime)s  %(levelname)-8s %(name)s › %(message)s',
)


@dataclass(slots=True)
class InvoiceItem:
    item_code: str
    item_name: str
    origin: str
    hts: str | None
    qty: float
    rate: float
    description: str
    serial_numbers: list[str]


@dataclass(slots=True)
class InvoiceDoc:
    invoice_no: str
    posting_date: str
    sales_order: str | None
    packing_slip: str | None
    carrier: str | None
    tracking: list[str]
    freight: float | None
    currency: str = 'USD'
    items: list[InvoiceItem] = field(default_factory=list)


@dataclass(slots=True)
class Config:
    site: str
    pdf_dir: Path
    warehouse: str
    expense_account: str
    supplier: str = 'Buffet Crampon Group USA'
    commit_each: bool = False


_NUM = lambda s: float(s.replace(',', ''))

_HDR = re2.compile(
    r'(SINV\d{5,6}|SCN\d{6}).{0,40}(SO\d{6})?.{0,40}?(\d{1,2}/\d{1,2}/\d{4})',
    re2.S,
)
_DATE = re2.compile(r'(\d{1,2})/(\d{1,2})/(\d{4})')
_SKU = re2.compile(r'\b(BC(?=\d)[0-9A-Z\-]+)\b')
_QTY = re2.compile(r'\b(\d+(?:\.\d+)?)\b')
_PRICE = re2.compile(r'\$?([\d,]+\.\d{2})')
_HTS = re2.compile(r'\b920[0-9]{4,}\b')
_TRACK = re2.compile(r'\b\d{12,}\b')
_PKG = re2.compile(r'\b(SPS\d{6})\b')
_DESC_SPLIT = re2.compile(r'\s{2,}')
_SERIAL_LINE = re2.compile(r'serial\s*(?:number|no\.?)\s*[:;]?\s*(.*)', re2.I)

_DESC_REGEX = re2.compile(
    r"""
    (?P<instrument_key>BB|A|Eb|C|D|Bass)\s+
    (?P<instrument_type>[A-Z]+)\s+
    (?P<key_arrangement>\d{2}/\d{1})\s+
    (?P<item_name>[A-Za-z0-9]+)\s+
    (?P<key_plating>NP|SP)\s+
    \((?P<pitch>\d{3})\)
    """,
    re2.VERBOSE | re2.IGNORECASE,
)

_PARTS_START = re2.compile(
    r'^(?:(?P<origin>\S+)\s+(?P<hts>\d{6,})\s+)?'
    r'(?P<code>\S+)\s+(?P<qty>\d+(?:\.\d+)?)\s+un\s+(?P<price>[\d,]+\.\d{2})',
    re2.I,
)


def ocr_pdf(pdf: Path) -> str:
    images = convert_from_path(pdf, dpi=300, thread_count=2)
    return '\n'.join(pytesseract.image_to_string(img) for img in images)


def to_iso_date(m: re2.Match) -> str:
    mon, day, yr = int(m[1]), int(m[2]), int(m[3])
    if mon > 12:
        mon, day = day, mon
    return f'{yr:04d}-{mon:02d}-{day:02d}'


def _split_blocks(lines: list[str]) -> list[list[str]]:
    blocks: list[list[str]] = []
    buf: list[str] = []
    for ln in lines:
        low = ln.strip().lower()
        if re2.search(r'page\s*\d+\s*of\s*\d+', low):
            continue
        if _HDR.search(ln):
            continue
        is_sku = bool(_SKU.search(ln) and _QTY.search(ln) and _PRICE.search(ln))
        is_part = bool(_PARTS_START.match(ln))
        if is_sku or is_part:
            if buf:
                blocks.append(buf)
            buf = [ln]
            continue
        if buf:
            buf.append(ln)
            if _SERIAL_LINE.search(ln):
                blocks.append(buf)
                buf = []
    if buf:
        blocks.append(buf)
    return blocks


def parse_invoice(txt: str, filename: str) -> InvoiceDoc | None:
    m = _HDR.search(txt)
    if not m:
        LOG.error('Header not found in %s', filename)
        return None
    inv_no, so_no, us_date = m.groups()
    posting_date = _DATE.sub(to_iso_date, us_date)
    pack = _PKG.search(txt)
    tracks = _TRACK.findall(txt)
    carrier = next((c for c in ('FedEx', 'UPS', 'DHL') if c.lower() in txt.lower()), None)
    freight = None
    mf = re2.search(r'Total\s+charges[\s\S]*?([\d,]+\.\d{2})', txt, re2.I)
    if mf:
        freight = _NUM(mf.group(1))
    items: list[InvoiceItem] = []
    for blk in _split_blocks(txt.splitlines()):
        first = blk[0]
        sku_m = _SKU.search(first)
        part_m = _PARTS_START.match(first)
        if sku_m:
            code = sku_m.group(1)
            qty_m = _QTY.search(first, sku_m.end())
            price_m = _PRICE.search(first, qty_m.end() if qty_m else 0)
            qty = _NUM(qty_m.group(1)) if qty_m else 0.0
            rate = _NUM(price_m.group(1)) if price_m else 0.0
            origin = first.split()[0]
            hts_m = next((x for ln in blk for x in (_HTS.search(ln),) if x), None)
            hts = hts_m.group(0) if hts_m else None
        elif part_m:
            origin = part_m.group('origin') or first.split()[0]
            hts = part_m.group('hts')
            code = part_m.group('code')
            qty = _NUM(part_m.group('qty'))
            rate = _NUM(part_m.group('price'))
        else:
            continue
        desc_lines: list[str] = []
        for ln in blk[1:]:
            if _SERIAL_LINE.search(ln):
                break
            if not _SKU.search(ln) and not _PARTS_START.match(ln):
                desc_lines.append(ln.strip())
        description = _DESC_SPLIT.sub(' ', ' '.join(desc_lines)).strip()
        serials: list[str] = []
        for ln in blk:
            sm = _SERIAL_LINE.search(ln)
            if sm:
                serials = [s.strip() for s in re2.split(r'[,\s]+', sm.group(1)) if s.strip()]
                break
        if sku_m and not serials:
            LOG.error('No serials for %s in %s; skipping', code, filename)
            continue
        item_name = code
        if sku_m:
            md = _DESC_REGEX.search(description)
            if md:
                item_name = md.group('item_name')
        items.append(
            InvoiceItem(
                item_code=code,
                item_name=item_name,
                origin=origin,
                hts=hts,
                qty=qty,
                rate=rate,
                description=description,
                serial_numbers=serials,
            )
        )
    if not items:
        LOG.error('No items parsed in %s', filename)
        return None
    return InvoiceDoc(
        invoice_no=inv_no,
        posting_date=posting_date,
        sales_order=so_no,
        packing_slip=pack.group(1) if pack else None,
        carrier=carrier,
        tracking=tracks,
        freight=freight,
        items=items,
    )


def _bench_connect(site: str):
    import frappe

    root = Path(__file__).resolve().parents[4]
    site_path = (root / 'sites' / site).resolve()
    frappe.init(site=str(site_path))
    frappe.connect()
    frappe.set_user('Administrator')
    frappe.local.lang = 'en'
    return frappe


def _ensure_item(frappe, it: InvoiceItem):
    if frappe.db.exists('Item', it.item_code):
        return
    frappe.get_doc(
        {
            'doctype': 'Item',
            'item_code': it.item_code,
            'item_name': it.item_name[:140],
            'has_serial_no': 1 if it.serial_numbers else 0,
            'stock_uom': 'Nos',
            'item_group': 'Clarinets' if _SKU.search(it.item_code) else 'Services',
        }
    ).insert(ignore_permissions=True)


def _ensure_freight_item(frappe):
    if not frappe.db.exists('Item', 'Freight and Handling'):
        frappe.get_doc(
            {
                'doctype': 'Item',
                'item_code': 'Freight and Handling',
                'item_name': 'Freight and Handling',
                'is_stock_item': 0,
                'stock_uom': 'Nos',
                'item_group': 'Services',
            }
        ).insert(ignore_permissions=True)


def create_po(frappe, cfg: Config, doc: InvoiceDoc) -> str | None:
    if frappe.db.exists('Purchase Order', {'supplier_invoice_no': doc.invoice_no}):
        LOG.warning('PO for %s already exists, skipping', doc.invoice_no)
        return None
    _ensure_freight_item(frappe)
    po = frappe.new_doc('Purchase Order')
    po.update(
        {
            'supplier': cfg.supplier,
            'supplier_invoice_no': doc.invoice_no,
            'transaction_date': doc.posting_date,
            'schedule_date': doc.posting_date,
            'currency': doc.currency,
            'plc_conversion_rate': 1.0,
        }
    )
    for it in doc.items:
        _ensure_item(frappe, it)
        po.append(
            'items',
            {
                'item_code': it.item_code,
                'item_name': it.item_name,
                'description': it.description,
                'qty': it.qty,
                'uom': 'Nos',
                'rate': it.rate,
                'warehouse': cfg.warehouse,
                'expense_account': cfg.expense_account,
            },
        )
    if doc.freight is not None and doc.freight > 0:
        po.append(
            'taxes',
            {
                'charge_type': 'Actual',
                'account_head': 'Freight & Shipping - MAI',
                'description': 'Shipping & Handling',
                'tax_amount': doc.freight,
            },
        )
    if not po.items:
        LOG.warning('No lines on PO for %s; skipping', doc.invoice_no)
        return None
    po.insert(ignore_permissions=True)
    LOG.info('Created PO %s for invoice %s', po.name, doc.invoice_no)
    return po.name


def main():
    parser = argparse.ArgumentParser(description='Import Buffet Crampon PDFs as POs')
    parser.add_argument('--site', required=True)
    parser.add_argument('--pdf-dir', required=True, type=Path)
    parser.add_argument('--default-wh', dest='warehouse', default='Stores - HQ')
    parser.add_argument(
        '--expense-acct', dest='expense_account', default='Cost of Goods Sold - MAI'
    )
    parser.add_argument('--commit-each', action='store_true')
    parser.add_argument('--show-ocr', action='store_true')
    parser.add_argument('--one', metavar='PDF')
    args = parser.parse_args()

    cfg = Config(
        site=args.site,
        pdf_dir=args.pdf_dir,
        warehouse=args.warehouse,
        expense_account=args.expense_account,
        commit_each=args.commit_each,
    )
    if not cfg.pdf_dir.is_dir():
        LOG.critical('PDF directory not found: %s', cfg.pdf_dir)
        sys.exit(1)

    invoices: list[InvoiceDoc] = []
    for pdf in [Path(args.one)] if args.one else sorted(cfg.pdf_dir.glob('*.pdf')):
        txt = ocr_pdf(pdf)
        if args.show_ocr:
            print(f"\n{'='*80}\n{pdf.name}\n{txt[:800]}\n{'='*80}\n")
            continue
        inv = parse_invoice(txt, pdf.name)
        if inv:
            invoices.append(inv)

    if args.show_ocr:
        return
    if not invoices:
        LOG.error('No invoices to import.')
        sys.exit(2)

    frappe = _bench_connect(cfg.site)
    try:
        created = 0
        for inv in invoices:
            if create_po(frappe, cfg, inv):
                created += 1
                if cfg.commit_each:
                    frappe.db.commit()
        if not cfg.commit_each:
            frappe.db.commit()
        LOG.info('Finished: %d POs created out of %d invoices', created, len(invoices))
    finally:
        frappe.destroy()


if __name__ == '__main__':
    main()
