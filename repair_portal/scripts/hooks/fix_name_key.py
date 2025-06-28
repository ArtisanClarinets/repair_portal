#!/usr/bin/env python3
"""
Script to format 'name' keys in any JSON file that contains a "doctype" key.

Usage (from your bench root):
  bench --site <your-site> execute repair_portal.scripts.fix_all_doctypes.run
"""

import json
import shutil
import logging
from pathlib import Path

import frappe

# ─── Logging setup ──────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# ─── Helpers ────────────────────────────────────────────────────────────────────
def backup(path: Path):
    bak = path.with_suffix(path.suffix + ".bak")
    shutil.copy2(path, bak)
    logger.debug(f"backed up: {path} → {bak}")

def format_name(name: str) -> str:
    """
    Convert "initial_state" → "Initial State"
    """
    return name.replace("_", " ").title()

# ─── Core traversal & processing ───────────────────────────────────────────────
def run(dry_run: bool = False):
    logger.info("🔄 scanning for JSON files with 'doctype' key…")

    app_root = Path(frappe.get_app_path("repair_portal"))

    fixed = skipped = errors = 0

    # Traverse all JSON files in the app directory
    for json_file in app_root.glob("**/*.json"):
        try:
            # Load the content of the JSON file
            content = json.loads(json_file.read_text())
        except Exception as e:
            logger.error(f"❌ invalid JSON in {json_file}: {e}")
            errors += 1
            continue
        
        # Check if "doctype" exists in the JSON
        if "doctype" in content:
            # Check if the "name" key exists and format it
            if "name" in content:
                original_name = content["name"]
                formatted_name = format_name(original_name)
                if original_name != formatted_name:
                    content["name"] = formatted_name
                    logger.info(f"✅ formatted 'name' in {json_file}: {original_name} → {formatted_name}")
                    if not dry_run:
                        backup(json_file)
                        json_file.write_text(json.dumps(content, indent=4) + "\n")
                    fixed += 1
                else:
                    skipped += 1
            else:
                skipped += 1
        else:
            skipped += 1

    logger.info(f"done: {fixed} fixed, {skipped} unchanged, {errors} errors.")

if __name__ == "__main__":
    # To preview only: run(dry_run=True)
    run()
