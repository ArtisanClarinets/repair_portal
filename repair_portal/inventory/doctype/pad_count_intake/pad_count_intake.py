# /home/frappe/frappe-bench/apps/repair_portal/repair_portal/inventory/doctype/pad_count_intake/pad_count_intake.py
# ---
# File Header:
# Absolute Path: /home/frappe/frappe-bench/apps/repair_portal/repair_portal/inventory/doctype/pad_count_intake/pad_count_intake.py
# Last Updated: 2025-08-21
# Version: v1.6.1 (PDF: fixed scope for single-page ruler block; no logic changes)
# Purpose: High-accuracy pad counting without ML (ArUco rectification + mm-to-px + Hough⊕Contours⊕Template fusion).
#          Generates a print-ready Shooting Kit PDF and places an instruction image into the Photo field (attach flow).
#          Provides processing, approval, and stock posting with audit logs and safety gates.
# Dependencies: Frappe Framework, ERPNext Stock, OpenCV (contrib for cv2.aruco), Pillow (fallback), ReportLab (PDF)

from __future__ import annotations

import io
import json
from dataclasses import dataclass

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime

# Preferred: OpenCV
try:
    import cv2
    import numpy as np

    HAS_CV2 = True
except Exception:
    HAS_CV2 = False
    from PIL import ImageFilter  # type: ignore

# Optional: ReportLab for PDF
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    HAS_REPORTLAB = True
except Exception:
    HAS_REPORTLAB = False


class PadCountIntake(Document):
    def before_save(self):
        """Fill inventory_delta from approved_count and infer company from warehouse."""
        try:
            if self.approved_count and (self.inventory_delta in (None, 0)):  # type: ignore
                self.inventory_delta = int(self.approved_count)  # type: ignore
            if not getattr(self, 'company', None) and getattr(self, 'warehouse', None):
                self.company = _get_company_for_warehouse(self.warehouse)  # type: ignore
        except Exception:
            frappe.log_error('PadCountIntake.before_save error', frappe.get_traceback())
            frappe.throw(_('Unexpected error while preparing document.'))

    def _append_log(self, action: str, value):
        """Safe log appender to the child table."""
        try:
            self.append(
                'count_logs',
                {
                    'action': action,
                    'value': str(value),
                    'by_user': frappe.session.user,
                    'at': now_datetime(),
                },
            )
        except Exception:
            frappe.log_error('PadCountIntake._append_log error', frappe.get_traceback())


# ----------------------- UI Actions -----------------------


@frappe.whitelist()
def generate_shooting_kit(name: str, marker_mm: float | None = None, aruco_dict: str | None = None):
    """Create & attach a multi-page Shooting Kit PDF + an instruction JPG (also sets Photo)."""
    doc = frappe.get_doc('Pad Count Intake', name)
    marker_mm = float(marker_mm or doc.get('aruco_marker_length_mm') or 50.0)  # type: ignore
    aruco_dict = (aruco_dict or doc.get('aruco_dict') or 'DICT_4X4_50').strip()  # type: ignore

    # Build assets
    try:
        marker_png = _make_aruco_png_bytes(aruco_dict, side_px=1200)  # type: ignore
    except Exception:
        frappe.log_error('generate_shooting_kit: aruco generation error', frappe.get_traceback())
        frappe.throw(_('Could not generate ArUco marker (opencv-contrib required).'))

    try:
        pdf_bytes = _build_marker_pdf(marker_png, marker_mm, aruco_dict, docname=name)  # type: ignore
    except Exception:
        frappe.log_error('generate_shooting_kit: pdf generation error', frappe.get_traceback())
        frappe.throw(_("PDF generation failed (install 'reportlab')."))

    try:
        instr_jpg = _build_instruction_image(marker_png, marker_mm, aruco_dict)  # type: ignore
    except Exception:
        frappe.log_error('generate_shooting_kit: instruction image error', frappe.get_traceback())
        instr_jpg = marker_png  # fallback

    # Attach & set Photo
    try:
        pdf_file = frappe.get_doc(
            {
                'doctype': 'File',
                'file_name': f'{name}-shooting-kit.pdf',
                'content': pdf_bytes,
                'is_private': 1,
                'attached_to_doctype': 'Pad Count Intake',
                'attached_to_name': name,
            }
        ).insert(ignore_permissions=True)

        jpg_file = frappe.get_doc(
            {
                'doctype': 'File',
                'file_name': f'{name}-instructions.jpg',
                'content': instr_jpg,
                'is_private': 1,
                'attached_to_doctype': 'Pad Count Intake',
                'attached_to_name': name,
            }
        ).insert(ignore_permissions=True)

        doc.photo = jpg_file.file_url  # type: ignore
        checklist = [
            'Top-down shot; camera parallel to mat.',
            f'Place printed ArUco marker ({int(marker_mm)} mm) in frame.',
            'Matte dark background; separate pads (≥ 1/2 pad).',
            'Shortest side ≥ 2000 px; avoid blur/glare.',
        ]
        notes = 'Shooting Checklist:\n- ' + '\n- '.join(checklist)
        doc.notes = (doc.notes + '\n\n' + notes) if doc.notes else notes  # type: ignore

        doc._append_log( # type: ignore
            'generate_shooting_kit', f'pdf={pdf_file.file_url}, img={jpg_file.file_url}' # type: ignore
        )  # type: ignore
        doc.save()
        frappe.db.commit()
    except Exception:
        frappe.log_error('generate_shooting_kit: attach/persist error', frappe.get_traceback())
        frappe.throw(_('Failed to attach files to the document.'))

    return {
        'photo': doc.photo, # type: ignore
        'pdf_url': pdf_file.file_url, # type: ignore
        'message': _('Shooting kit generated and attached.'),
    }  # type: ignore


@frappe.whitelist()
def process_image(name: str):
    """Detect pads (no-ML pipeline), attach preview + JSON, update quality flag."""
    doc = frappe.get_doc('Pad Count Intake', name)
    if not doc.photo:  # type: ignore
        frappe.throw(_('Please attach a photo first.'))

    try:
        file_doc = frappe.get_doc('File', {'file_url': doc.photo})  # type: ignore
        content = file_doc.get_content()  # type: ignore
    except Exception:
        frappe.log_error('PadCountIntake.process_image get_content error', frappe.get_traceback())
        frappe.throw(_('Could not read the attached image.'))

    params = {
        'min_radius': int(doc.min_radius or 10),  # type: ignore
        'max_radius': int(doc.max_radius or 60),  # type: ignore
        'dp': float(doc.dp or 1.2),  # type: ignore
        'param1': int(doc.param1 or 100),  # type: ignore
        'param2': int(doc.param2 or 30),  # type: ignore
        'blur': int(doc.blur or 7),  # type: ignore
        'use_aruco': bool(doc.use_aruco),  # type: ignore
        'aruco_dict': (doc.aruco_dict or 'DICT_4X4_50'),  # type: ignore
        'marker_mm': float(doc.aruco_marker_length_mm or 50.0),  # type: ignore
        'pad_mm': float(doc.pad_diameter_mm or 10.0),  # type: ignore
        'auto_radius_from_mm': bool(doc.auto_radius_from_mm),  # type: ignore
    }

    try:
        detected_count, preview_bytes, meta_json = detect_pads(content, params)
    except Exception:
        frappe.log_error('PadCountIntake.detect_pads error', frappe.get_traceback())
        frappe.throw(_('Image processing failed. Please verify image quality and try again.'))

    preview_file = frappe.get_doc(
        {
            'doctype': 'File',
            'file_name': f'{name}-preview.jpg',
            'content': preview_bytes,
            'is_private': 1,
            'attached_to_doctype': 'Pad Count Intake',
            'attached_to_name': name,
        }
    )
    preview_file.insert(ignore_permissions=True)

    meta_file = frappe.get_doc(
        {
            'doctype': 'File',
            'file_name': f'{name}-detections.json',
            'content': meta_json.encode('utf-8'),
            'is_private': 1,
            'attached_to_doctype': 'Pad Count Intake',
            'attached_to_name': name,
        }
    )
    meta_file.insert(ignore_permissions=True)

    try:
        doc.detected_count = int(detected_count)  # type: ignore
        if not doc.approved_count:  # type: ignore
            doc.approved_count = int(detected_count)  # type: ignore
        doc.processed_preview = preview_file.file_url  # type: ignore
        doc.detections_meta = meta_file.file_url  # type: ignore
        doc.processed_at = now_datetime()  # type: ignore

        try:
            quality_ok = bool(json.loads(meta_json).get('quality_ok', True))
        except Exception:
            quality_ok = True
        doc.flags_quality_ok = 1 if quality_ok else 0  # type: ignore

        doc._append_log('process_image', f'detected={detected_count}, quality_ok={quality_ok}')  # type: ignore
        doc.save()
        frappe.db.commit()
    except Exception:
        frappe.log_error('PadCountIntake.process_image persist error', frappe.get_traceback())
        frappe.throw(_('Failed to persist results.'))

    return {
        'detected_count': detected_count,
        'processed_preview': doc.processed_preview, # type: ignore
        'detections_meta': doc.detections_meta, # type: ignore
    }  # type: ignore


@frappe.whitelist()
def approve_count(name: str, approved_count: int):
    """Set the human-approved count and move to Approved state."""
    doc = frappe.get_doc('Pad Count Intake', name)
    try:
        doc.approved_count = int(approved_count)  # type: ignore
        if not doc.inventory_delta:  # type: ignore
            doc.inventory_delta = int(approved_count)  # type: ignore
        doc.review_status = 'Approved'  # type: ignore
        doc.approved_at = now_datetime()  # type: ignore
        doc._append_log('approve_count', approved_count)  # type: ignore
        doc.save()
        frappe.db.commit()
    except Exception:
        frappe.log_error('PadCountIntake.approve_count error', frappe.get_traceback())
        frappe.throw(_('Could not approve count.'))
    return {'approved_count': doc.approved_count, 'inventory_delta': doc.inventory_delta}  # type: ignore


@frappe.whitelist()
def update_inventory(name: str):
    """Create/submit a Stock Entry based on inventory_action and inventory_delta."""
    doc = frappe.get_doc('Pad Count Intake', name)
    if doc.review_status != 'Approved':  # type: ignore
        frappe.throw(_('Please set Review Status to Approved before updating inventory.'))

    delta = int(doc.inventory_delta or 0)  # type: ignore
    if delta == 0 or doc.inventory_action == 'No Change':  # type: ignore
        frappe.throw(_('Inventory Delta must be non-zero to proceed.'))
    if not doc.item or not doc.warehouse:  # type: ignore
        frappe.throw(_('Item and Warehouse are required.'))

    is_stock_item = frappe.db.get_value('Item', doc.item, 'is_stock_item')  # type: ignore
    if not is_stock_item:
        frappe.throw(_('Selected Item is not a stock item.'))

    company = doc.company or _get_company_for_warehouse(doc.warehouse)  # type: ignore
    if not company:
        frappe.throw(_('Unable to determine Company for the selected Warehouse.'))

    purpose = (
        'Material Receipt' if doc.inventory_action == 'Increase' and delta > 0 else 'Material Issue' # type: ignore
    )  # type: ignore
    qty = abs(delta)

    try:
        se = frappe.get_doc(
            {
                'doctype': 'Stock Entry',
                'stock_entry_type': purpose,
                'company': company,
                'to_warehouse': doc.warehouse if purpose == 'Material Receipt' else None,  # type: ignore
                'from_warehouse': doc.warehouse if purpose == 'Material Issue' else None,  # type: ignore
                'items': [
                    {
                        'item_code': doc.item,  # type: ignore
                        'qty': qty,
                        'uom': doc.uom or 'Nos',  # type: ignore
                        't_warehouse': doc.warehouse if purpose == 'Material Receipt' else None,  # type: ignore
                        's_warehouse': doc.warehouse if purpose == 'Material Issue' else None,  # type: ignore
                    }
                ],
            }
        )
        se.insert()
        if 'Inventory Manager' in frappe.get_roles(frappe.session.user):
            se.submit()

        doc.stock_entry = se.name  # type: ignore
        doc._append_log('update_inventory', f'{purpose} qty={qty}, SE={se.name}')  # type: ignore
        doc.save()
        frappe.db.commit()
    except Exception:
        frappe.log_error('PadCountIntake.update_inventory error', frappe.get_traceback())
        frappe.throw(_('Failed to create or submit Stock Entry.'))

    return {'stock_entry': doc.stock_entry, 'purpose': purpose, 'qty': qty}  # type: ignore


# ----------------------- Detection (No-ML Fusion) -----------------------


@dataclass
class Detection:
    x: int
    y: int
    r: int
    conf: float
    method: str  # "hough" | "contour" | "template"


def detect_pads(img_bytes: bytes, params: dict):
    """Return (count, preview_jpeg_bytes, meta_json)."""
    if not HAS_CV2:
        # Pillow fallback (very rough)
        from PIL import Image

        im = Image.open(io.BytesIO(img_bytes))
        gray = im.convert('L').filter(
            ImageFilter.GaussianBlur(radius=max(1, (params.get('blur') or 7) // 2))
        )
        a = np.array(gray, dtype=np.uint8)  # type: ignore
        hist, _ = np.histogram(a.flatten(), 256, [0, 256])  # type: ignore
        total = a.size
        current_max, threshold = 0, 0
        sum_total = np.dot(np.arange(256), hist)
        sumB, wB = 0.0, 0.0
        for i in range(256):
            wB += hist[i]
            if wB == 0:
                continue
            wF = total - wB
            if wF == 0:
                break
            sumB += i * hist[i]
            mB = sumB / wB
            mF = (sum_total - sumB) / wF
            between = wB * wF * (mB - mF) ** 2
            if between > current_max:
                current_max = between
                threshold = i
        bw = (a > threshold).astype(np.uint8)
        white = int((bw == 255).sum())
        avg_pad_area = float((params['max_radius'] ** 2) * 3.14)
        count = max(0, int(white / max(1.0, avg_pad_area)))
        b = io.BytesIO()
        im.save(b, format='JPEG', quality=85)
        meta = {'quality_ok': True, 'detections': [], 'backend': 'pillow'}
        return int(count), b.getvalue(), json.dumps(meta)

    arr = np.frombuffer(img_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    quality_ok, metrics = _quality_checks(img)

    px_per_mm: float | None = None
    warp_img = img
    aruco_info = {}
    if bool(params.get('use_aruco', True)):
        warp_img, px_per_mm, aruco_info = _try_aruco_rectify_and_scale(
            img_bgr=img,
            aruco_dict_name=str(params.get('aruco_dict') or 'DICT_4X4_50'),
            marker_mm=float(params.get('marker_mm') or 50.0),
        )

    if params.get('auto_radius_from_mm', True) and px_per_mm:
        pad_mm = float(params.get('pad_mm') or 10.0)
        r_px = max(2, int((pad_mm / 2.0) * px_per_mm))
        params['min_radius'] = max(2, int(r_px * 0.75))
        params['max_radius'] = max(params['min_radius'] + 2, int(r_px * 1.25))

    gray = _preprocess(warp_img, params.get('blur') or 7)
    det_h = _detect_hough(gray, params)
    det_c = _detect_contours(gray, params)
    det_t = _detect_template(gray, params)

    fused = _nms_merge(det_h + det_c + det_t, iou_thr=0.35)

    hsv = cv2.cvtColor(warp_img, cv2.COLOR_BGR2HSV)
    for d in fused:
        v = hsv[d.y, d.x, 2] / 255.0
        h = hsv[d.y, d.x, 0]
        warmth = 1.0 - min(abs((h - 20) / 40.0), 1.0)
        d.conf = float(min(1.0, d.conf * (0.7 + 0.3 * warmth) * (0.6 + 0.4 * v)))

    fused = [d for d in fused if d.conf >= 0.45]

    preview_bytes = _annotate(warp_img, fused)
    meta = {
        'quality_ok': bool(quality_ok),
        'quality_metrics': metrics,
        'detections': [d.__dict__ for d in fused],
        'method_counts': {'hough': len(det_h), 'contour': len(det_c), 'template': len(det_t)},
        'aruco': aruco_info,
        'px_per_mm': px_per_mm,
    }
    return len(fused), preview_bytes, json.dumps(meta)


def _quality_checks(img_bgr) -> tuple[bool, dict]:
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    focus = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).ravel()
    total = hist.sum() or 1.0
    mid = float(hist[5:251].sum() / total)
    h, w = gray.shape[:2]
    metrics = {'focus_var': focus, 'mid_tone_ratio': mid, 'w': int(w), 'h': int(h)}
    ok = (focus >= 50.0) and (mid >= 0.65) and (min(h, w) >= 600)
    return ok, metrics


def _preprocess(img_bgr, blur_ks: int):
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
    L, A, B = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    L2 = clahe.apply(L)
    lab2 = cv2.merge([L2, A, B])
    eq = cv2.cvtColor(lab2, cv2.COLOR_LAB2BGR)
    gray = cv2.cvtColor(eq, cv2.COLOR_BGR2GRAY)
    k = blur_ks if blur_ks and blur_ks % 2 == 1 else 7
    big_k = k * 3 if (k * 3) % 2 == 1 else (k * 3 + 1)
    illum = cv2.GaussianBlur(gray, (big_k, big_k), 0)
    illum = cv2.max(illum, 1)  # type: ignore
    norm = cv2.divide(gray, illum, scale=255)
    den = cv2.bilateralFilter(norm, 7, 50, 50)
    return den


def _detect_hough(gray, params) -> list[Detection]:
    min_r = int(params['min_radius'])
    max_r = int(params['max_radius'])
    minDist = max(10, int((min_r + max_r) / 2))
    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=float(params['dp']),
        minDist=minDist,
        param1=int(params['param1']),
        param2=int(params['param2']),
        minRadius=min_r,
        maxRadius=max_r,
    )
    dets: list[Detection] = []
    if circles is not None:
        for x, y, r in np.round(circles[0, :]).astype('int'):
            dets.append(Detection(x=int(x), y=int(y), r=int(r), conf=0.85, method='hough'))
    return dets


def _detect_contours(gray, params) -> list[Detection]:
    thr = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 35, 2)
    thr = cv2.medianBlur(thr, 5)
    kernel = np.ones((3, 3), np.uint8)
    thr = cv2.morphologyEx(thr, cv2.MORPH_OPEN, kernel, iterations=1)
    cnts, _ = cv2.findContours(thr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    dets: list[Detection] = []
    for c in cnts:
        area = cv2.contourArea(c)
        if area < 50:
            continue
        (x, y), r = cv2.minEnclosingCircle(c)
        if r < params['min_radius'] or r > params['max_radius']:
            continue
        peri = cv2.arcLength(c, True)
        if peri == 0:
            continue
        circularity = 4 * np.pi * area / (peri * peri)
        if circularity < 0.6:
            continue
        dets.append(
            Detection(
                x=int(x), y=int(y), r=int(r), conf=float(min(1.0, circularity)), method='contour'
            )
        )
    return dets


def _detect_template(gray, params) -> list[Detection]:
    r = max(3, int((int(params['min_radius']) + int(params['max_radius'])) / 2))
    size = r * 2 + 3
    tmpl = np.zeros((size, size), dtype=np.uint8)
    cv2.circle(tmpl, (size // 2, size // 2), r, 255, thickness=-1)  # type: ignore
    edges = cv2.Canny(
        gray, threshold1=max(20, int(params['param1'] * 0.5)), threshold2=int(params['param1'])
    )
    t_edges = cv2.Canny(tmpl, 50, 150)
    res = cv2.matchTemplate(edges, t_edges, cv2.TM_CCOEFF_NORMED)
    thr = 0.5
    ys, xs = np.where(res >= thr)
    dets: list[Detection] = []
    used = np.zeros_like(res, dtype=np.uint8)
    for y, x in zip(ys.tolist(), xs.tolist(), strict=False):
        if used[y, x]:
            continue
        win = res[max(0, y - 5) : y + 6, max(0, x - 5) : x + 6]
        if res[y, x] < float(np.max(win)):
            continue
        cx = x + size // 2
        cy = y + size // 2
        dets.append(
            Detection(
                x=int(cx), y=int(cy), r=int(r), conf=float(min(1.0, res[y, x])), method='template' # type: ignore
            )
        )  # type: ignore
        used[max(0, y - 5) : y + 6, max(0, x - 5) : x + 6] = 1
    return dets


def _nms_merge(dets: list[Detection], iou_thr=0.3) -> list[Detection]:
    if not dets:
        return []
    boxes = []
    scores = []
    for d in dets:
        x1 = d.x - d.r
        y1 = d.y - d.r
        w = d.r * 2
        h = d.r * 2
        boxes.append([int(x1), int(y1), int(w), int(h)])
        scores.append(float(d.conf))
    idxs = cv2.dnn.NMSBoxes(boxes, scores, score_threshold=0.3, nms_threshold=float(iou_thr))
    idxs = idxs.flatten().tolist() if len(idxs) else []  # type: ignore
    return [dets[i] for i in idxs]


def _annotate(img_bgr, dets: list[Detection]):
    out = img_bgr.copy()
    for d in dets:
        cv2.circle(out, (d.x, d.y), d.r, (0, 255, 0), 2)
        cv2.circle(out, (d.x, d.y), 2, (255, 0, 0), 3)
    cv2.putText(
        out, f'Detected: {len(dets)}', (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2
    )
    ok, buf = cv2.imencode('.jpg', out, [int(cv2.IMWRITE_JPEG_QUALITY), 88])
    return buf.tobytes()


def _try_aruco_rectify_and_scale(img_bgr, aruco_dict_name: str, marker_mm: float):
    info = {'found': False, 'corners': None, 'dict': aruco_dict_name, 'marker_mm': marker_mm}
    try:
        aruco = cv2.aruco
    except Exception:
        return img_bgr, None, info

    dict_map = {
        'DICT_4X4_50': aruco.DICT_4X4_50,
        'DICT_4X4_100': aruco.DICT_4X4_100,
        'DICT_5X5_50': aruco.DICT_5X5_50,
        'DICT_5X5_100': aruco.DICT_5X5_100,
        'DICT_6X6_50': aruco.DICT_6X6_50,
        'DICT_6X6_100': aruco.DICT_6X6_100,
        'DICT_APRILTAG_36h11': aruco.DICT_APRILTAG_36h11,
    }
    dkey = dict_map.get(aruco_dict_name, aruco.DICT_4X4_50)
    adict = aruco.getPredefinedDictionary(dkey)
    params = aruco.DetectorParameters()
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    detector = aruco.ArucoDetector(adict, params)
    corners, ids, _ = detector.detectMarkers(gray)
    if ids is None or len(corners) == 0:
        return img_bgr, None, info

    # largest marker
    areas = [cv2.contourArea(c[0].astype(np.float32)) for c in corners]
    idx = int(np.argmax(areas))
    c0 = corners[idx][0]
    info.update({'found': True, 'corners': c0.tolist()})

    # order TL, TR, BR, BL
    def order_pts(pts):
        s = pts.sum(axis=1)
        diff = np.diff(pts, axis=1)
        tl = pts[np.argmin(s)]
        br = pts[np.argmax(s)]
        tr = pts[np.argmin(diff)]
        bl = pts[np.argmax(diff)]
        return np.array([tl, tr, br, bl], dtype=np.float32)

    pts = order_pts(c0.astype(np.float32))
    side_px = max(int(np.linalg.norm(pts[0] - pts[1])), 10)
    dst = np.array([[0, 0], [side_px, 0], [side_px, side_px], [0, side_px]], dtype=np.float32)
    H = cv2.getPerspectiveTransform(pts, dst)
    warped = cv2.warpPerspective(img_bgr, H, (img_bgr.shape[1], img_bgr.shape[0]))
    px_per_mm = side_px / max(marker_mm, 1e-6)
    return warped, float(px_per_mm), info


def _get_company_for_warehouse(wh: str) -> str | None:
    if not wh:
        return None
    company = frappe.db.get_value('Warehouse', wh, 'company')
    if company:
        return company  # type: ignore
    return frappe.db.get_single_value('Global Defaults', 'default_company')  # type: ignore


# ----------------------- PDF & Asset Builders -----------------------


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

        # ✅ ensure local page_w/page_h exist in this scope
        c.setPageSize(pagesize)
        page_w, page_h = pagesize

        # --- Page geometry (strict columns) ---
        m = 15 * mm  # outer margin
        header_h = 22 * mm  # header block height
        gutter = 14 * mm  # column gutter (generous)
        left_w = 110 * mm  # text column width
        right_x = m + left_w + gutter
        right_w = page_w - right_x - m
        content_top = page_h - m - header_h
        content_bottom = m + 18 * mm
        content_h = content_top - content_bottom

        # Header
        c.setTitle(f'Pad Shooting Kit: {docname}')
        c.setFont('Helvetica-Bold', 14)
        c.drawString(m, page_h - m - 12, f'Clarinet Pad Shooting Kit ({label})')
        c.setFont('Helvetica', 9)
        info = f'Document: {docname} | ArUco: {aruco_dict} | Marker: {int(marker_mm)} mm'
        info_x = m
        info_y = page_h - m - 28
        info_max_w = left_w
        info_y = _draw_paragraph(
            c, info, info_x, info_y, info_max_w, font_name='Helvetica', font_size=9, leading=11
        )

        # Left column content
        x = m
        y = info_y - 8 * mm

        c.setFont('Helvetica-Bold', 12)
        c.drawString(x, y, 'Step-by-Step: How to Use the Marker Grid')
        y -= 14

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

        # Right column visuals
        marker_pts = marker_mm * mm
        if marker_pts > right_w:
            extra = marker_pts - right_w
            right_x = max(m + left_w + gutter / 2 + 2 * mm, right_x - extra / 2)
            right_w = page_w - right_x - m

        ruler_block_h = 16 * mm
        needed_h = marker_pts + ruler_block_h + 10 * mm
        start_y = content_bottom + max(0, (content_h - needed_h) / 2.0)

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

        # ✅ Ruler block (moved inside this function so page_w/mrk_y are in scope)
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

        # ✅ switch page size for the grid page
        c.setPageSize(pagesize)
        page_w, page_h = pagesize

        m = 20 * mm
        header_h = 16 * mm
        footer_h = 16 * mm
        content_top = page_h - m - header_h
        content_bottom = m + footer_h + 22 * mm  # clear bottom ruler

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

        # mini-ruler — below the page title (above markers)
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

    # Build the document
    c = canvas.Canvas(buf, pagesize=A4)
    draw_single_page(c, A4, 'A4 Single')
    draw_grid_page(c, A4, 'A4 Grid')
    c.save()
    return buf.getvalue()


# ---- text helpers (used by both .py files) ----


def _wrap_lines(c, text: str, max_width: float, font_name='Helvetica', font_size=10):
    """Return a list of lines wrapped to max_width (points)."""
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
    """Draw a wrapped paragraph; return new y below it."""
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
    """Draw a bulleted/numbered list with wrapping for each item; return new y."""
    pad = 10  # indent after bullet/number
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


def _build_instruction_image(marker_png: bytes, marker_mm: float, aruco_dict: str) -> bytes:
    """Compact instruction image (JPG) used to pre-populate the Photo field."""
    if not HAS_CV2:
        return marker_png
    W, H = 1080, 1440
    img = np.full((H, W, 3), 245, dtype=np.uint8)
    cv2.rectangle(img, (0, 0), (W, 120), (40, 40, 40), -1)
    cv2.putText(
        img,
        'Shooting Instructions',
        (30, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.6,
        (255, 255, 255),
        3,
        cv2.LINE_AA,
    )

    marker = cv2.imdecode(np.frombuffer(marker_png, np.uint8), cv2.IMREAD_UNCHANGED)
    marker_side = 320
    mk = cv2.resize(marker, (marker_side, marker_side), interpolation=cv2.INTER_AREA)
    x0 = W - marker_side - 40
    y0 = 160
    if mk.ndim == 3 and mk.shape[2] == 4:
        alpha = mk[:, :, 3] / 255.0
        bg = np.ones((marker_side, marker_side, 3), dtype=np.uint8) * 255
        for c in range(3):
            bg[:, :, c] = (alpha * mk[:, :, c] + (1 - alpha) * bg[:, :, c]).astype(np.uint8)
        mk = bg
    img[y0 : y0 + marker_side, x0 : x0 + marker_side] = mk

    bullets = [
        f'Print the kit PDF at 100% (marker = {int(marker_mm)} mm).',
        'Place marker on matte dark background.',
        'Top-down shot; keep camera parallel.',
        'Separate pads (gap ≥ 1/2 pad).',
        'Avoid glare/blur; shortest side ≥ 2000 px.',
        'Upload this photo here, then click Process Image.',
    ]
    y = 170
    for b in bullets:
        cv2.circle(img, (40, y - 10), 6, (50, 50, 50), -1)
        cv2.putText(img, b, (65, y), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (20, 20, 20), 2, cv2.LINE_AA)
        y += 60

    cv2.putText(
        img,
        f'ArUco: {aruco_dict}',
        (40, H - 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (80, 80, 80),
        2,
        cv2.LINE_AA,
    )
    ok, jpg = cv2.imencode('.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
    if not ok:
        raise RuntimeError('Failed to encode instruction JPG.')
    return jpg.tobytes()
