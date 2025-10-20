from __future__ import annotations

import io
import json
import math
import statistics
from typing import Any

import frappe
from frappe import _

# Optional scientific stack (plots will be skipped if not present)
try:
    import numpy as np  # type: ignore
except Exception:  # pragma: no cover
    np = None  # type: ignore

try:
    import matplotlib

    matplotlib.use("Agg")  # headless
    import matplotlib.pyplot as plt  # type: ignore
except Exception:  # pragma: no cover
    plt = None  # type: ignore


# --------- Utilities ---------


def _json(obj: Any) -> str:
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)


def _parse(s: Any) -> Any:
    if not s:
        return None
    if isinstance(s, (dict, list)):
        return s
    try:
        return json.loads(s)
    except Exception:
        return None


def _attach_png(fig_or_bytes, filename: str, attach_to_doctype: str, attach_to_name: str) -> str:
    """Attach a PNG and return the public file_name."""
    if plt is not None and hasattr(fig_or_bytes, "savefig"):
        bio = io.BytesIO()
        fig_or_bytes.savefig(bio, format="png", dpi=160, bbox_inches="tight")
        plt.close(fig_or_bytes)
        content = bio.getvalue()
    else:
        # already bytes
        content = fig_or_bytes if isinstance(fig_or_bytes, (bytes, bytearray)) else b""

    filedoc = frappe.get_doc(
        {
            "doctype": "File",
            "file_name": filename,
            "attached_to_doctype": attach_to_doctype,
            "attached_to_name": attach_to_name,
            "is_private": 0,
            "content": content,
        }
    )
    filedoc.insert(ignore_permissions=True)
    return filedoc.file_name  # type: ignore


def _note_grid(freq: float, a4: float) -> tuple[int, float]:
    """Return nearest MIDI and cents error at given A4."""
    midi = 69 + 12 * math.log2(freq / a4)
    mround = int(round(midi))
    target = a4 * (2 ** ((mround - 69) / 12))
    cents = 1200 * math.log2(freq / target)
    return mround, cents


def _group_register(note_name: str) -> str:
    # naive register grouping based on octave digit
    try:
        octv = int(note_name[-1])
        return "chalumeau" if octv <= 4 else "clarion"
    except Exception:
        return "unknown"


# --------- Main entry ---------


def run_analysis(session: str, test: str) -> None:
    """Background entry point. Mutates the child row inside Lab Session."""
    sess = frappe.get_doc("Lab Session", session)
    row = next((t for t in sess.tests if t.name == test), None)  # type: ignore
    if not row:
        frappe.throw(_("Lab Test not found"))

    row.status = "Analyzing"  # type: ignore
    row.analysis_started = frappe.utils.now_datetime()  # type: ignore
    sess.save(ignore_permissions=True)

    # dispatch
    ttype = row.test_type  # type: ignore
    raw = _parse(row.raw_json) or {}  # type: ignore
    cfg = _parse(row.config_json) or {}  # type: ignore
    a4 = float(sess.reference_pitch or 440)  # type: ignore

    plots: list[str] = []
    metrics: dict[str, Any] = {}
    points: list[dict[str, Any]] = []

    try:
        if ttype == "intonation":
            metrics, points, plots = _analyze_intonation(sess, row, raw, a4)
        elif ttype == "resonance":
            metrics, points, plots = _analyze_resonance(sess, row, raw, a4)
        elif ttype == "leak":
            metrics, points, plots = _analyze_leak(sess, row, raw)
        elif ttype == "tone_fitness":
            metrics, points, plots = _analyze_tone(sess, row, raw)
        elif ttype == "reed_match":
            metrics, points, plots = _analyze_reed_match(sess, row, raw)
        elif ttype == "measurement":
            metrics, points, plots = _analyze_measurement(sess, row, raw)
        else:
            metrics = {"warning": f"Unknown test_type: {ttype}"}
    except Exception:
        frappe.log_error(title=f"Lab analysis failed ({ttype})", message=frappe.get_traceback())
        metrics = {"error": "analysis_failed"}

    # commit results to child row
    row.metrics_json = _json(metrics)
    row.features_json = row.features_json or ""  # type: ignore # reserved
    # rewrite points table
    row.points = []  # type: ignore
    for p in points:
        row.append("points", p)  # type: ignore
    # merge plots (include any client snapshots)
    existing_plots = _parse(row.plots_json) or []  # type: ignore
    row.plots_json = _json(list(dict.fromkeys(existing_plots + plots)))  # type: ignore
    row.status = "Complete"  # type: ignore
    row.analysis_completed = frappe.utils.now_datetime()  # type: ignore
    sess.save(ignore_permissions=True)

    # Update session rollups and Instrument Wellness Summary
    _update_rollups(sess)
    _update_instrument_wellness(sess)


# --------- Per-test analyzers ---------


def _analyze_intonation(sess, row, raw, a4: float):
    frames = raw.get("frames") or []
    if not frames:
        return ({"warning": "no_frames"}, [], [])

    # Aggregate by note name
    bucket: dict[str, dict[str, Any]] = {}
    cents_all: list[float] = []
    for fr in frames:
        f0 = float(fr.get("f0") or 0)
        conf = float(fr.get("conf") or 0)
        name = fr.get("name") or ""
        if f0 <= 0 or conf <= 0.05 or not name:
            continue
        # compute cents at server to be safe
        midi, cents = _note_grid(f0, a4)
        cents_all.append(cents)
        b = bucket.setdefault(name, {"sum": 0.0, "n": 0, "vals": []})
        b["sum"] += cents
        b["n"] += 1
        b["vals"].append(cents)

    per_note: list[tuple[str, float, float]] = []
    for name, agg in bucket.items():
        n = max(1, agg["n"])
        avg = agg["sum"] / n
        std = statistics.pstdev(agg["vals"]) if len(agg["vals"]) > 1 else 0.0
        per_note.append((name, avg, std))

    per_note.sort(key=lambda x: x[0])

    # metrics
    avg_dev = statistics.mean([x[1] for x in per_note]) if per_note else 0.0
    stdev_cents = statistics.pstdev(cents_all) if len(cents_all) > 1 else 0.0
    score = max(0.0, 100.0 - min(100.0, abs(avg_dev) * 2.0 + stdev_cents * 1.5))

    # points table (note as label, y=avg cents, z=std)
    points = [
        {"label": name, "group": _group_register(name), "x": 0.0, "y": float(avg), "z": float(std)}
        for (name, avg, std) in per_note
    ]

    plots: list[str] = []
    if plt is not None:
        # Heatmap-like bar: note vs avg cents
        fig, ax = plt.subplots(figsize=(8, 2.8))
        labels = [p[0] for p in per_note]
        vals = [p[1] for p in per_note]
        ax.bar(range(len(vals)), vals)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=90)
        ax.axhline(0, color="#444", linewidth=1)
        ax.set_ylabel("cents")
        ax.set_title("Intonation (avg cents per note)")
        plots.append(_attach_png(fig, f"{row.name}_intonation_bar.png", "Lab Session", sess.name))

        # Drift strip (use 1Hz time bucket medians)
        ts_pairs = [
            (float(fr.get("t") or 0), float(fr.get("f0") or 0)) for fr in frames if fr.get("t") is not None
        ]
        if ts_pairs:
            ts_pairs.sort()
            if np is not None:
                times = np.array([t for t, _ in ts_pairs])
                freqs = np.array([f for _, f in ts_pairs])
                mids = 69 + 12 * np.log2(freqs / a4)
                mids_r = np.round(mids)
                target = a4 * (2 ** ((mids_r - 69) / 12))
                cents_series = 1200 * np.log2(freqs / target)
                fig2, ax2 = plt.subplots(figsize=(8, 2.2))
                ax2.plot(times - times.min(), cents_series, linewidth=0.8)
                ax2.axhline(0, color="#444", linewidth=1)
                ax2.set_xlabel("time (s)")
                ax2.set_ylabel("cents")
                ax2.set_title("Cents drift")
                plots.append(_attach_png(fig2, f"{row.name}_drift.png", "Lab Session", sess.name))
    metrics = {
        "avg_cent_dev": round(avg_dev, 2),
        "stability_std_cents": round(stdev_cents, 2),
        "intonation_score": round(score, 2),
        "notes_counted": len(per_note),
    }
    return (metrics, points, plots)


def _analyze_resonance(sess, row, raw, a4: float):
    resp = raw.get("response") or {}
    freq = resp.get("freq") or []
    magdb = resp.get("magdb") or []
    if not freq or not magdb:
        return ({"warning": "no_response"}, [], [])

    # simple peak picking
    peaks: list[tuple[float, float]] = []  # (f, mag)
    for i in range(2, len(magdb) - 2):
        left = magdb[i - 1]
        right = magdb[i + 1]
        if magdb[i] > left and magdb[i] > right and magdb[i] > (max(left, right) + 1.0):
            peaks.append((float(freq[i]), float(magdb[i])))

    # reduce to top N by magnitude, spaced
    peaks.sort(key=lambda x: x[1], reverse=True)
    filtered: list[tuple[float, float]] = []
    for f, m in peaks:
        if all(abs(f - pf) > 30.0 for pf, _ in filtered):
            filtered.append((f, m))
        if len(filtered) >= 12:
            break

    # points table: peaks (x=freq, y=mag)
    points = [
        {"label": f"Peak {i+1}", "group": "ESS-peaks", "x": float(f), "y": float(m)}
        for i, (f, m) in enumerate(filtered)
    ]

    # metric: alignment to tempered note grid (average nearest cents offset at peaks)
    offsets = []
    for f, _ in filtered:
        _, cents = _note_grid(f, a4)
        offsets.append(abs(cents))
    align = statistics.mean(offsets) if offsets else 0.0
    score = max(0.0, 100.0 - min(100.0, align * 8.0))

    plots: list[str] = []
    if plt is not None:
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.plot(freq, magdb, linewidth=0.8)
        ax.set_xlabel("Hz")
        ax.set_ylabel("|H(f)| (dB)")
        ax.set_title("Resonance response")
        for f, m in filtered:
            ax.scatter([f], [m], color="red", s=12)
        # overlay note grid in background (every semitone ~ from 100–4000 Hz)
        if np is not None:
            fmin, fmax = 80, 4000
            frs = []
            m = 21  # A0 midi
            while True:
                hz = a4 * (2 ** ((m - 69) / 12))
                if hz > fmax:
                    break
                if hz >= fmin:
                    frs.append((hz, m))
                m += 1
            for hz, mm in frs:
                ax.axvline(hz, color="#ddd", linewidth=0.4)
        plots.append(_attach_png(fig, f"{row.name}_resonance.png", "Lab Session", sess.name))

    metrics = {
        "peaks_count": len(filtered),
        "avg_peak_offset_cents": round(align, 2),
        "resonance_score": round(score, 2),
    }
    return (metrics, points, plots)


def _analyze_leak(sess, row, raw):
    # Expect raw = { "holes": [{"label":"LH1","score":0..1}, ...] }
    holes = raw.get("holes") or []
    if not holes:
        return ({"warning": "no_holes"}, [], [])

    vals = [float(h.get("score") or 0.0) for h in holes]
    leak_idx = statistics.mean(vals) if vals else 0.0
    score = max(0.0, 100.0 - min(100.0, leak_idx * 100.0))

    points = [
        {
            "label": str(h.get("label") or ""),
            "group": "leak",
            "x": 0.0,
            "y": float(h.get("score") or 0.0),
        }
        for h in holes
    ]

    plots: list[str] = []
    if plt is not None:
        labels = [str(h.get("label") or "") for h in holes]
        fig, ax = plt.subplots(figsize=(8, 2.5))
        ax.bar(range(len(vals)), vals)
        ax.set_xticks(range(len(vals)))
        ax.set_xticklabels(labels, rotation=90)
        ax.set_ylim(0, 1)
        ax.set_ylabel("leak score")
        ax.set_title("Per-hole leak")
        plots.append(_attach_png(fig, f"{row.name}_leak.png", "Lab Session", sess.name))

    metrics = {"leak_index": round(leak_idx, 3), "leak_score": round(score, 2)}
    return (metrics, points, plots)


def _analyze_tone(sess, row, raw):
    # Expect raw = {"frames":[{"t":..,"centroid":..,"spread":..,"flux":..,"odd_even":..}, ...]}
    frames = raw.get("frames") or []
    if not frames:
        return ({"warning": "no_frames"}, [], [])

    centroid = [float(f.get("centroid") or 0.0) for f in frames]
    spread = [float(f.get("spread") or 0.0) for f in frames]
    flux = [float(f.get("flux") or 0.0) for f in frames]
    odd_even = [float(f.get("odd_even") or 0.0) for f in frames]

    # simple targets (illustrative)
    tgt_centroid = 2500.0
    tone_err = abs((statistics.mean(centroid) if centroid else 0.0) - tgt_centroid) / 100.0
    flux_pen = statistics.mean([abs(x) for x in flux]) if flux else 0.0
    oe_pen = abs((statistics.mean(odd_even) if odd_even else 0.0) - 1.0)
    score = max(0.0, 100.0 - min(100.0, tone_err + flux_pen + oe_pen))

    points = []

    plots: list[str] = []
    if plt is not None and frames:
        t = [float(f.get("t") or 0.0) for f in frames]
        fig, ax = plt.subplots(figsize=(8, 2.5))
        ax.plot(t, centroid, linewidth=0.8, label="centroid")
        ax.set_xlabel("time (s)")
        ax.set_ylabel("Hz")
        ax.set_title("Spectral centroid")
        plots.append(_attach_png(fig, f"{row.name}_centroid.png", "Lab Session", sess.name))

    metrics = {
        "tone_score": round(score, 2),
        "centroid_mean": round(statistics.mean(centroid) if centroid else 0.0, 2),
        "centroid_std": round(statistics.pstdev(centroid) if len(centroid) > 1 else 0.0, 2),
    }
    return (metrics, points, plots)


def _analyze_reed_match(sess, row, raw):
    # Placeholder: pick top 3 reeds closest to reference centroid / odd_even
    reeds = raw.get("reeds") or []  # [{"id":..,"centroid":..,"odd_even":..}, ...]
    if not reeds:
        return ({"warning": "no_reeds"}, [], [])
    scored = []
    for r in reeds:
        c = float(r.get("centroid") or 0.0)
        oe = float(r.get("odd_even") or 1.0)
        err = abs(c - 2500.0) / 100.0 + abs(oe - 1.0)
        scored.append((err, r))
    scored.sort(key=lambda x: x[0])
    top = [x[1] for x in scored[:3]]
    metrics = {"recommended_reeds": top}
    return (metrics, [], [])


def _analyze_measurement(sess, row, raw):
    # Pass-through; expects raw = {"params":[{"label":"...","value":..,"unit":".."}, ...]}
    params = raw.get("params") or []
    points = [
        {
            "label": str(p.get("label") or ""),
            "group": "measurement",
            "x": 0.0,
            "y": float(p.get("value") or 0.0),
            "meta_json": json.dumps({"unit": p.get("unit")}),
        }
        for p in params
    ]
    return ({"count": len(params)}, points, [])


# --------- Rollups & Wellness ---------


def _update_rollups(sess_doc):
    """Compute per-session roll-up scores from tests' metrics."""
    ints = []
    ress = []
    leaks = []
    tones = []
    for t in sess_doc.tests or []:
        m = _parse(t.metrics_json) or {}
        if "intonation_score" in m:
            ints.append(float(m["intonation_score"]))
        if "resonance_score" in m:
            ress.append(float(m["resonance_score"]))
        if "leak_score" in m:
            leaks.append(float(m["leak_score"]))
        if "tone_score" in m:
            tones.append(float(m["tone_score"]))

    sess_doc.intonation_score = round(statistics.mean(ints), 2) if ints else None
    sess_doc.resonance_score = round(statistics.mean(ress), 2) if ress else None
    sess_doc.leak_score = round(statistics.mean(leaks), 2) if leaks else None
    sess_doc.tone_score = round(statistics.mean(tones), 2) if tones else None

    # overall weighted mean
    weights = {"intonation": 0.35, "resonance": 0.25, "leak": 0.25, "tone": 0.15}
    parts = []
    if sess_doc.intonation_score is not None:
        parts.append(sess_doc.intonation_score * weights["intonation"])
    if sess_doc.resonance_score is not None:
        parts.append(sess_doc.resonance_score * weights["resonance"])
    if sess_doc.leak_score is not None:
        parts.append(sess_doc.leak_score * weights["leak"])
    if sess_doc.tone_score is not None:
        parts.append(sess_doc.tone_score * weights["tone"])
    sess_doc.overall_score = round(sum(parts), 2) if parts else None

    sess_doc.save(ignore_permissions=True)


def _update_instrument_wellness(sess_doc):
    inst = getattr(sess_doc, "instrument", None)
    if not inst:
        return
    name = frappe.db.get_value("Instrument Wellness Summary", {"instrument": inst}, "name")
    if name:
        iws = frappe.get_doc("Instrument Wellness Summary", name)  # type: ignore
    else:
        iws = frappe.get_doc({"doctype": "Instrument Wellness Summary", "instrument": inst})
    iws.last_session = sess_doc.name  # type: ignore
    iws.intonation_score = sess_doc.intonation_score  # type: ignore
    iws.resonance_score = sess_doc.resonance_score  # type: ignore
    iws.leak_score = sess_doc.leak_score  # type: ignore
    iws.tone_score = sess_doc.tone_score  # type: ignore
    iws.overall_score = sess_doc.overall_score  # type: ignore

    # append trend datapoint
    trend = _parse(iws.trend_json) or []  # type: ignore
    trend.append({"ts": frappe.utils.now(), "session": sess_doc.name, "overall": iws.overall_score})  # type: ignore
    # keep last 50
    iws.trend_json = _json(trend[-50:])  # type: ignore
    iws.save(ignore_permissions=True)
