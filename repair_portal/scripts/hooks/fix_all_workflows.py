#!/usr/bin/env python3
"""
Script to validate workflows AND verify that their target DocTypes
have the proper workflow-state field in their schema.

Usage (from your bench root):
  bench --site <your-site> execute repair_portal.scripts.fix_all_workflows.run
"""

import json
import logging
import shutil
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


def clean_list_field(obj: dict, key: str) -> bool:
    if key not in obj:
        return False
    val = obj[key]
    if isinstance(val, list):
        obj[key] = "\n".join(val)
        return True
    if val is None:
        obj.pop(key)
        return True
    return False


def normalize_workflow(data: dict, wf_name: str) -> bool:
    changed = False
    for fld, want in {"doctype": "Workflow", "name": wf_name, "is_standard": 1, "sync_on_migrate": 1}.items():
        if data.get(fld) != want:
            data[fld] = want
            changed = True

    for state in data.get("states", []):
        if clean_list_field(state, "only_allow_edit_for"):
            changed = True

    for tr in data.get("transitions", []):
        if clean_list_field(tr, "allowed"):
            changed = True

    # Ensure "name" fields follow the pattern: "Initial State"
    for state in data.get("states", []):
        if "name" in state:
            state["name"] = state["name"].replace("_", " ").title()  # Capitalize and format the name

    for tr in data.get("transitions", []):
        if "name" in tr:
            tr["name"] = tr["name"].replace("_", " ").title()  # Capitalize and format the name

    return changed


def slugify(name: str) -> str:
    """
    Convert "Final QA Checklist" → "final_qa_checklist"
    """
    return name.strip().lower().replace(" ", "_")


def find_doctype_json(app_root: Path, module: str, doc_type: str) -> Path | None:
    """
    Try to locate <slug>.json under:
      1) apps/repair_portal/<module>/doctype/<slug>/<slug>.json
      2) anywhere else in the app via **/doctype/<slug>/<slug>.json
    """
    slug = slugify(doc_type)
    # 1) same module
    direct = app_root / module / "doctype" / slug / f"{slug}.json"
    if direct.exists():
        return direct

    # 2) full-app fallback
    return next(app_root.glob(f"**/doctype/{slug}/{slug}.json"), None)


def verify_doctype_schema(app_root: Path, module: str, doc_type: str, state_field: str) -> bool:
    """
    Ensure the JSON schema for this DocType declares the workflow_state field.
    """
    dt_path = find_doctype_json(app_root, module, doc_type)
    if not dt_path:
        slug = slugify(doc_type)
        logger.error(
            f"❌ DocType schema not found for '{doc_type}' "
            f"(looked for: …/{module}/doctype/{slug}/{slug}.json)"
        )
        return False

    try:
        dt_schema = json.loads(dt_path.read_text())
    except Exception as e:
        logger.error(f"❌ failed to parse {dt_path}: {e}")
        return False

    fields = {f.get("fieldname") for f in dt_schema.get("fields", [])}
    if state_field not in fields:
        logger.error(f"❌ DocType '{doc_type}' missing field '{state_field}' " f"in {dt_path}")
        return False

    logger.debug(f"✅ DocType '{doc_type}' schema OK ({state_field} present)")
    return True


# ─── Core traversal & processing ───────────────────────────────────────────────
def run(dry_run: bool = False):
    logger.info("🔄 scanning workflows…")

    app_root = Path(frappe.get_app_path("repair_portal"))

    fixed = skipped = errors = 0

    for wf_file in app_root.glob("**/workflow/*/*.json"):
        parts = wf_file.relative_to(app_root).parts
        if len(parts) != 4 or parts[1].lower() != "workflow":
            continue

        module, _, wf_name, fname = parts

        # 1) load workflow JSON
        try:
            workflow = json.loads(wf_file.read_text())
        except Exception as e:
            logger.error(f"❌ invalid JSON in {wf_file}: {e}")
            errors += 1
            continue

        # 2) ensure we have a document_type
        doc_type = workflow.get("document_type")
        if not doc_type:
            logger.error(f"❌ workflow '{wf_name}' missing 'document_type' key")
            errors += 1
            continue

        state_field = workflow.get("workflow_state_field", "workflow_state")

        # 3) verify DocType schema exists & has state field
        if not verify_doctype_schema(app_root, module, doc_type, state_field):
            errors += 1
            continue

        # 4) normalize & write back if needed
        if normalize_workflow(workflow, wf_name):
            if dry_run:
                logger.info(f"[dry-run] would fix: {module}/workflow/{wf_name}/{fname}")
            else:
                backup(wf_file)
                wf_file.write_text(json.dumps(workflow, indent=4) + "\n")
                logger.info(f"✅ fixed workflow: {module}/workflow/{wf_name}/{fname}")
            fixed += 1
        else:
            skipped += 1

    logger.info(f"done: {fixed} fixed, {skipped} unchanged, {errors} errors.")


if __name__ == "__main__":
    # To preview only: run(dry_run=True)
    run()
