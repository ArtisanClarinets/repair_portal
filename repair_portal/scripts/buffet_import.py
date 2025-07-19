#!/usr/bin/env python3
"""
buffet_import.py · Buffet Crampon PDF → ERPNext v15 (offline)
v2025-07-07+parts-fix · Dylan

• OCR Buffet Crampon PDF invoices (full orders & parts)
• Creates Purchase Receipts (+ optional Purchase Invoices)
• Maps every header- and item-level field you listed
• Skips duplicate serial numbers (DB + in-memory)
• Adds freight as “shipping_charge” **and** an Actual tax row
• Safe due-date and absolute site-path handling
• Robust block splitter across page breaks
• Flexible serial-line regex to catch OCR variants
• Supports both BC-prefixed SKUs and generic “origin HTS? code  qty un  price” lines
"""

from __future__ import annotations

import argparse
import logging
import os
import shutil
import sys
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

# ───────────────────────── logging ─────────────────────────
LOG = logging.getLogger("buffet_offline")
logging.basicConfig(
    level=os.getenv("BUFFET_LOGLEVEL", "INFO").upper(),
    format="%(asctime)s  %(levelname)-8s %(name)s › %(message)s",
)

# ───────────────────────── system binaries check ────────────
for exe in ("tesseract", "pdfinfo", "pdftocairo"):
    if not shutil.which(exe):
        LOG.critical("%s missing – install poppler-utils & tesseract-ocr", exe)
        sys.exit(10)


# ───────────────────────── configuration ────────────────────
@dataclass(slots=True)
class Config:
    site: str
    pdf_dir: Path
    warehouse: str
    expense_account: str
    supplier: str = "Buffet Crampon Group USA"
    make_purchase_invoice: bool = False
    due_days: int = 0
    skip_dupes: bool = True
    commit_each: bool = False


# ───────────────────────── OCR + parsing ──────────────────
import pytesseract
import regex as re2
from pdf2image import convert_from_path

_num = lambda s: float(s.replace(",", ""))


def ocr_pdf(pdf: Path) -> str:
    imgs = convert_from_path(pdf, dpi=300, thread_count=2)
    return "\n".join(pytesseract.image_to_string(i) for i in imgs)


# ────────────────────── data classes ──────────────────────
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
    currency: str = "USD"
    items: list[InvoiceItem] = field(default_factory=list)


# ───────────────────────── regexes ─────────────────────────
_HDR = re2.compile(r"(SINV\d{5,6}|SCN\d{6}).{0,40}(SO\d{6})?.{0,40}?(\d{1,2}/\d{1,2}/\d{4})", re2.S)
_DATE = re2.compile(r"(\d{1,2})/(\d{1,2})/(\d{4})")
_SKU = re2.compile(r"\b(BC(?=\d)[0-9A-Z\-]+)\b")
_QTY = re2.compile(r"\b(\d+(?:\.\d+)?)\b")
_PRICE = re2.compile(r"\$?([\d,]+\.\d{2})")
_HTS = re2.compile(r"\b920[0-9]{4,}\b")
_TRACK = re2.compile(r"\b\d{12,}\b")
_PKG = re2.compile(r"\b(SPS\d{6})\b")
_DESC_SPLIT = re2.compile(r"\s{2,}")
SERIAL_RE = re2.compile(r"serial\s*(?:number|no\.?)\s*[:;]?\s*(.*)", re2.I)

# instrument‐description extractor (for item_name)
DESC_REGEX = re2.compile(
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

# allow optional origin + HTS before code
_PARTS_START = re2.compile(
    r"^(?:(?P<origin>\S+)\s+(?P<hts>\d{6,})\s+)?"
    r"(?P<code>\S+)\s+(?P<qty>\d+(?:\.\d+)?)\s+un\s+(?P<price>[\d,]+\.\d{2})",
    re2.I,
)


def to_iso(m):
    mon, day, yr = int(m[1]), int(m[2]), int(m[3])
    if mon > 12:
        mon, day = day, mon
    return f"{yr:04d}-{mon:02d}-{day:02d}"


def _parse_blocks(lines: list[str]) -> list[list[str]]:
    """
    Split into item blocks:
     - start at SKU+qty+price or origin HTS? code qty un price
     - accumulate until SERIAL_RE line or next block start
     - skip page headers/footers
    """
    blocks, buf = [], []
    for ln in lines:
        low = ln.strip().lower()
        if re2.search(r"page\s*\d+\s*of\s*\d+", low):
            continue
        if _HDR.search(ln):
            continue

        sku_line = _SKU.search(ln) and _QTY.search(ln) and _PRICE.search(ln)
        parts_line = _PARTS_START.match(ln)

        if sku_line or parts_line:
            if buf:
                blocks.append(buf)
            buf = [ln]
            continue

        if buf:
            buf.append(ln)
            if SERIAL_RE.search(ln):
                blocks.append(buf)
                buf = []
    if buf:
        blocks.append(buf)
    return blocks


def parse_invoice(txt: str, name: str) -> InvoiceDoc | None:
    m = _HDR.search(txt)
    if not m:
        LOG.error("%s: header not found", name)
        return None

    inv_no, so_no, us_date = m.groups()
    iso_date = _DATE.sub(to_iso, us_date)

    pack = _PKG.search(txt)
    tracks = _TRACK.findall(txt)
    carrier = next((c for c in ("FedEx", "UPS", "DHL") if c.lower() in txt.lower()), None)

    # only grab "Total charges"
    freight = None
    m_f = re2.search(r"Total\s+charges[\s\S]*?([\d,]+\.\d{2})", txt, re2.I)
    if m_f:
        freight = _num(m_f.group(1))

    items: list[InvoiceItem] = []
    for blk in _parse_blocks(txt.splitlines()):
        first = blk[0]
        sku_m = _SKU.search(first)
        parts_m = _PARTS_START.match(first)

        # extract common fields
        if sku_m:
            code = sku_m.group(1)
            qty_m = _QTY.search(first, sku_m.end())
            rate_m = _PRICE.search(first, qty_m.end() if qty_m else 0)
            qty = _num(qty_m.group(1)) if qty_m else 0
            rate = _num(rate_m.group(1)) if rate_m else 0
            origin = first.strip().split()[0]
            hts_m = next((m for ln in blk for m in (_HTS.search(ln),) if m), None)
            hts = hts_m.group(0) if hts_m else None
        elif parts_m:
            origin = parts_m.group("origin") or first.strip().split()[0]
            hts = parts_m.group("hts")
            code = parts_m.group("code")
            qty = _num(parts_m.group("qty"))
            rate = _num(parts_m.group("price"))
        else:
            continue

        # build description from all non-SKU / non-parts lines until serial
        desc_lines = []
        for ln in blk[1:]:
            if SERIAL_RE.search(ln):
                break
            if not _SKU.search(ln) and not _PARTS_START.match(ln):
                desc_lines.append(ln.strip())
        desc = _DESC_SPLIT.sub(" ", " ".join(desc_lines)).strip()

        # extract serials if present
        serials: list[str] = []
        for ln in blk:
            m_ser = SERIAL_RE.search(ln)
            if m_ser:
                raw = m_ser.group(1)
                serials = [s.strip() for s in re2.split(r"[,\s]+", raw) if s.strip()]
                break

        # skip missing serials on SKU lines
        if sku_m and not serials:
            LOG.error("%s: serials missing for %s", name, code)
            continue

        # item_name: DESC_REGEX if SKU, else code
        item_name = code
        if sku_m:
            md = DESC_REGEX.search(desc)
            if md:
                item_name = md.group("item_name")

        items.append(
            InvoiceItem(
                item_code=code,
                item_name=item_name,
                origin=origin,
                hts=hts,
                qty=qty,
                rate=rate,
                description=desc,
                serial_numbers=serials,
            )
        )

    if not items:
        LOG.error("%s: no items parsed", name)
        return None

    return InvoiceDoc(
        invoice_no=inv_no,
        posting_date=iso_date,
        sales_order=so_no,
        packing_slip=pack.group(1) if pack else None,
        carrier=carrier,
        tracking=tracks,
        freight=freight,
        items=items,
    )


def load_invoices(dir: Path, show=False, one: str | None = None) -> list[InvoiceDoc]:
    pdfs = [Path(one)] if one else sorted(dir.glob("*.pdf"))
    docs = []
    for p in pdfs:
        try:
            raw = ocr_pdf(p)
            if show:
                print("\n" + "=" * 80 + f"\n{p.name}\n" + raw[:800] + "\n" + "=" * 80 + "\n")
                continue
            inv = parse_invoice(raw, p.name)
            if inv:
                docs.append(inv)
                LOG.info("✓ parsed %-30s %2d items", p.name, len(inv.items))
        except Exception as e:
            LOG.exception("OCR failed for %s – %s", p.name, e)
    return docs


def _bench_connect(site_name: str):
    import frappe

    bench_root = Path(__file__).resolve().parents[4]
    site_path = (bench_root / "sites" / site_name).resolve()
    if not site_path.is_dir():
        raise FileNotFoundError(site_path)
    (site_path / "logs").mkdir(parents=True, exist_ok=True)
    frappe.init(site=str(site_path))
    frappe.connect()
    frappe.set_user("Administrator")
    frappe.local.lang = "en"
    return frappe


def _ensure_supplier(f, name: str):
    if not f.db.exists("Supplier", name):
        f.get_doc({"doctype": "Supplier", "supplier_name": name, "supplier_type": "Company"}).insert(
            ignore_permissions=True
        )


def _ensure_warehouse(f, wh: str):
    if not f.db.exists("Warehouse", wh):
        f.get_doc({"doctype": "Warehouse", "warehouse_name": wh, "company": f.get_default("company")}).insert(
            ignore_permissions=True
        )


# ─────────────── NEW: centralised Website-Item creation ────────────────
def _ensure_website_item(f, it: InvoiceItem):
    """
    Create or update Website Item so that:
        • route  == item_code  (clean / predictable URL)
        • web_item_name = item_name (fallback to item_code)
        • published      = 1
    Safe to call repeatedly.
    """
    where = {"item_code": it.item_code}
    wi_name = f.db.exists("Website Item", where)
    if wi_name:
        wi = f.get_doc("Website Item", wi_name)
    else:
        wi = f.get_doc({"doctype": "Website Item", **where})

    # update / back-fill
    wi.web_item_name = it.item_name or it.item_code
    wi.route = it.item_code
    wi.published = 1
    wi.flags.ignore_permissions = True
    wi.save()


def _ensure_item(f, it: InvoiceItem):
    """
    ▸ Creates Item if missing.
    ▸ Ensures a Website Item exists with route == item_code.
    """
    if not f.db.exists("Item", it.item_code):
        f.get_doc(
            {
                "doctype": "Item",
                "item_code": it.item_code,
                "item_name": it.item_name[:140],
                "has_serial_no": 1 if it.serial_numbers else 0,
                "stock_uom": "Nos",
                "item_group": "Clarinets" if _SKU.search(it.item_code) else "Services",
            }
        ).insert(ignore_permissions=True)

    # Only older (non-Webshop) sites still expose Item.route.
    doc = f.get_doc("Item", it.item_code)
    if hasattr(doc, "route"):
        if not doc.route:
            doc.route = it.item_code
            doc.save(ignore_permissions=True)

    # v15 Webshop path
    _ensure_website_item(f, it)


def _ensure_freight_item(f):
    if not f.db.exists("Item", "Freight and Handling"):
        f.get_doc(
            {
                "doctype": "Item",
                "item_code": "Freight and Handling",
                "item_name": "Freight and Handling",
                "is_stock_item": 0,
                "stock_uom": "Nos",
                "item_group": "Services",
            }
        ).insert(ignore_permissions=True)


def _filter_new_serials(f, seen: set[str], serials: list[str]) -> list[str]:
    return [s for s in serials if s not in seen and not f.db.exists("Serial No", s)]


def _pr(f, cfg: Config, doc: InvoiceDoc, seen: set[str]) -> str | None:
    _ensure_freight_item(f)
    pr = f.new_doc("Purchase Receipt")
    pr.update(
        {
            "supplier": cfg.supplier,
            "supplier_invoice_no": doc.invoice_no,
            "supplier_sales_order_no": doc.sales_order,
            "posting_date": doc.posting_date,
            "custom_packing_slip_no": doc.packing_slip,
            "custom_carrier": doc.carrier,
            "tracking_number": doc.tracking[0] if doc.tracking else None,
            "custom_tracking_list": "\n".join(doc.tracking) if doc.tracking else None,
            "currency": doc.currency,
            "set_posting_time": 1,
            "mode_of_payment": "ACH",
            "payment_terms_template": "Net 30",
            "shipping_charge": doc.freight,
        }
    )
    for it in doc.items:
        _ensure_item(f, it)
        serials = _filter_new_serials(f, seen, it.serial_numbers) if cfg.skip_dupes else it.serial_numbers
        qty = len(serials) if serials else it.qty
        if qty <= 0:
            LOG.warning("⤷ skipping zero-qty %s on %s", it.item_code, doc.invoice_no)
            continue

        row = {
            "item_code": it.item_code,
            "item_name": it.item_name,
            "description": it.description,
            "qty": qty,
            "uom": "Nos",
            "conversion_factor": 1,
            "rate": it.rate,
            "warehouse": cfg.warehouse,
            "expense_account": cfg.expense_account,
            "custom_origin_country": it.origin,
            "custom_hts_code": it.hts,
            "discount_percentage": 1,
            "discount_amount": 0,
        }
        if serials:
            row["serial_no"] = "\n".join(serials)
            seen.update(serials)
        pr.append("items", row)

    if doc.freight:
        pr.append(
            "taxes",
            {
                "charge_type": "Actual",
                "account_head": "Freight & Shipping - MAI",
                "tax_amount": doc.freight,
                "description": "Shipping & Handling",
            },
        )

    if not pr.items:
        LOG.warning("⚠ nothing to receive for %s – PR skipped", doc.invoice_no)
        return None

    pr.insert(ignore_permissions=True)
    pr.submit()
    LOG.info("PR %s", pr.name)
    return pr.name


def _pi(f, cfg: Config, pr_name: str, doc: InvoiceDoc) -> str | None:
    from frappe.utils import add_days, getdate

    pr = f.get_doc("Purchase Receipt", pr_name)
    pi = f.new_doc("Purchase Invoice")
    pi.update(
        {
            "supplier": cfg.supplier,
            "supplier_invoice_no": doc.invoice_no,
            "supplier_sales_order_no": doc.sales_order,
            "posting_date": doc.posting_date,
            "bill_date": doc.posting_date,
            "custom_packing_slip_no": doc.packing_slip,
            "custom_carrier": doc.carrier,
            "tracking_number": doc.tracking[0] if doc.tracking else None,
            "custom_tracking_list": "\n".join(doc.tracking) if doc.tracking else None,
            "currency": doc.currency,
            "mode_of_payment": "ACH",
            "payment_terms_template": "Net 30",
            "shipping_charge": doc.freight,
            "update_stock": 0,
        }
    )
    for row in pr.items:
        pi.append(
            "items",
            {
                **{
                    k: row.get(k)
                    for k in (
                        "item_code",
                        "item_name",
                        "description",
                        "qty",
                        "uom",
                        "conversion_factor",
                        "rate",
                        "serial_no",
                        "warehouse",
                        "expense_account",
                        "discount_percentage",
                        "discount_amount",
                        "custom_origin_country",
                        "custom_hts_code",
                    )
                },
                **{"purchase_receipt": pr.name, "purchase_receipt_item": row.name},
            },
        )
    if doc.freight:
        pi.append(
            "taxes",
            {
                "charge_type": "Actual",
                "account_head": "Freight & Shipping - MAI",
                "tax_amount": doc.freight,
                "description": "Shipping & Handling",
            },
        )
    pi.set_missing_values()
    pi.credit_days = max(0, cfg.due_days)
    pi.credit_days_based_on = "Day(s)"
    pi.payment_terms_template = "Net 30"
    pi.set("payment_schedule", [])
    pi.due_date = add_days(getdate(doc.posting_date), pi.credit_days)
    pi.insert(ignore_permissions=True)
    pi.submit()
    LOG.info("PI %s", pi.name)
    return pi.name


def push(f, cfg: Config, docs: list[InvoiceDoc]):
    seen: set[str] = set()
    _ensure_supplier(f, cfg.supplier)
    _ensure_warehouse(f, cfg.warehouse)
    for d in docs:
        prn = _pr(f, cfg, d, seen)
        if prn and cfg.make_purchase_invoice:
            _pi(f, cfg, prn, d)
        if cfg.commit_each:
            f.db.commit()
    if not cfg.commit_each:
        f.db.commit()


def main(argv: Sequence[str] | None = None):
    ap = argparse.ArgumentParser(description="Buffet → ERPNext importer")
    ap.add_argument("--site", required=True)
    ap.add_argument("--pdf-dir", required=True, type=Path)
    ap.add_argument("--default-wh", dest="warehouse", default="Stores - HQ")
    ap.add_argument("--expense-acct", dest="expense_account", default="Cost of Goods Sold - MAI")
    ap.add_argument("--due-days", type=int, default=0)
    ap.add_argument("--make-pi", action="store_true")
    ap.add_argument("--skip-dupes", action=argparse.BooleanOptionalAction, default=True)
    ap.add_argument("--commit-each", action=argparse.BooleanOptionalAction, default=False)
    ap.add_argument("--show-ocr", action="store_true")
    ap.add_argument("--one", metavar="PDF")
    args = ap.parse_args(argv)

    cfg = Config(
        site=args.site,
        pdf_dir=args.pdf_dir,
        warehouse=args.warehouse,
        expense_account=args.expense_account,
        make_purchase_invoice=args.make_pi,
        due_days=args.due_days,
        skip_dupes=args.skip_dupes,
        commit_each=args.commit_each,
    )

    if not cfg.pdf_dir.is_dir():
        LOG.critical("%s not found", cfg.pdf_dir)
        sys.exit(2)

    invs = load_invoices(cfg.pdf_dir, args.show_ocr, args.one)
    if args.show_ocr:
        sys.exit(0)
    if not invs:
        LOG.error("No invoices parsed")
        sys.exit(3)

    f = _bench_connect(cfg.site)
    try:
        push(f, cfg, invs)
        LOG.info("✓ Imported %d invoice(s).", len(invs))
    finally:
        f.destroy()


if __name__ == "__main__":
    main()
