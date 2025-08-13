from __future__ import annotations
import base64, json, math
from typing import Dict, Any, List, Tuple
import frappe
from frappe import _
from frappe.utils import now
from frappe.model.document import Document

# -------- internals --------
def _get_or_create_design(prototype: str) -> Document:
    res = frappe.get_all("Clarinet Design", filters={"prototype": prototype}, pluck="name")
    if res:
        return frappe.get_doc("Clarinet Design", res[0])
    proto = frappe.get_doc("Prototype", prototype)
    title = f"{getattr(proto,'title',None) or prototype} Design"
    d = frappe.get_doc({
        "doctype": "Clarinet Design",
        "prototype": prototype,
        "title": title,
        "clarinet_type": "B♭",
        "overall_length_mm": 600,
        "barrel_length_mm": 66,
        "upper_joint_length_mm": 230,
        "tenon_gap_mm": 2.0,
        "lower_joint_length_mm": 250,
        "bell_length_mm": 110,
        "wall_thickness_mm": 2.5,
        "grid_mm": 5.0
    }).insert(ignore_permissions=True)
    frappe.db.commit()
    return d

def _interp_bore_mm(bore: List[Dict[str, float]], x_mm: float) -> float:
    if not bore:  # default clarinet-ish
        return 14.6
    bore = sorted(bore, key=lambda s: s["x_mm"])
    if x_mm <= bore[0]["x_mm"]:
        return bore[0]["bore_mm"]
    if x_mm >= bore[-1]["x_mm"]:
        return bore[-1]["bore_mm"]
    for i in range(len(bore)-1):
        x0, d0 = bore[i]["x_mm"], bore[i]["bore_mm"]
        x1, d1 = bore[i+1]["x_mm"], bore[i+1]["bore_mm"]
        if x0 <= x_mm <= x1:
            t = (x_mm - x0) / (x1 - x0) if x1 != x0 else 0.0
            return d0 + t*(d1 - d0)
    return bore[-1]["bore_mm"]

# -------- CRUD / attachments --------
@frappe.whitelist()
def load_design(prototype: str) -> Dict[str, Any]:
    frappe.only_for(("System Manager","Manufacturing Manager","Manufacturing User"))
    d = _get_or_create_design(prototype)
    return {
        "design_name": d.name,
        "title": d.title,
        "clarinet_type": d.clarinet_type,
        "overall_length_mm": d.overall_length_mm,
        "barrel_length_mm": d.barrel_length_mm,
        "upper_joint_length_mm": d.upper_joint_length_mm,
        "tenon_gap_mm": d.tenon_gap_mm,
        "lower_joint_length_mm": d.lower_joint_length_mm,
        "bell_length_mm": d.bell_length_mm,
        "wall_thickness_mm": d.wall_thickness_mm,
        "grid_mm": d.grid_mm,
        "bore_segments": [{"x_mm": s.x_mm, "bore_mm": s.bore_mm, "notes": s.notes or ""} for s in d.bore_segments],
        "tone_holes": [{
            "name_label": h.name_label, "note_label": h.note_label, "joint": h.joint,
            "x_mm": h.x_mm, "diameter_mm": h.diameter_mm, "chimney_mm": h.chimney_mm,
            "undercut_pct": h.undercut_pct, "azimuth_deg": h.azimuth_deg, "y_offset_mm": h.y_offset_mm,
            "ringed": int(h.ringed or 0), "is_open_key": int(h.is_open_key or 0),
            "notes": h.notes or ""
        } for h in d.tone_holes],
    }

@frappe.whitelist()
def save_design(prototype: str, payload: str) -> str:
    frappe.only_for(("System Manager","Manufacturing Manager","Manufacturing User"))
    data = json.loads(payload)
    d = _get_or_create_design(prototype)
    for k in ("title","clarinet_type","overall_length_mm","barrel_length_mm",
              "upper_joint_length_mm","tenon_gap_mm","lower_joint_length_mm",
              "bell_length_mm","wall_thickness_mm","grid_mm"):
        if k in data: setattr(d, k, data[k])
    d.set("bore_segments", [])
    for s in data.get("bore_segments", []):
        d.append("bore_segments", {"x_mm": float(s["x_mm"]), "bore_mm": float(s["bore_mm"]), "notes": s.get("notes","")})
    d.set("tone_holes", [])
    for h in data.get("tone_holes", []):
        d.append("tone_holes", {
            "name_label": h.get("name_label"),
            "note_label": h.get("note_label"),
            "joint": h.get("joint","Upper"),
            "x_mm": float(h["x_mm"]),
            "diameter_mm": float(h["diameter_mm"]),
            "chimney_mm": float(h.get("chimney_mm", 4.0)),
            "undercut_pct": float(h.get("undercut_pct", 0.0)),
            "azimuth_deg": float(h.get("azimuth_deg", 0.0)),
            "y_offset_mm": float(h.get("y_offset_mm", 0.0)),
            "ringed": int(h.get("ringed", 0)),
            "is_open_key": int(h.get("is_open_key", 0)),
            "notes": h.get("notes","")
        })
    d.save(ignore_permissions=True)
    frappe.db.commit()
    return d.name

@frappe.whitelist()
def export_svg(prototype: str, svg_text_b64: str) -> str:
    frappe.only_for(("System Manager","Manufacturing Manager","Manufacturing User"))
    d = _get_or_create_design(prototype)
    svg_text = base64.b64decode(svg_text_b64).decode("utf-8", errors="ignore")
    fname = f"{d.name}-{now().replace(' ','_').replace(':','-')}.svg"
    filedoc = frappe.get_doc({
        "doctype": "File",
        "file_name": fname,
        "attached_to_doctype": "Clarinet Design",
        "attached_to_name": d.name,
        "content": svg_text,
        "decode": 1,
        "is_private": 0
    }).insert(ignore_permissions=True)
    frappe.db.commit()
    return filedoc.file_url

@frappe.whitelist()
def export_png(prototype: str, png_b64: str) -> str:
    frappe.only_for(("System Manager","Manufacturing Manager","Manufacturing User"))
    d = _get_or_create_design(prototype)
    content = base64.b64decode(png_b64)
    fname = f"{d.name}-{now().replace(' ','_').replace(':','-')}.png"
    filedoc = frappe.get_doc({
        "doctype": "File",
        "file_name": fname,
        "attached_to_doctype": "Clarinet Design",
        "attached_to_name": d.name,
        "content": content,
        "decode": 1,
        "is_private": 0
    }).insert(ignore_permissions=True)
    frappe.db.commit()
    return filedoc.file_url

# -------- OpenWind bridge --------
@frappe.whitelist()
def build_openwind_json(prototype: str) -> str:
    """Return OpenWind-style JSON string built from Clarinet Design."""
    d = _get_or_create_design(prototype)
    bore = [{"x_mm": s.x_mm, "diameter_mm": s.bore_mm} for s in d.bore_segments]
    holes = [{
        "name": h.name_label, "note": h.note_label, "x_mm": h.x_mm,
        "diameter_mm": h.diameter_mm, "chimney_mm": h.chimney_mm,
        "azimuth_deg": h.azimuth_deg, "undercut_pct": h.undercut_pct
    } for h in d.tone_holes]
    payload = {
        "instrument": {"family": "clarinet", "variant": d.clarinet_type},
        "geometry": {
            "length_mm": d.overall_length_mm,
            "barrel_length_mm": d.barrel_length_mm,
            "upper_joint_length_mm": d.upper_joint_length_mm,
            "tenon_gap_mm": d.tenon_gap_mm,
            "lower_joint_length_mm": d.lower_joint_length_mm,
            "bell_length_mm": d.bell_length_mm,
            "bore_profile": bore,
            "tone_holes": holes
        },
        "solver": {
            "f_min_hz": 50.0, "f_max_hz": 4000.0, "df_hz": 5.0,
            "temperature_C": 20.0, "humidity_pct": 50.0
        },
        "meta": {"source": "ERPNext Clarinet Editor", "prototype": prototype}
    }
    return json.dumps(payload)

@frappe.whitelist()
def run_openwind(prototype: str, solver_params_json: str | None = None) -> Dict[str, Any]:
    """POST to OpenWind solver. Returns dict with frequencies/Z (or passthrough)."""
    frappe.only_for(("System Manager","Manufacturing Manager","Manufacturing User"))
    ow_url = frappe.conf.get("openwind_url")
    if not ow_url:
        frappe.throw(_("Missing site_config 'openwind_url'"))
    payload = json.loads(build_openwind_json(prototype))
    if solver_params_json:
        payload["solver"].update(json.loads(solver_params_json))
    headers = {"Content-Type": "application/json"}
    api_key = frappe.conf.get("openwind_api_key")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    # requests is vendored in frappe (frappe.integrations.utils)
    import requests
    r = requests.post(ow_url, headers=headers, data=json.dumps(payload), timeout=120)
    r.raise_for_status()
    try:
        out = r.json()
    except Exception:
        # if server returns raw PNG base64
        out = {"plot_png_b64": base64.b64encode(r.content).decode("ascii")}
    return out

@frappe.whitelist()
def tolerance_report(prototype: str, min_clearance_mm: float = 0.6) -> Dict[str, Any]:
    """Compute per-hole safety vs outer diameter (bore + 2*wall)."""
    d = _get_or_create_design(prototype)
    bore = [{"x_mm": s.x_mm, "bore_mm": s.bore_mm} for s in d.bore_segments]
    report = []
    for h in d.tone_holes:
        bore_d = _interp_bore_mm(bore, h.x_mm)
        outer_d = bore_d + 2.0*(d.wall_thickness_mm or 0)
        eff_hole_d = (h.diameter_mm or 0) * (1.0 + (h.undercut_pct or 0)/100.0)
        margin = outer_d - eff_hole_d
        ok = (margin >= min_clearance_mm)
        report.append({
            "name": h.name_label, "x_mm": h.x_mm, "bore_d_mm": bore_d,
            "outer_d_mm": outer_d, "eff_hole_d_mm": eff_hole_d,
            "margin_mm": margin, "ok": int(ok)
        })
    return {"min_clearance_mm": min_clearance_mm, "holes": report}
