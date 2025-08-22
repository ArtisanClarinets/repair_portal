# ---
# File Header:
# Absolute Path: /home/frappe/frappe-bench/apps/repair_portal/repair_portal/inventory/doctype/pad_count_intake/pad_count_intake_api.py
# Last Updated: 2025-08-21
# Version: v1.1.1 (Fix: move single-page ruler block inside draw_single_page; ensure page size set per page)
# Purpose: Public API to download the multi-page Shooting Kit PDF *without* needing a saved document.
# Dependencies: Frappe Framework, OpenCV (contrib), ReportLab

from __future__ import annotations

import io
import frappe
from frappe import _

try:
    import cv2
    import numpy as np

    HAS_CV2 = True
except Exception:
    HAS_CV2 = False

try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader

    HAS_REPORTLAB = True
except Exception:
    HAS_REPORTLAB = False


@frappe.whitelist()
def generate_shooting_kit_preview(
    aruco_dict: str = 'DICT_4X4_50',
    marker_length_mm: float = 50.0,
    pad_diameter_mm: float = 10.0,  # kept for future use/URL parity
    docname: str | None = None,
):
    """Return a downloadable PDF Shooting Kit (works before saving the DocType)."""
    if not HAS_CV2:
        frappe.throw(
            _(
                'OpenCV (contrib) is required to generate the ArUco marker (package: opencv-contrib-python).'
            )
        )
    if not HAS_REPORTLAB:
        frappe.throw(_('ReportLab is required to create PDFs (package: reportlab).'))

    marker_png = _make_aruco_png_bytes(aruco_dict=aruco_dict, side_px=1200)
    pdf_bytes = _build_marker_pdf(
        marker_png, float(marker_length_mm), str(aruco_dict), str(docname or 'New')
    )

    filename = f"Pad-Shooting-Kit-{(docname or 'New')}.pdf".replace('/', '-')
    frappe.local.response.filename = filename
    frappe.local.response.filecontent = pdf_bytes
    frappe.local.response.type = 'download'
    frappe.local.response.display_content_as = 'attachment'
    return


# ----------------------- PDF helpers (same layout as controller) -----------------------


def _make_aruco_png_bytes(aruco_dict: str, side_px: int = 1200) -> bytes:
    if not HAS_CV2 or not hasattr(cv2, 'aruco'):
        raise RuntimeError('OpenCV contrib (cv2.aruco) not available.')
    aruco = cv2.aruco
    dict_map = {
        'DICT_4X4_50': aruco.DICT_4X4_50,
        'DICT_4X4_100': aruco.DICT_4X4_100,
        'DICT_5X5_50': aruco.DICT_5X5_50,
        'DICT_5X5_100': aruco.DICT_5X5_100,
        'DICT_6X6_50': aruco.DICT_6X6_50,
        'DICT_6X6_100': aruco.DICT_6X6_100,
        'DICT_APRILTAG_36h11': aruco.DICT_APRILTAG_36h11,
    }
    dkey = dict_map.get(aruco_dict, aruco.DICT_4X4_50)
    adict = aruco.getPredefinedDictionary(dkey)
    marker_id = 0
    img = aruco.generateImageMarker(adict, marker_id, side_px)
    border = int(0.1 * side_px)
    canvas_img = 255 * np.ones((side_px + 2 * border, side_px + 2 * border), dtype=np.uint8)
    canvas_img[border : border + side_px, border : border + side_px] = img
    ok, buf = cv2.imencode('.png', canvas_img)
    if not ok:
        raise RuntimeError('Failed to encode ArUco PNG.')
    return buf.tobytes()


def _build_marker_pdf(marker_png: bytes, marker_mm: float, aruco_dict: str, docname: str) -> bytes:
    """
    Multi-page PDF with robust, non-overlapping layout:
      1) A4 Single (left = steps; right = exact-size marker + 100 mm ruler)
      2) A4 Grid (3×3 + 50 mm mini-ruler + 100 mm bottom ruler)
      3) Letter Single
      4) Letter Grid
    All sizes in true millimeters; print at 100%.
    """
    if not HAS_REPORTLAB:
        raise RuntimeError('ReportLab not available.')
    buf = io.BytesIO()

    def draw_single_page(c, pagesize, label):
        from reportlab.lib.utils import ImageReader

        # Ensure page size and local geometry are scoped for this page
        c.setPageSize(pagesize)
        page_w, page_h = pagesize

        m = 15 * mm
        header_h = 22 * mm
        gutter = 14 * mm
        left_w = 110 * mm
        right_x = m + left_w + gutter
        right_w = page_w - right_x - m
        content_top = page_h - m - header_h
        content_bottom = m + 18 * mm
        content_h = content_top - content_bottom

        # header
        c.setTitle(f'Pad Shooting Kit: {docname}')
        c.setFont('Helvetica-Bold', 16)
        c.drawString(m, page_h - m - 12, f'Clarinet Pad Shooting Kit ({label})')
        c.setFont('Helvetica', 10)
        c.drawString(
            m,
            page_h - m - 28,
            f'Document: {docname}   |   ArUco: {aruco_dict}   |   Marker Side: {int(marker_mm)} mm',
        )

        # left column text
        x = m
        y = content_top
        c.setFont('Helvetica-Bold', 12)
        c.drawString(x, y, 'Step-by-Step: How to Use the Marker Grid')
        y -= 16

        steps = [
            "Print this kit at 100% scale (no 'Fit to Page').",
            'Verify the 100 mm ruler on this page matches a real ruler.',
            'Cut out a marker (from the grid page) and tape it on a dark, matte surface.',
            'Arrange pads with ≥ 1/2 pad gap; keep the marker flat on the same plane.',
            'Take a top-down photo (camera parallel), no glare/blur; shortest side ≥ 2000 px.',
            "Upload the photo in Pad Count Intake → Photo, then click 'Process Image'.",
            'Review the annotated preview; approve or adjust the final count; Update Inventory.',
        ]
        y = _draw_bulleted(c, steps, x, y, left_w, number=True, leading=13)
        y -= 6

        c.setFont('Helvetica-Bold', 10)
        c.drawString(x, y, 'Tips:')
        y -= 12
        tips = [
            'One marker is enough; two at opposite corners improve reliability.',
            'Keep printed markers clean and flat. Re-print if worn or curled.',
            "If the printed ruler isn't exactly 100 mm, re-print at 100% scale.",
        ]
        y = _draw_bulleted(c, tips, x, y, left_w, bullet='•', leading=13)

        # right column visuals
        marker_pts = marker_mm * mm
        if marker_pts > right_w:
            extra = marker_pts - right_w
            right_x = max(m + left_w + gutter / 2 + 2 * mm, right_x - extra / 2)
            right_w = page_w - right_x - m

        ruler_block_h = 16 * mm
        needed_h = marker_pts + ruler_block_h + 10 * mm
        start_y = content_bottom + max(0, (content_h - needed_h) / 2.0)

        # Nudge to reduce chance of text overlap in tight layouts
        shift_down = 12 * mm

        mrk_x = right_x + (right_w - marker_pts) / 2.0
        mrk_y = start_y + ruler_block_h + 6 * mm - shift_down
        if mrk_y < (content_bottom + 4 * mm):
            mrk_y = content_bottom + 4 * mm

        c.rect(mrk_x - 1, mrk_y - 1, marker_pts + 2, marker_pts + 2, stroke=1, fill=0)
        c.drawImage(
            ImageReader(io.BytesIO(marker_png)),
            mrk_x,
            mrk_y,
            width=marker_pts,
            height=marker_pts,
            mask='auto',
        )

        # ✅ Ruler block (now inside function; has access to page/right geometry and mrk_y)
        r_len = 100 * mm
        r_x = right_x + (right_w - r_len) / 2.0
        r_y = mrk_y - (ruler_block_h + 4 * mm)
        c.setFont('Helvetica', 9)
        c.drawString(r_x, r_y + 12 * mm, 'Ruler: 100 mm')
        c.line(r_x, r_y, r_x + r_len, r_y)
        for i in range(0, 101, 10):
            x_tick = r_x + i * mm
            tick_h = (6 * mm) if (i % 50) else (10 * mm)
            c.line(x_tick, r_y, x_tick, r_y + tick_h)
            c.drawString(x_tick - 6 * mm, r_y - 4 * mm, str(i))

        c.setFont('Helvetica-Oblique', 9)
        c.drawString(m, m, 'Print at 100% scale. Keep this sheet flat when shooting.')
        c.showPage()

    def draw_grid_page(c, pagesize, label, rows=3, cols=3):
        from reportlab.lib.utils import ImageReader

        # Ensure page size is set for this page too
        c.setPageSize(pagesize)
        page_w, page_h = pagesize
        m = 20 * mm
        header_h = 16 * mm
        footer_h = 16 * mm
        content_top = page_h - m - header_h
        content_bottom = m + footer_h + 22 * mm

        c.setFont('Helvetica-Bold', 14)
        c.drawString(m, page_h - m - 12, f'Pad Shooting Kit Multi-Marker Grid ({label})')

        avail_w = page_w - 2 * m
        avail_h = content_top - content_bottom
        cell_w = avail_w / cols
        cell_h = avail_h / rows
        side = min(cell_w, cell_h) * 0.8

        IR = ImageReader(io.BytesIO(marker_png))
        tl_x = tl_y = None
        for r in range(rows):
            for col in range(cols):
                x = m + col * cell_w + (cell_w - side) / 2.0
                y = content_top - (r + 1) * cell_h + (cell_h - side) / 2.0
                c.rect(x - 1, y - 1, side + 2, side + 2, stroke=1, fill=0)
                c.drawImage(IR, x, y, width=side, height=side, mask='auto')
                if r == 0 and col == 0:
                    tl_x, tl_y = x, y

        # mini-ruler — place below the page title (above markers) with extra text bottom padding
        mini_len = 50 * mm
        mini_y = page_h - m - (header_h / 2.0) - 4 * mm
        text_bottom_pad = 3 * mm
        text_y = mini_y + text_bottom_pad
        mini_x = m
        if mini_x + mini_len > page_w - m:
            mini_x = m + (avail_w - mini_len) / 2.0
        c.setFont('Helvetica', 8)
        c.drawString(mini_x, text_y, 'Mini Ruler: 50 mm')
        c.line(mini_x, mini_y, mini_x + mini_len, mini_y)
        from reportlab.pdfbase.pdfmetrics import stringWidth

        for i in range(0, 51, 10):
            x_tick = mini_x + i * mm
            tick_h = (4 * mm) if (i % 50) else (7 * mm)
            c.line(x_tick, mini_y, x_tick, mini_y + tick_h)
            lbl = str(i)
            lbl_w = stringWidth(lbl, 'Helvetica', 8)
            c.drawString(x_tick - (lbl_w / 2.0), mini_y - 4 * mm, lbl)

        # bottom 100 mm ruler
        r_len = 100 * mm
        r_x = (page_w - r_len) / 2.0
        r_y = m + 22 * mm
        c.setFont('Helvetica', 9)
        c.drawString(r_x, r_y + 12 * mm, 'Ruler: 100 mm')
        c.line(r_x, r_y, r_x + r_len, r_y)
        for i in range(0, 101, 10):
            x_tick = r_x + i * mm
            tick_h = (6 * mm) if (i % 50) else (10 * mm)
            c.line(x_tick, r_y, x_tick, r_y + tick_h)
            c.drawString(x_tick - 6 * mm, r_y - 4 * mm, str(i))

        c.setFont('Helvetica-Oblique', 9)
        c.drawString(m, m, f'Grid layout {rows}x{cols} ({label}). Print at 100%.')
        c.showPage()

    c = canvas.Canvas(buf, pagesize=A4)
    draw_single_page(c, A4, 'A4 Single')
    draw_grid_page(c, A4, 'A4 Grid')
    c.save()
    return buf.getvalue()


def _build_marker_pdf_compact(
    marker_png: bytes, marker_mm: float, aruco_dict: str, docname: str
) -> bytes:
    """Compact one-page PDF variant for quick printing: smaller fonts, truncated header.
    Useful for diagnostics and compact printouts where full instruction text is not needed.
    """
    if not HAS_REPORTLAB:
        raise RuntimeError('ReportLab not available.')
    buf = io.BytesIO()
    page = A4
    page_w, page_h = page
    c = canvas.Canvas(buf, pagesize=page)

    m = 12 * mm
    # header (compact)
    c.setFont('Helvetica-Bold', 12)
    short_name = (docname or '').strip()
    if len(short_name) > 40:
        short_name = short_name[:37] + '...'
    c.drawString(m, page_h - m - 8, f'Pad Shooting Kit (Compact) — {short_name}')
    c.setFont('Helvetica', 8)
    c.drawString(m, page_h - m - 20, f'ArUco: {aruco_dict}   |   Marker: {int(marker_mm)} mm')

    # marker preview (compact, top-left)
    try:
        img_reader = ImageReader(io.BytesIO(marker_png))
    except Exception:
        img_reader = None

    marker_side = 60 * mm
    img_x = m
    img_y = page_h - m - 20 - marker_side - 6 * mm
    if img_reader:
        c.drawImage(img_reader, img_x, img_y, width=marker_side, height=marker_side, mask='auto')
    else:
        c.rect(img_x, img_y, marker_side, marker_side)

    # small bullet points
    bullets = [
        'Print at 100% (no fit-to-page).',
        'Place marker on matte dark background.',
        'Top-down shot; avoid glare/blur.',
        'Use the grid page for extra markers if needed.',
    ]
    tx = img_x + marker_side + 8 * mm
    ty = page_h - m - 30
    c.setFont('Helvetica', 9)
    leading = 11
    for b in bullets:
        c.drawString(tx, ty, f'• {b}')
        ty -= leading

    # compact 100mm ruler at bottom
    r_len = 100 * mm
    r_x = (page_w - r_len) / 2.0
    r_y = m + 18 * mm
    c.setFont('Helvetica', 8)
    # raise legend slightly to add breathing room above the ruler
    c.drawString(r_x, r_y + 10 * mm, 'Ruler: 100 mm')
    c.line(r_x, r_y, r_x + r_len, r_y)
    for i in range(0, 101, 10):
        x_tick = r_x + i * mm
        tick_h = (4 * mm) if (i % 50) else (6 * mm)
        c.line(x_tick, r_y, x_tick, r_y + tick_h)
        c.drawString(x_tick - 4 * mm, r_y - 4 * mm, str(i))

    c.setFont('Helvetica-Oblique', 8)
    c.drawString(
        m, m, 'Compact variant: for quick print/diagnostics. Full kit available in main PDF.'
    )
    c.save()
    return buf.getvalue()


# ---- text helpers ----


def _wrap_lines(c, text: str, max_width: float, font_name='Helvetica', font_size=10):
    """Return wrapped lines to fit max_width (points)."""
    from reportlab.pdfbase.pdfmetrics import stringWidth

    c.setFont(font_name, font_size)
    words = text.split()
    lines, cur = [], ''
    for w in words:
        probe = (cur + ' ' + w).strip()
        if stringWidth(probe, font_name, font_size) <= max_width:
            cur = probe
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _draw_paragraph(
    c,
    text: str,
    x: float,
    y: float,
    max_width: float,
    font_name='Helvetica',
    font_size=10,
    leading=13,
) -> float:
    lines = _wrap_lines(c, text, max_width, font_name, font_size)
    c.setFont(font_name, font_size)
    for ln in lines:
        c.drawString(x, y, ln)
        y -= leading
    return y


def _draw_bulleted(
    c,
    items,
    x: float,
    y: float,
    max_width: float,
    bullet='•',
    number=False,
    leading=13,
    font_name='Helvetica',
    font_size=10,
) -> float:
    pad = 10
    num = 1
    for it in items:
        label = f'{num})' if number else bullet
        c.setFont(font_name, font_size)
        c.drawString(x, y, label)
        y = _draw_paragraph(
            c,
            str(it),
            x + pad,
            y,
            max_width - pad,
            font_name=font_name,
            font_size=font_size,
            leading=leading,
        )
        y -= 2
        num += 1
    return y
