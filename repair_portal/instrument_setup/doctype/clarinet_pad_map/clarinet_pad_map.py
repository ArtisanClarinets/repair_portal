# File Header Template
# Relative Path: repair_portal/instrument_setup/doctype/clarinet_pad_map/clarinet_pad_map.py
# Last Updated: 2025-08-09
# Version: v2.3
# Purpose: Auto-populates pad layout template for French-style soprano clarinets (B♭, A, C, D, E♭)
#          and Bass Clarinets (Low E♭, Low C, Low D w/ removable extension); exposes method for client trigger;
#          enforces is_open_key for specific pad positions without overriding explicit user choices.
# Dependencies: Clarinet Pad Entry, Instrument Model, Instrument Category

from __future__ import annotations

import re
import frappe
from frappe.model.document import Document
from typing import Optional, Tuple, Dict, Any

# --- Soprano (French-style) ---
STANDARD_SOPRANO_TYPES = {"B♭", "A", "C", "D", "E♭"}

STANDARD_PAD_NAMES_TOP = [
    "Register Key",
    "C Trill Key",
    "B♭ Trill Key",
    "F# Trill Key",
    "B♭/E♭ Trill Key",
    "A Key",
    "G#/Ab Key",
    "E/B Ring (LH 1)",
    "D/A Ring (LH 2)",
    "Inline B♭/E♭ Key",
    "C#/G# Key",
]

STANDARD_PAD_NAMES_BOTTOM = [
    "3 Ring Key",
    "Inline F#/B Key",
    "A♭/E♭ Pinky Key",
    "F#/C# Pinky Key",
    "F/C Pinky Key",
    "E/B Pinky Key",
    "E♭/B♭ Pinky Key (optional)",
]

# Pads that must be flagged as "open" (is_open_key = 1) on SOPRANO
OPEN_KEY_POSITIONS_SOPRANO = {
    "E/B Ring (LH 1)",
    "D/A Ring (LH 2)",
    "3 Ring Key",
    "F/C Pinky Key",
    "E/B Pinky Key",
    "E♭/B♭ Pinky Key (optional)",
}

# --- Bass Clarinet helpers ---
def _normalize_title(s: Optional[str]) -> str:
    if not s:
        return ""
    s = s.lower()
    s = s.replace("—", "-").replace("–", "-")
    s = re.sub(r"[^\w\s/#\-\(\)♭♯]+", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = s.replace("e♭", "eb").replace("d♭", "db").replace("c♯", "c#").replace("f♯", "f#")
    return s

BASS_VARIANTS = {
    "low_eb": {
        "aliases": {
            "bass clarinet - low eb",
            "bass clarinet (low eb)",
            "bass clarinet low eb",
            "bass clarinet short",
            "bass clarinet (short, low eb)",
            "bass clarinet - low e♭",
            "bass - low eb",
            "Bass — Low E♭"
        }
    },
    "low_c": {
        "aliases": {
            "bass clarinet - low c",
            "bass clarinet (low c)",
            "bass clarinet low c",
            "bass clarinet extended",
            "bass clarinet (extended, low c)",
            "bass - low c",
            "Bass — Low C"
        }
    },
    "low_d_extension": {
        "aliases": {
            "bass clarinet - low d ext",
            "bass clarinet (low d extension)",
            "bass clarinet low d extension",
            "bass clarinet - low d w/ extension",
            "bass clarinet - low d with extension",
            "bass clarinet (removable low d)",
            "bass clarinet - low d",
            "bass - low d",
            "bass - low d ext",
            "Bass — Low D"
        }
    },
}
# normalize alias strings once
for v in BASS_VARIANTS.values():
    v["aliases"] = {_normalize_title(x) for x in v["aliases"]}

# Common bass top joint keys (plateau + side keys)
BASS_PAD_NAMES_TOP_COMMON = [
    "Body Register Key",
    "Neck Register Vent",
    "C Trill Key",
    "B♭ Trill Key",
    "F# Trill Key",
    "B♭/E♭ Trill Key",
    "A Key",
    "G#/Ab Key",
    "LH 1 Plateau (E/B)",
    "LH 2 Plateau (D/A)",
    "LH 3 Plateau (C/G)",
    "Fork B♭ (Side) Key",
]

# Common bass bottom joint keys (right-hand plateau + lower stack & pinky cluster)
BASS_PAD_NAMES_BOTTOM_COMMON = [
    "RH 1 Plateau (E/B)",
    "RH 2 Plateau (D/A)",
    "RH 3 Plateau (C/G)",
    "F/C Key",
    "E/B Key",
    "F#/C# Key",
    "E♭/B♭ Key",
    "Low E Key",
    "Low E♭ Key",
]

# Variant-specific extra low-note mechanisms
BASS_EXTRA_LOW_D = [
    "Low D Key",
    "D Extension Latch",
]

BASS_EXTRA_LOW_C = [
    "Low D Key",
    "Low C# Key",
    "Low C Key",
    "Low C Lever",
    "Low C# Lever",
]

# Pads that should be treated as "open" on BASS (tone-hole/ring equivalents)
OPEN_KEY_POSITIONS_BASS = {
    "RH 1 Plateau (E/B)",
    "RH 2 Plateau (D/A)",
    "RH 3 Plateau (C/G)",
}

class ClarinetPadMap(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from frappe.types import DF
        from repair_portal.instrument_setup.doctype.clarinet_pad_entry.clarinet_pad_entry import (
            ClarinetPadEntry,
        )
        bottom_joint_pads: DF.Table[ClarinetPadEntry]
        clarinet_model: DF.Link | None
        instrument_category: DF.Link | None
        pad_map_title: DF.Data | None
        top_joint_pads: DF.Table[ClarinetPadEntry]
    # end: auto-generated types

    """
    Represents the pad layout template for a given clarinet model, including top and bottom joint pads.
    Supports modern French-style soprano clarinets (B♭, A, C, D, E♭) and Bass Clarinets
    (Low E♭, Low C, Low D w/ removable extension).
    Enforces is_open_key = 1 for selected pad positions without overriding explicit user choices.
    """

    # ----- Lifecycle hooks -----
    def validate(self):
        family, variant = self._detect_family_variant()

        # Auto-populate only if both tables are empty and family is recognized.
        if family and not self.top_joint_pads and not self.bottom_joint_pads:
            if family == "soprano":
                self._populate_soprano()
            elif family == "bass":
                self._populate_bass(variant)

        # Always enforce open-key defaults without clobbering user edits.
        self._enforce_open_key_flags(family=family)

    # ----- Detection -----
    def _get_category_title_from_links(self) -> Optional[str]:
        """
        Resolve the category title using either:
          - instrument_category (Link to Instrument Category), or
          - clarinet_model/instrument_model -> Instrument Category -> title
        Returns title (string) or None.
        """
        # direct link present on this DocType?
        if getattr(self, "instrument_category", None):
            cat = self.instrument_category
            title = frappe.db.get_value("Instrument Category", cat, "title")
            if isinstance(title, str):
                return title
            elif title is not None:
                return str(title)
            else:
                return None

        # else try via model link (instrument_model or clarinet_model)
        model = getattr(self, "instrument_model", None) or getattr(self, "clarinet_model", None)
        if model:
            category = frappe.db.get_value("Instrument Model", model, "instrument_category")
            if category:
                title = frappe.db.get_value("Instrument Category", category, "title")
                if isinstance(title, str):
                    return title
                elif title is not None:
                    return str(title)
                else:
                    return None
        return None

    def get_clarinet_type(self) -> Optional[str]:
        """Backward-compatible helper (kept for any external callers)."""
        return self._get_category_title_from_links()

    def _detect_family_variant(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Determine whether the linked Instrument Category corresponds to a soprano or bass,
        and for bass, which low-note variant (low_eb, low_c, low_d_extension).

        Returns: (family, variant)
          family ∈ {"soprano","bass",None}
          variant ∈ {"low_eb","low_c","low_d_extension",None}
        """
        title = self._get_category_title_from_links()
        if not title:
            return None, None

        # Exact soprano match uses original labels
        if title in STANDARD_SOPRANO_TYPES:
            return "soprano", None

        norm = _normalize_title(title)

        # Bass aliases
        for variant, data in BASS_VARIANTS.items():
            if norm in data["aliases"]:
                return "bass", variant

        # Heuristic: contains "bass clarinet" → pick variant by token
        if "bass clarinet" in norm or norm.startswith("bass - "):
            if "low c" in norm:
                return "bass", "low_c"
            if "low d" in norm:
                return "bass", "low_d_extension"
            return "bass", "low_eb"

        # Unknown
        return None, None

    # ----- Population -----
    def _populate_soprano(self):
        for name in STANDARD_PAD_NAMES_TOP:
            self.append(
                "top_joint_pads",
                {"pad_position": name, "is_open_key": 1 if name in OPEN_KEY_POSITIONS_SOPRANO else 0},
            )
        for name in STANDARD_PAD_NAMES_BOTTOM:
            self.append(
                "bottom_joint_pads",
                {"pad_position": name, "is_open_key": 1 if name in OPEN_KEY_POSITIONS_SOPRANO else 0},
            )

    def _populate_bass(self, variant: Optional[str]):
        # Always include common sets first
        for name in BASS_PAD_NAMES_TOP_COMMON:
            self.append(
                "top_joint_pads",
                {"pad_position": name, "is_open_key": 1 if name in OPEN_KEY_POSITIONS_BASS else 0},
            )

        bottom = list(BASS_PAD_NAMES_BOTTOM_COMMON)

        # Variant-specific additions
        if variant == "low_c":
            bottom += BASS_EXTRA_LOW_C
        elif variant == "low_d_extension":
            bottom += BASS_EXTRA_LOW_D
        # else low_eb → no extras beyond common

        for name in bottom:
            self.append(
                "bottom_joint_pads",
                {"pad_position": name, "is_open_key": 1 if name in OPEN_KEY_POSITIONS_BASS else 0},
            )

    # ----- Enforcement (non-destructive) -----
    def _enforce_open_key_flags(self, family: Optional[str]):
        """
        Set a default is_open_key only when the field is unset.
        - If pad_position is in OPEN set and is_open_key is unset -> set to 1
        - If pad_position is not in OPEN set and is_open_key is unset -> set to 0
        - If user already set 0 or 1 -> DO NOT change it
        """
        open_set = (
            OPEN_KEY_POSITIONS_SOPRANO if family == "soprano" else
            OPEN_KEY_POSITIONS_BASS if family == "bass" else
            OPEN_KEY_POSITIONS_SOPRANO
        )

        def _normalize(v):
            if v is None:
                return None
            if isinstance(v, str) and v.strip() == "":
                return None
            return v

        def _apply(rows):
            for row in (rows or []):
                if not getattr(row, "pad_position", None):
                    continue
                current = _normalize(getattr(row, "is_open_key", None))
                if current is None:
                    row.is_open_key = 1 if row.pad_position in open_set else 0
                else:
                    try:
                        row.is_open_key = int(current)
                    except Exception:
                        pass

        _apply(self.top_joint_pads)
        _apply(self.bottom_joint_pads)


# --- Whitelisted: supports saved and unsaved docs ---
@frappe.whitelist(allow_guest=False)
def populate_standard_pad_names(docname: Optional[str] = None, doc_json: Optional[Any] = None):
    """
    Populate pads for a Clarinet Pad Map.

    Use either:
      - docname: saved Document name → populate + save, returns True
      - doc_json: full Document dict (unsaved) → populate in-memory, returns rows (no save)
    """
    def _populate_and_enforce(_doc: ClarinetPadMap):
        family, variant = _doc._detect_family_variant()
        if not _doc.top_joint_pads and not _doc.bottom_joint_pads:
            if family == "soprano":
                _doc._populate_soprano()
            elif family == "bass":
                _doc._populate_bass(variant)
        _doc._enforce_open_key_flags(family=family)

    # Saved document path
    if docname:
        doc = frappe.get_doc("Clarinet Pad Map", docname)  # raises DoesNotExist if wrong
        _populate_and_enforce(doc)
        doc.save()
        return True

    # Unsaved document path
    if doc_json:
        if isinstance(doc_json, str):
            # JS may stringify args; parse safely
            try:
                doc_json = frappe.parse_json(doc_json)
            except Exception:
                frappe.throw("Invalid doc_json payload.")
        if not isinstance(doc_json, dict):
            frappe.throw("doc_json must be a dict or JSON string.")

        # Rehydrate as a Document but DO NOT save
        temp_doc = frappe.get_doc(doc_json)
        _populate_and_enforce(temp_doc)

        # Return rows so client can patch the UI without reload/save
        return {
            "top_joint_pads": [r.as_dict() for r in (temp_doc.top_joint_pads or [])],
            "bottom_joint_pads": [r.as_dict() for r in (temp_doc.bottom_joint_pads or [])],
        }

    frappe.throw("Provide either 'docname' (saved doc) or 'doc_json' (unsaved doc).")