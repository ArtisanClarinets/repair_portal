# your_app/your_app/api/lab_capture.py
from __future__ import annotations
import base64, io, os, subprocess, tempfile, json
from typing import Optional
import frappe

# Adjust to where you saved the analyzer file:
from your_app.analysis.lab_analysis_pro_plus import run_analysis

AUDIO_DIR = "lab_audio"  # files will be under /private/files/lab_audio/

def _ensure_dir():
    path = frappe.get_site_path("private", "files", AUDIO_DIR)
    os.makedirs(path, exist_ok=True)
    return path

def _save_data_url_to_file(data_url: str, filename: str) -> str:
    # data_url like: data:audio/webm;base64,AAAA...
    head, b64 = data_url.split(",", 1)
    raw = base64.b64decode(b64)
    path = os.path.join(_ensure_dir(), filename)
    with open(path, "wb") as f:
        f.write(raw)
    return path

def _ffmpeg_transcode_to_wav48k_mono(in_path: str) -> str:
    out_path = os.path.splitext(in_path)[0] + ".wav"
    cmd = [
        "ffmpeg", "-y",
        "-i", in_path,
        "-ac", "1",           # mono
        "-ar", "48000",       # 48 kHz
        "-sample_fmt", "s16", # 16-bit PCM
        out_path,
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return out_path

def _attach_file(path: str, filename: str, doctype: str, name: str, is_private: int = 1) -> str:
    with open(path, "rb") as f:
        content = f.read()
    filedoc = frappe.get_doc({
        "doctype": "File",
        "file_name": filename,
        "attached_to_doctype": doctype,
        "attached_to_name": name,
        "is_private": is_private,
        "content": content
    }).insert(ignore_permissions=True)
    return filedoc.file_name  # public URL if public, else /private/files/...

@frappe.whitelist()
def start_session(instrument: str, a4: float = 440.0) -> str:
    """Create a Lab Session with defaults. Returns session name."""
    sess = frappe.get_doc({
        "doctype": "Lab Session",
        "instrument": instrument,
        "reference_pitch": float(a4),
        "tests": []
    }).insert(ignore_permissions=True)
    return sess.name

@frappe.whitelist()
def upload_take(session: str,
                test_type: str,
                data_url: str,
                cfg_json: str = "{}",
                filename: Optional[str] = None) -> dict:
    """
    Accept a browser/mobile recording via data URL.
    - Saves original (webm/mp4/wav), transcodes to wav 48k mono for analysis
    - Creates/updates a Lab Test row and enqueues analysis
    Returns: {session, test, file_orig, file_wav}
    """
    sess = frappe.get_doc("Lab Session", session)
    cfg = json.loads(cfg_json or "{}")

    # 1) persist upload
    filename = filename or f"{frappe.utils.now_datetime().isoformat()}_{frappe.generate_hash(length=6)}.webm"
    local_path = _save_data_url_to_file(data_url, filename)

    # 2) transcode for analysis
    try:
        wav_path = _ffmpeg_transcode_to_wav48k_mono(local_path)
    except Exception:
        # if already wav, keep going
        if not filename.lower().endswith(".wav"):
            raise

    # 3) create Lab Test child row
    row = None
    for t in sess.tests or []:
        if t.test_type == test_type and t.status in (None, "", "Pending"):
            row = t
            break
    if not row:
        row = sess.append("tests", {
            "test_type": test_type,
            "status": "Queued",
            "raw_json": "{}",
            "config_json": json.dumps(cfg)
        })
    sess.save(ignore_permissions=True)

    # 4) attach both files (original + wav) to the session for traceability
    file_orig = _attach_file(local_path, os.path.basename(local_path), "Lab Session", sess.name, is_private=1)
    wav_final = wav_path if local_path.endswith(".wav") else os.path.splitext(local_path)[0] + ".wav"
    file_wav  = _attach_file(wav_final, os.path.basename(wav_final), "Lab Session", sess.name, is_private=1)

    # 5) set raw_json for analyzer
    row.status = "Queued"
    row.raw_json = json.dumps({"audio_path": file_wav})   # analyzer reads this path
    row.config_json = json.dumps(cfg or {})
    sess.save(ignore_permissions=True)

    # 6) enqueue analysis
    frappe.enqueue(run_analysis, queue="long", session=sess.name, test=row.name)

    return {"session": sess.name, "test": row.name, "file_orig": file_orig, "file_wav": file_wav}