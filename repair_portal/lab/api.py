# File Header Template
# Relative Path: repair_portal/lab/api.py
# Last Updated: 2025-07-24
# Version: v1.8-patched
# Purpose: Fortune-500 Lab API for instrument diagnostics, file uploads, and signal analytics
# Dependencies: Frappe, Instrument Profile, Impedance Snapshot, Tone Fitness, Leak Test, librosa, soundfile, numpy

from __future__ import annotations

import base64
import math

import frappe
from frappe import _
from frappe.utils import now_datetime

MAX_RECORDING_SIZE = 20 * 1024 * 1024  # 20MB


class LabAPIError(frappe.ValidationError):
	"""Custom error class for lab API errors, logs automatically."""

	def __init__(self, message):
		super().__init__(message)
		frappe.log_error(message, "Lab API Error")


def _attach_file(parent_doc, b64, fname):
	"""Attach a decoded base64 file to a document (private, no public URL)."""
	if not b64:
		return
	content = base64.b64decode(b64)
	if len(content) > MAX_RECORDING_SIZE:
		raise LabAPIError(_("Recording file too large (>20MB)."))
	file_doc = frappe.get_doc(
		{
			"doctype": "File",
			"file_name": fname,
			"attached_to_doctype": parent_doc.doctype,
			"attached_to_name": parent_doc.name,
			"is_private": 1,
			"content": content,
		}
	)
	file_doc.save(ignore_permissions=True)
	return file_doc


def freq_to_note(freq):
	"""Convert frequency (Hz) to note name (e.g., A4)."""
	if not freq:
		return "—"
	note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
	n = round(12 * math.log2(freq / 440.0) + 57)
	return note_names[n % 12] + str(n // 12 - 1)


def calc_cents(freq):
	"""Calculate cents offset from A440 for tuning."""
	if not freq:
		return 0
	n = 12 * math.log2(freq / 440.0)
	nearest = round(n)
	return (n - nearest) * 100


@frappe.whitelist(allow_guest=False)
def get_instruments():
	"""
	Get all enabled instrument profiles for use in dropdowns.
	Security: Only for Technician or Lab roles.
	Returns:
	    list: [{ 'name': ..., 'instrument': ..., 'brand': ..., 'model': ... }]
	"""
	user = frappe.session.user
	roles = frappe.get_roles(user)
	if "Technician" not in roles and "Lab" not in roles:
		frappe.log_error(f"Unauthorized instrument access attempt by {user}", "Lab API Security")
		frappe.throw(_("You do not have permission to access instruments."), frappe.PermissionError)
	instruments = frappe.get_all(
		"Instrument Profile", filters={}, fields=["name", "instrument", "brand", "model"]
	)
	return instruments


@frappe.whitelist(allow_guest=False, methods=["POST"])
def save_impedance_snapshot(instrument=None, raw_data="{}", recording_base64=None, filename=None):
	"""
	Save a new impedance snapshot and attach the audio file.
	Args:
	    instrument (str): Name of Instrument Profile (required)
	    raw_data (str): Optional JSON string with raw measurement data
	    recording_base64 (str): Required. Audio as base64 webm
	    filename (str): Optional filename
	Returns:
	    dict: { "name": <Impedance Snapshot name> }
	"""
	user = frappe.session.user
	roles = frappe.get_roles(user)
	if "Technician" not in roles and "Lab" not in roles:
		frappe.throw(_("Only Technicians can record impedance data."), frappe.PermissionError)

	if not instrument:
		raise LabAPIError(_("Instrument is required."))
	if not recording_base64 or len(recording_base64) < 100:
		raise LabAPIError(_("Recording missing or too short."))

	try:
		# Attach file
		file_doc = None
		if filename:
			file_doc = _attach_file(
				parent_doc=frappe.get_doc("Instrument Profile", instrument),
				b64=recording_base64,
				fname=filename,
			)

		# Create snapshot doc
		snapshot = frappe.new_doc("Impedance Snapshot")
		snapshot.instrument = instrument
		snapshot.raw_data = raw_data or "{}"
		if file_doc:
			snapshot.file = file_doc.file_url
		snapshot.owner = user
		snapshot.insert(ignore_permissions=True)
		frappe.db.commit()

		frappe.logger().info(f"Impedance snapshot saved by {user} for {instrument} ({snapshot.name})")
		return {"name": snapshot.name}
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Lab API: Save Impedance Snapshot Error")
		raise LabAPIError(_("Failed to save impedance snapshot."))


@frappe.whitelist(allow_guest=False, methods=["POST"])
def save_intonation_session(instrument=None, recording_base64=None, filename=None):
	"""
	Save an intonation session and attach the audio file.
	Args:
	    instrument (str): Name of Instrument Profile (required)
	    recording_base64 (str): Required. Audio as base64 webm
	    filename (str): Optional filename
	Returns:
	    dict: { "name": <Intonation Session name> }
	"""
	user = frappe.session.user
	roles = frappe.get_roles(user)
	if "Technician" not in roles and "Lab" not in roles:
		frappe.throw(_("Only Technicians can record intonation."), frappe.PermissionError)

	if not instrument:
		raise LabAPIError(_("Instrument is required."))
	if not recording_base64 or len(recording_base64) < 100:
		raise LabAPIError(_("Recording missing or too short."))

	try:
		# Attach file
		file_doc = None
		if filename:
			file_doc = _attach_file(
				parent_doc=frappe.get_doc("Instrument Profile", instrument),
				b64=recording_base64,
				fname=filename,
			)

		session = frappe.new_doc("Intonation Session")
		session.instrument = instrument
		if file_doc:
			session.file = file_doc.file_url
		session.owner = user
		session.insert(ignore_permissions=True)
		frappe.db.commit()

		frappe.logger().info(f"Intonation session saved by {user} for {instrument} ({session.name})")
		return {"name": session.name}
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Lab API: Save Intonation Session Error")
		raise LabAPIError(_("Failed to save intonation session."))


@frappe.whitelist(allow_guest=False, methods=["POST"])
def save_tone_fitness(instrument=None, recording_base64=None, filename=None):
	"""
	Analyze and save tone fitness from audio, with spectral features.
	Args:
	    instrument (str): Name of Instrument Profile (required)
	    recording_base64 (str): Required. Audio as base64 webm/wav
	    filename (str): Optional filename
	Returns:
	    dict: { "name": <Tone Fitness name> }
	"""
	if not instrument:
		raise LabAPIError(_("Instrument is required."))
	if not recording_base64:
		raise LabAPIError(_("No recording provided."))

	try:
		import io

		import librosa
		import numpy as np
		import soundfile as sf

		# Decode and load audio
		y, sr = sf.read(io.BytesIO(base64.b64decode(recording_base64)))
		centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
		bandwidth = float(np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr)))

		doc = frappe.new_doc("Tone Fitness")
		doc.instrument = instrument
		doc.json_data = frappe.as_json({"centroid": centroid, "spread": bandwidth})
		doc.entries = [{"reading_time": now_datetime(), "centroid": centroid, "spread": bandwidth}]
		doc.insert(ignore_permissions=True)

		if filename:
			_attach_file(doc, recording_base64, filename)

		return {"name": doc.name}
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Lab API: Tone Fitness Error")
		raise LabAPIError(_("Error processing tone fitness."))


@frappe.whitelist(allow_guest=False, methods=["POST"])
def save_leak_test(instrument=None, recording_base64=None, filename=None):
	"""
	Mock leak detection – creates dummy scores for tone holes.
	Args:
	    instrument (str): Name of Instrument Profile (required)
	    recording_base64 (str): Optional audio
	    filename (str): Optional filename
	Returns:
	    dict: { "name": <Leak Test name> }
	"""
	if not instrument:
		raise LabAPIError(_("Instrument is required."))

	try:
		doc = frappe.new_doc("Leak Test")
		doc.instrument = instrument
		doc.json_data = frappe.as_json({"algorithm": "mock", "holes": 3})
		doc.readings = [
			{
				"tone_hole": f"Hole {i+1}",
				"leak_score": round(0.1 * (i + 1), 2),
				"time_logged": now_datetime(),
			}
			for i in range(3)
		]
		doc.insert(ignore_permissions=True)

		if recording_base64 and filename:
			_attach_file(doc, recording_base64, filename)

		return {"name": doc.name}
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Lab API: Leak Test Error")
		raise LabAPIError(_("Error saving leak test."))
