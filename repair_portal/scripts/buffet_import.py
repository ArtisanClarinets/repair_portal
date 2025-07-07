#!/usr/bin/env python3
"""
buffet_import.py · Buffet Crampon PDF → ERPNext v15 (offline)
• OCR Buffet PDFs  →  Purchase Receipt / Invoice
• Header mapping & item breakdown per 2025-07-07 spec


python buffet_import.py \
     --site erp.artisanclarinets.com \
     --pdf-dir invoice_pdf \
     --default-wh "Clarinet Inventory - MAI" \
     --expense-acct "Cost of Goods Sold - MAI" \
     --make-pi \
     --due-days 0

"""

from __future__ import annotations
import argparse, logging, os, re, shutil, sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence, Set

LOG = logging.getLogger("buffet_offline")
logging.basicConfig(
    level=os.getenv("BUFFET_LOGLEVEL", "INFO").upper(),
    format="%(asctime)s  %(levelname)-8s %(name)s › %(message)s",
)

for exe in ("tesseract", "pdfinfo", "pdftocairo"):
    if not shutil.which(exe):
        LOG.critical("%s missing – install poppler-utils & tesseract-ocr", exe)
        sys.exit(10)

# ───────────────────────── configuration
@dataclass(slots=True)
class Config:
    site: str
    pdf_dir: Path
    warehouse: str
    expense_account: str
    supplier: str = "Buffet Crampon Group USA"          # new default
    make_purchase_invoice: bool = False
    due_days: int = 0
    skip_dupes: bool = True
    commit_each: bool = False

# ───────────────────────── OCR + parsing helpers
import pytesseract
from pdf2image import convert_from_path
import regex as re2

@dataclass(slots=True)
class InvoiceItem:
    item_code: str
    item_name: str
    origin: str
    hts: str | None
    qty: float
    rate: float
    description: str
    serial_numbers: List[str]

@dataclass(slots=True)
class InvoiceDoc:
    invoice_no: str
    posting_date: str
    sales_order: str | None
    packing_slip: str | None
    carrier: str | None
    tracking: List[str]
    freight: float | None
    currency: str = "USD"
    items: List[InvoiceItem] | None = None

_HDR   = re2.compile(r"(SINV\d{5,6}).{0,40}(SO\d{6})?.{0,40}?(\d{1,2}/\d{1,2}/\d{4})", re2.S)
_DATE  = re2.compile(r"(\d{1,2})/(\d{1,2})/(\d{4})")
_SKU   = re2.compile(r"\b(BC[0-9A-Z\-]+)\b")
_QTY   = re2.compile(r"\b(\d+(?:\.\d+)?)\b")
_PRICE = re2.compile(r"\$?([\d,]+\.\d{2})")
_HTS   = re2.compile(r"\b920[0-9]{4,}\b")
_TRACK = re2.compile(r"\b\d{12,}\b")
_PKG   = re2.compile(r"\b(SPS\d{6})\b")
_DESC_SPLIT = re2.compile(r"\s{2,}")

DESC_REGEX = re.compile(
    r"""
    (?P<instrument_key>BB|A|Eb|C|D|Bass)\s+
    (?P<instrument_type>[A-Z]+)\s+
    (?P<key_arrangement>\d{2}/\d{1})\s+
    (?P<item_name>[A-Za-z0-9]+)\s+
    (?P<key_plating>NP|SP)\s+
    \((?P<pitch>\d{3})\)
    """, re.VERBOSE | re.IGNORECASE
)

_num = lambda s: float(s.replace(",", ""))

def ocr_pdf(pdf: Path) -> str:
    imgs = convert_from_path(pdf, dpi=300, thread_count=2)
    return "\n".join(pytesseract.image_to_string(i) for i in imgs)

def _parse_blocks(lines: List[str]) -> List[List[str]]:
    """Group price/qty line + description line + serials line."""
    out, buf = [], []
    for ln in lines:
        if _SKU.search(ln):
            if buf: out.append(buf)
            buf = [ln]
        elif buf and ln.strip():
            buf.append(ln)
            if len(buf) == 3:
                out.append(buf)
                buf = []
    if buf: out.append(buf)
    return out

def parse_invoice(txt: str, name: str) -> InvoiceDoc | None:
    m = _HDR.search(txt)
    if not m:
        LOG.error("%s: header not found", name)
        return None
    inv_no, so_no, us_date = m.groups()
    iso_date = _DATE.sub(lambda g: f"{g[3]}-{int(g[1]):02d}-{int(g[2]):02d}", us_date)

    packing = _PKG.search(txt)
    tracks  = _TRACK.findall(txt)
    carrier = None
    for kw in ("FedEx", "UPS", "DHL"):
        if kw.lower() in txt.lower():
            carrier = kw; break

    freight = None
    m_f = re.search(r"charges\s+amount.*?([0-9,]+\.\d{2})", txt, re.I | re.S)
    if m_f: freight = _num(m_f.group(1))

    items: List[InvoiceItem] = []
    blocks = _parse_blocks(txt.splitlines())

    for blk in blocks:
        price_ln, desc_ln, sn_ln = (blk + ["", ""])[:3]

        sku_m = _SKU.search(price_ln)
        qty_m = _QTY.search(price_ln, sku_m.end() if sku_m else 0)
        price_m = _PRICE.search(price_ln, qty_m.end() if qty_m else 0)
        if not (sku_m and qty_m and price_m):
            continue

        # origin (first word on price line)
        origin = price_ln.strip().split()[0]

        # HTS if present
        hts = None
        hts_m = _HTS.search(price_ln)
        if hts_m: hts = hts_m.group(0)

        # item_name via regex
        md = DESC_REGEX.search(desc_ln)
        item_name = md.group("item_name") if md else sku_m.group(1)

        # serials
        serials = [s.strip() for s in re.split(r"[ ,]+", sn_ln.split(":",1)[-1]) if s.strip()]
        if not serials:
            LOG.warning("%s: serials missing for %s", name, sku_m.group(1))

        items.append(
            InvoiceItem(
                item_code   = sku_m.group(1),
                item_name   = item_name,
                origin      = origin,
                hts         = hts,
                qty         = _num(qty_m.group(1)),
                rate        = _num(price_m.group(1)),
                description = _DESC_SPLIT.sub(" ", desc_ln).strip(),
                serial_numbers = serials,
            )
        )

    if not items:
        LOG.error("%s: no items parsed", name)
        return None

    return InvoiceDoc(
        invoice_no   = inv_no,
        posting_date = iso_date,
        sales_order  = so_no,
        packing_slip = packing.group(1) if packing else None,
        carrier      = carrier,
        tracking     = tracks,
        freight      = freight,
        items        = items
    )

def load_invoices(dir: Path, show=False, one: str | None = None) -> List[InvoiceDoc]:
    pdfs = [Path(one)] if one else sorted(dir.glob("*.pdf"))
    docs: List[InvoiceDoc] = []
    for p in pdfs:
        try:
            raw = ocr_pdf(p)
            if show:
                print("═"*80, p.name, "\n", raw[:1000], "\n"+"═"*80)
                continue
            d = parse_invoice(raw, p.name)
            if d:
                docs.append(d)
                LOG.info("✓ parsed %-45s %2d item(s)", p.name, len(d.items))
        except Exception as e:
            LOG.exception("OCR failed for %s – %s", p, e)
    return docs

# ───────────────────────── ERPNext helpers
def _bench_connect(site_name: str):
    import frappe
    bench_root = Path(__file__).resolve().parents[4]
    site_path  = (bench_root / "sites" / site_name).resolve()
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
        f.get_doc({"doctype":"Supplier","supplier_name":name,"supplier_type":"Company"}).insert(ignore_permissions=True)

def _ensure_item(f, it: InvoiceItem):
    if f.db.exists("Item", it.item_code):
        return
    f.get_doc({
        "doctype": "Item",
        "item_code": it.item_code,
        "item_name": it.item_name[:140],
        "has_serial_no": 1,
        "stock_uom": "Nos",
        "item_group": "Clarinets",
    }).insert(ignore_permissions=True)

def _ensure_freight_item(f):
    if f.db.exists("Item", "Freight and Handling"):
        return
    f.get_doc({
        "doctype": "Item",
        "item_code": "Freight and Handling",
        "is_stock_item": 0,
        "stock_uom": "Nos",
        "item_group": "Services",
    }).insert(ignore_permissions=True)

# ───────── duplicate-serial helper
def _filter_new_serials(f, seen: Set[str], serials: List[str]) -> List[str]:
    return [s for s in serials if s not in seen and not f.db.exists("Serial No", s)]

# ───────── PR builder
def _pr(f, cfg: Config, doc: InvoiceDoc, seen: Set[str]) -> str | None:
    _ensure_freight_item(f)
    pr = f.new_doc("Purchase Receipt")
    pr.update({
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
    })

    for it in doc.items:
        _ensure_item(f, it)
        serials = _filter_new_serials(f, seen, it.serial_numbers) if cfg.skip_dupes else it.serial_numbers
        if not serials:
            LOG.warning("⤷ all serials duped, skipping %s on %s", it.item_code, doc.invoice_no)
            continue
        pr.append("items", {
            "item_code": it.item_code,
            "item_name": it.item_name,
            "description": it.description,
            "qty": len(serials),
            "uom": "Nos",
            "rate": it.rate,
            "conversion_factor": 1,
            "warehouse": cfg.warehouse,
            "expense_account": cfg.expense_account,
            "serial_no": "\n".join(serials),
            "discount_percentage": 1,
            "discount_amount": 0,
            "custom_origin_country": it.origin,
            "custom_hts_code": it.hts,
        })
        seen.update(serials)

    if doc.freight:
        pr.append("taxes", {
            "charge_type": "Actual",
            "account_head": "Freight & Shipping - MAI",
            "tax_amount": doc.freight,
            "description": "Shipping & Handling",
        })

    if not pr.items:
        LOG.warning("⚠ nothing to receive for %s – PR skipped", doc.invoice_no)
        return None

    pr.insert(ignore_permissions=True)
    pr.submit()
    LOG.info("PR %s", pr.name)
    return pr.name

# ───────── PI builder
def _pi(f, cfg: Config, pr_name: str, doc: InvoiceDoc) -> str:
    from frappe.utils import add_days, getdate
    pr = f.get_doc("Purchase Receipt", pr_name)

    pi = f.new_doc("Purchase Invoice")
    pi.update({
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
    })

    for row in pr.items:
        pi.append("items", {
            k: row.get(k) for k in (
                "item_code","item_name","description","qty","uom","conversion_factor",
                "rate","serial_no","warehouse","expense_account",
                "discount_percentage","discount_amount","custom_origin_country",
                "custom_hts_code"
            )
        } | {
            "purchase_receipt": pr.name,
            "purchase_receipt_item": row.name,
        })

    if doc.freight:
        pi.append("taxes", {
            "charge_type": "Actual",
            "account_head": "Freight & Shipping - MAI",
            "tax_amount": doc.freight,
            "description": "Shipping & Handling",
        })

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

# ───────────────────────── orchestrator
def push(f, cfg: Config, docs: List[InvoiceDoc]):
    seen: Set[str] = set()
    _ensure_supplier(f, cfg.supplier)
    for d in docs:
        pr_name = _pr(f, cfg, d, seen)
        if pr_name and cfg.make_purchase_invoice:
            _pi(f, cfg, pr_name, d)
        if cfg.commit_each: f.db.commit()
    if not cfg.commit_each: f.db.commit()

# ───────────────────────── CLI
def main(argv: Sequence[str] | None = None):
    ap = argparse.ArgumentParser(description="Buffet → ERPNext importer")
    ap.add_argument("--site", required=True)
    ap.add_argument("--pdf-dir", required=True, type=Path)
    ap.add_argument("--default-wh", default="Stores - HQ")
    ap.add_argument("--expense-acct", default="Cost of Goods Sold - MAI")
    ap.add_argument("--due-days", type=int, default=0)
    ap.add_argument("--make-pi", action="store_true")
    ap.add_argument("--skip-dupes", action=argparse.BooleanOptionalAction, default=True)
    ap.add_argument("--commit-each", action=argparse.BooleanOptionalAction, default=False)
    ap.add_argument("--show-ocr", action="store_true")
    ap.add_argument("--one", metavar="PDF")
    a = ap.parse_args(argv)

    cfg = Config(
        site=a.site, pdf_dir=a.pdf_dir, warehouse=a.default_wh,
        expense_account=a.expense_acct, make_purchase_invoice=a.make_pi,
        due_days=a.due_days, skip_dupes=a.skip_dupes, commit_each=a.commit_each
    )
    if not cfg.pdf_dir.is_dir():
        LOG.critical("%s not found", cfg.pdf_dir); sys.exit(2)

    invs = load_invoices(cfg.pdf_dir, a.show_ocr, a.one)
    if a.show_ocr: sys.exit(0)
    if not invs: LOG.error("No invoices parsed"); sys.exit(3)

    f = _bench_connect(cfg.site)
    try:
        push(f, cfg, invs)
        LOG.info("✓ Imported %d invoice(s).", len(invs))
    finally:
        f.destroy()

if __name__ == "__main__":
    main()