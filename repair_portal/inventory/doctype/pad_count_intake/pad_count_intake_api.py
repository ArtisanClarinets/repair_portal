# ---
# File Header:
# Absolute Path: /home/frappe/frappe-bench/apps/repair_portal/repair_portal/inventory/doctype/pad_count_intake/pad_count_intake_api.py
# Last Updated: 2025-08-21
# Version: v1.0.1 (Pre-save download endpoint; aligns PDF with in-doc generator)
# Purpose: Public API to download the Shooting Kit PDF *without* needing a saved document.
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
    aruco_dict: str = "DICT_4X4_50",
    marker_length_mm: float = 50.0,
    pad_diameter_mm: float = 10.0,
    docname: str | None = None
):
    if not HAS_CV2:
        frappe.throw(_("OpenCV (contrib) is required to generate the ArUco marker (package: opencv-contrib-python)."))
    if not HAS_REPORTLAB:
        frappe.throw(_("ReportLab is required to create PDFs (package: reportlab)."))

    marker_png = _make_aruco_png_bytes(aruco_dict=aruco_dict, side_px=1200)
    pdf_bytes = _build_marker_pdf(marker_png, float(marker_length_mm), str(aruco_dict), str(docname or "New"))

    filename = f"Pad-Shooting-Kit-{(docname or 'New')}.pdf".replace("/", "-")
    frappe.local.response.filename = filename
    frappe.local.response.filecontent = pdf_bytes
    frappe.local.response.type = "download"
    frappe.local.response.display_content_as = "attachment"
    return


def _make_aruco_png_bytes(aruco_dict: str, side_px: int = 1200) -> bytes:
    if not HAS_CV2 or not hasattr(cv2, "aruco"):
        raise RuntimeError("OpenCV contrib (cv2.aruco) not available.")
    aruco = cv2.aruco
    dict_map = {
        "DICT_4X4_50": aruco.DICT_4X4_50,
        "DICT_4X4_100": aruco.DICT_4X4_100,
        "DICT_5X5_50": aruco.DICT_5X5_50,
        "DICT_5X5_100": aruco.DICT_5X5_100,
        "DICT_6X6_50": aruco.DICT_6X6_50,
        "DICT_6X6_100": aruco.DICT_6X6_100,
        "DICT_APRILTAG_36h11": aruco.DICT_APRILTAG_36h11
    }
    dkey = dict_map.get(aruco_dict, aruco.DICT_4X4_50)
    adict = aruco.getPredefinedDictionary(dkey)
    marker_id = 0
    img = aruco.generateImageMarker(adict, marker_id, side_px)
    border = int(0.1 * side_px)
    canvas_img = 255 * np.ones((side_px + 2*border, side_px + 2*border), dtype=np.uint8)
    canvas_img[border:border+side_px, border:border+side_px] = img
    ok, buf = cv2.imencode(".png", canvas_img)
    if not ok:
        raise RuntimeError("Failed to encode ArUco PNG.")
    return buf.tobytes()


def _build_marker_pdf(marker_png: bytes, marker_mm: float, aruco_dict: str, docname: str) -> bytes:
    buf = io.BytesIO()

    def draw_steps_block(c, x, y_top, width):
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x, y_top, "Step-by-Step: How to Use the Marker Grid")
        y = y_top - 16
        c.setFont("Helvetica", 10)
        steps = [
            "1) Print this kit at 100% scale (no 'Fit to Page').",
            "2) Verify the 100 mm ruler on this page matches a real ruler.",
            "3) Cut out a marker (from the grid page) and tape it on a dark, matte surface.",
            "4) Arrange pads with ≥ 1/2 pad gap; keep the marker flat on the same plane.",
            "5) Take a top-down photo (camera parallel), no glare/blur; shortest side ≥ 2000 px.",
            "6) Upload the photo in Pad Count Intake → Photo, then click 'Process Image'.",
            "7) Review the annotated preview; approve or adjust the final count; Update Inventory."
        ]
        line_h = 13
        for s in steps:
            c.drawString(x, y, s)
            y -= line_h
        y -= 6
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x, y, "Tips:")
        y -= 12
        c.setFont("Helvetica", 10)
        tips = [
            "• One marker is enough; two at opposite corners improve reliability.",
            "• Keep printed markers clean and flat. Re-print if worn or curled.",
            "• If the printed ruler isn't exactly 100 mm, re-print at 100% scale."
        ]
        for t in tips:
            c.drawString(x, y, t)
            y -= line_h
        return y

    def draw_single_page(c, pagesize, label):
        page_w, page_h = pagesize
        m = 15 * mm
        c.setTitle(f"Pad Shooting Kit: {docname}")

        c.setFont("Helvetica-Bold", 16)
        c.drawString(m, page_h - m - 12, f"Clarinet Pad Shooting Kit ({label})")
        c.setFont("Helvetica", 10)
        c.drawString(m, page_h - m - 28, f"Document: {docname}   |   ArUco: {aruco_dict}   |   Marker Side: {int(marker_mm)} mm")

        left_w = 95 * mm
        draw_steps_block(c, x=m, y_top=page_h - m - 52, width=left_w)

        marker_pts = marker_mm * mm
        mrk_x = m + left_w + 12
        mrk_y_top = page_h - m - 52
        mrk_y = mrk_y_top - marker_pts
        if mrk_y < m + 40*mm:
            mrk_y = m + 40*mm

        c.rect(mrk_x - 1, mrk_y - 1, marker_pts + 2, marker_pts + 2, stroke=1, fill=0)
        c.drawImage(ImageReader(io.BytesIO(marker_png)), mrk_x, mrk_y, width=marker_pts, height=marker_pts, mask='auto')

        r_x = mrk_x
        r_y = mrk_y - 14*mm
        c.setFont("Helvetica", 9)
        c.drawString(r_x, r_y + 12*mm, "Ruler: 100 mm")
        c.line(r_x, r_y, r_x + 100*mm, r_y)
        for i in range(0, 101, 10):
            x = r_x + i*mm
            tick_h = 6 if i % 50 else 10
            c.line(x, r_y, x, r_y + tick_h)
            c.drawString(x - 6, r_y - 10, str(i))

        c.setFont("Helvetica-Oblique", 9)
        c.drawString(m, m, "Print at 100% scale. Keep this sheet flat when shooting.")
        c.showPage()

    def draw_grid_page(c, pagesize, label, rows=3, cols=3):
        page_w, page_h = pagesize
        m = 20 * mm
        c.setFont("Helvetica-Bold", 14)
        c.drawString(m, page_h - m - 12, f"Pad Shooting Kit Multi-Marker Grid ({label})")

        avail_w = page_w - 2*m
        avail_h = page_h - 2*m - 40
        cell_w = avail_w / cols
        cell_h = (avail_h - 20*mm) / rows
        side = min(cell_w, cell_h) * 0.8

        IR = ImageReader(io.BytesIO(marker_png))
        tl_x = tl_y = None
        for r in range(rows):
            for col in range(cols):
                x = m + col*cell_w + (cell_w - side)/2
                y = page_h - m - (r+1)*cell_h - 10*mm
                c.rect(x-1, y-1, side+2, side+2, stroke=1, fill=0)
                c.drawImage(IR, x, y, width=side, height=side, mask='auto')
                if r == 0 and col == 0:
                    tl_x, tl_y = x, y

        if tl_x is not None and tl_y is not None:
            mini_gap = 6 * mm
            mini_len = 50 * mm
            mini_y0 = tl_y + side / 2.0
            mini_x0 = tl_x + side + mini_gap
            c.setFont("Helvetica", 8)
            c.drawString(mini_x0, mini_y0 + 8, "Mini Ruler: 50 mm")
            c.line(mini_x0, mini_y0, mini_x0 + mini_len, mini_y0)
            for i in range(0, 51, 10):
                x = mini_x0 + i*mm
                tick_h = 4 if i % 50 else 7
                c.line(x, mini_y0, x, mini_y0 + tick_h)
                c.drawString(x - 6, mini_y0 - 10, str(i))

        r_x = m
        r_y = m + 20
        c.setFont("Helvetica", 9)
        c.drawString(r_x, r_y + 12, "Ruler: 100 mm")
        c.line(r_x, r_y, r_x + 100*mm, r_y)
        for i in range(0, 101, 10):
            x = r_x + i*mm
            tick_h = 6 if i % 50 else 10
            c.line(x, r_y, x, r_y + tick_h)
            c.drawString(x - 6, r_y - 10, str(i))

        c.setFont("Helvetica-Oblique", 9)
        c.drawString(m, m, f"Grid layout {rows}x{cols} ({label}). Print at 100%.")
        c.showPage()

    c = canvas.Canvas(buf, pagesize=A4)
    draw_single_page(c, A4, "A4 Single")
    draw_grid_page(c, A4, "A4 Grid")
    draw_single_page(c, letter, "US Letter Single")
    draw_grid_page(c, letter, "US Letter Grid")
    c.save()
    return buf.getvalue()
