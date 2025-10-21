"""
File: repair_portal/utils/install/install_consent_artifacts.py
Version: v1.4.2 (2025-09-16)

Purpose (idempotent, data-safe):
- Upsert Workflow Action masters (handles both "Workflow Action" and legacy "Workflow Action Master").
- Upsert Workflow States (correct field: doc_status) with styles.
- Create/merge the "Consent Form Workflow" without deleting existing custom states/transitions/roles.
- Ensure the "Consent Settings" singleton exists; seed default variable mappings if absent.
- Optionally apply linked sources via Consent Settings' method if present.

Key fixes in v1.4.2:
- Robust normalization for role containers ("allow_edit" on states, "allowed" on transitions):
  supports child-rows, dicts, strings, or newline-separated strings. No more `.get()` on `str`.
- Extra meta-guards and type checks to satisfy Pylance and avoid edge-case crashes.
"""

from __future__ import annotations

from typing import Any

import frappe

WF_NAME = "Consent Form Workflow"
DT_CONSENT_FORM = "Consent Form"

# Preferred roles; we'll keep only those that exist on the site
PREFERRED_ROLES = ["System Manager", "Sales User"]


# ----------------------------
# Utilities
# ----------------------------


def _site_log(msg: str) -> None:
    try:
        frappe.logger("repair_portal.install").info(msg)
    except Exception:
        pass


def _existing_roles(candidates: list[str]) -> list[str]:
    present = [r for r in candidates if frappe.db.exists("Role", r)]
    if not present and frappe.db.exists("Role", "System Manager"):
        present = ["System Manager"]
    return present


def _get_action_link_target_dt() -> str:
    """
    Returns the DocType that the Workflow Transition 'action' field links to.
    Typically 'Workflow Action' on v15, but some sites still use 'Workflow Action Master'.
    """
    meta_tr = frappe.get_meta("Workflow Transition")
    f = meta_tr.get_field("action")
    if f and getattr(f, "options", None):
        return str(f.options)
    return "Workflow Action"


def _ensure_singleton_exists(doctype: str) -> None:
    """
    If a singleton DocType exists but its singleton row hasn’t been created yet,
    calling frappe.get_single throws DoesNotExistError. Create it safely.
    """
    if not frappe.db.exists("DocType", doctype):
        frappe.throw(f"Required DocType '{doctype}' is not installed.")
    try:
        frappe.get_single(doctype)  # will throw if missing
    except frappe.DoesNotExistError:
        doc = frappe.new_doc(doctype)
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        _site_log(f"Created singleton for {doctype}.")


def _safe_set(doc: Any, fieldname: str, value: Any) -> bool:
    """Meta-guarded set that only assigns when the field exists and value differs."""
    meta = frappe.get_meta(doc.doctype)
    if meta.has_field(fieldname) and doc.get(fieldname) != value:
        doc.set(fieldname, value)
        return True
    return False


# ----------------------------
# Upsert: Workflow Actions
# ----------------------------


def _upsert_workflow_actions() -> dict[str, str]:
    """
    Ensure the required actions exist in whichever DocType the transitions link to.
    Returns a mapping of friendly action label -> actual link name to use.
    """
    actions_needed = [
        "Request Signature",
        "Submit (Requires Signature)",
        "Cancel",
    ]

    target_dt = _get_action_link_target_dt()
    target_meta = frappe.get_meta(target_dt)

    # Candidate label fields
    nameish_fields = [
        "workflow_action_name",  # Workflow Action (v15)
        "action",  # legacy variants
        "action_name",
        "title",
        "name",  # fallback
    ]
    usable_label_field: str | None = None
    for f in nameish_fields:
        if target_meta.has_field(f):
            usable_label_field = f
            break

    link_names: dict[str, str] = {}

    for label in actions_needed:
        # Prefer a direct name match
        if frappe.db.exists(target_dt, label):
            link_names[label] = label
            continue

        # Otherwise search by label field to avoid duplicates
        existing_name: str | None = None
        if usable_label_field and usable_label_field != "name":
            # Normalize any possible return shape from frappe.db.get_value
            raw = frappe.db.get_value(target_dt, {usable_label_field: label}, "name")

            # Possible shapes:
            # - dict (e.g. {"name": "DocName"})
            # - list/tuple (e.g. ["DocName"]) when multiple fields requested
            # - scalar (str/int) when single field requested
            # - None when not found
            if isinstance(raw, dict):
                existing_name = raw.get("name")  # type: ignore[arg-type]
            elif isinstance(raw, (list, tuple)):
                existing_name = str(raw[0]) if raw else None
            elif raw is None:
                existing_name = None
            else:
                # scalar (string/int); coerce to str for safety
                existing_name = str(raw)

        if existing_name:
            link_names[label] = str(existing_name)
            continue

        # Create
        data: dict[str, Any] = {"doctype": target_dt}
        if usable_label_field:
            data[usable_label_field] = label
        action_doc = frappe.get_doc(data).insert(ignore_permissions=True)
        frappe.db.commit()
        link_names[label] = str(action_doc.name)

    _site_log(f"Workflow actions ensured in '{target_dt}': {link_names}")
    return link_names


# ----------------------------
# Upsert: Workflow States (masters)
# ----------------------------


def _upsert_workflow_states() -> None:
    """
    Ensure the Workflow State master rows exist and have correct doc_status/style.
    IMPORTANT: Field is 'doc_status' (int 0/1/2). Do NOT use Document.docstatus.
    """
    desired = [
        # (name,              doc_status, style)
        ("Draft", 0, "Primary"),
        ("Pending Signature", 0, "Warning"),
        ("Signed", 1, "Success"),
        ("Cancelled", 2, "Danger"),
    ]

    ws_meta = frappe.get_meta("Workflow State")
    has_state_alias = ws_meta.has_field("state")  # some variants mirror name into 'state'
    has_ws_name = ws_meta.has_field("workflow_state_name")

    for name, doc_status, style in desired:
        if frappe.db.exists("Workflow State", name):
            ws = frappe.get_doc("Workflow State", name)
            changed = False

            if ws.get("doc_status") != doc_status:
                ws.set("doc_status", doc_status)
                changed = True

            if ws.get("style") != style:
                ws.set("style", style)
                changed = True

            if has_ws_name and ws.get("workflow_state_name") != name:
                ws.set("workflow_state_name", name)
                changed = True
            if has_state_alias and ws.get("state") != name:
                ws.set("state", name)
                changed = True

            if changed:
                ws.save(ignore_permissions=True)
        else:
            data: dict[str, Any] = {
                "doctype": "Workflow State",
                "doc_status": doc_status,
                "style": style,
            }
            if has_ws_name:
                data["workflow_state_name"] = name
            if has_state_alias:
                data["state"] = name

            ws = frappe.get_doc(data).insert(ignore_permissions=True)
            # Try to align name with label (non-fatal if rename is blocked)
            old_name = str(ws.name or "")
            if old_name and old_name != name:
                try:
                    frappe.rename_doc("Workflow State", old_name, name, force=True)
                except Exception:
                    pass

        frappe.db.commit()

    _site_log("Workflow States upserted.")


# ----------------------------
# Merge helpers for existing Workflow doc
# ----------------------------


def _find_state_row(wf: Any, state_name: str) -> Any | None:
    for row in wf.get("states") or []:
        if (row.get("state") or "") == state_name:
            return row
    return None


def _normalize_role_names(container_value: Any) -> set[str]:
    """
    Accepts:
      - list of child docs (with .get('role'))
      - list of dicts
      - list of strings
      - newline-separated string
      - None
    Returns a set of role names (strings).
    """
    roles: set[str] = set()
    if container_value is None:
        return roles

    # newline-separated string?
    if isinstance(container_value, str):
        for part in container_value.splitlines():
            p = part.strip()
            if p:
                roles.add(p)
        return roles

    # list-like?
    if isinstance(container_value, list):
        for it in container_value:
            if hasattr(it, "get") or isinstance(it, dict):  # child doc
                val = it.get("role")
                if isinstance(val, str) and val.strip():
                    roles.add(val.strip())
            elif isinstance(it, str):
                s = it.strip()
                if s:
                    roles.add(s)
        return roles

    return roles


def _ensure_roles_on_row(row: Any, child_field: str, roles_to_add: list[str]) -> bool:
    """
    Adds roles to either a child table ('Table' / 'Table MultiSelect') or a MultiSelect-like field.
    Returns True if any role was added.
    """
    meta = frappe.get_meta(row.doctype)
    fd = meta.get_field(child_field)
    if not fd:
        return False

    ft = str(fd.fieldtype or "")

    # Current values in a normalized set
    existing_roles = _normalize_role_names(row.get(child_field))

    added = False

    if ft in ("Table", "Table MultiSelect", "Table Multiselect"):
        for role in roles_to_add:
            if role and role not in existing_roles:
                row.append(child_field, {"role": role})
                existing_roles.add(role)
                added = True
        return added

    # Fallback for MultiSelect-like text storage (newline-separated)
    if ft in ("MultiSelect", "Small Text", "Text", "Data"):
        # Merge and write back as newline-separated
        for role in roles_to_add:
            if role and role not in existing_roles:
                existing_roles.add(role)
                added = True
        if added:
            row.set(child_field, "\n".join(sorted(existing_roles)))
        return added

    # Unknown type => do nothing
    return False


def _find_transition_row(wf: Any, state: str, action: str, next_state: str) -> Any | None:
    for tr in wf.get("transitions") or []:
        if tr.get("state") == state and tr.get("action") == action and tr.get("next_state") == next_state:
            return tr
    return None


# ----------------------------
# Upsert: Workflow definition (merge, don’t clobber)
# ----------------------------


def _upsert_workflow(link_actions: dict[str, str]) -> None:
    # Ensure target Document Type exists
    if not frappe.db.exists("DocType", DT_CONSENT_FORM):
        frappe.throw(
            f"Target DocType '{DT_CONSENT_FORM}' is not installed. "
            "Install/enable it before installing the workflow."
        )

    # Ensure state masters first
    _upsert_workflow_states()

    roles_draft = _existing_roles(PREFERRED_ROLES)
    roles_pending = _existing_roles(PREFERRED_ROLES)
    roles_signed = _existing_roles(["System Manager"])
    roles_cancelled = _existing_roles(["System Manager"])

    # Resolve action link names (safe even if docname != label)
    action_request = link_actions["Request Signature"]
    action_submit = link_actions["Submit (Requires Signature)"]
    action_cancel = link_actions["Cancel"]

    # Load or create workflow skeleton
    if frappe.db.exists("Workflow", WF_NAME):
        wf = frappe.get_doc("Workflow", WF_NAME)
        created = False
    else:
        wf = frappe.new_doc("Workflow")
        created = True

    # Set core fields (meta-guarded)
    changed = False
    changed |= _safe_set(wf, "workflow_name", WF_NAME)
    changed |= _safe_set(wf, "document_type", DT_CONSENT_FORM)
    changed |= _safe_set(wf, "workflow_state_field", "workflow_state")
    changed |= _safe_set(wf, "is_active", 1)
    changed |= _safe_set(wf, "send_email_alert", 0)
    changed |= _safe_set(wf, "override_status", 0)

    # --- States (merge/update, no deletes) ---
    def _ensure_state(state_name: str, doc_status: int, style: str, roles: list[str]) -> None:
        nonlocal changed
        st = _find_state_row(wf, state_name)
        if not st:
            # Prepare initial allow_edit value depending on the child-field type
            roles_to_seed = list(roles) if roles else []
            if not roles_to_seed:
                roles_to_seed = ["System Manager"]

            # Determine child doctype for 'states' table on Workflow
            wf_meta = frappe.get_meta("Workflow")
            states_field = wf_meta.get_field("states")
            child_doctype = getattr(states_field, "options", None) if states_field else None

            allow_edit_value = None
            if child_doctype:
                child_meta = frappe.get_meta(child_doctype)
                child_fd = child_meta.get_field("allow_edit")
                if child_fd:
                    ft = str(child_fd.fieldtype or "")
                    if ft in ("Table", "Table MultiSelect", "Table Multiselect"):
                        allow_edit_value = [{"role": r} for r in roles_to_seed]
                    elif ft in ("MultiSelect", "Small Text", "Text", "Data"):
                        allow_edit_value = "\n".join(sorted(set(roles_to_seed)))
                    elif ft == "Link":
                        # Single-link to Role: pick first existing role as scalar
                        allow_edit_value = str(roles_to_seed[0])

            # Fallback: if unknown, use table-like rows
            if allow_edit_value is None:
                allow_edit_value = [{"role": r} for r in roles_to_seed]

            st = wf.append(
                "states",
                {
                    "state": state_name,
                    "doc_status": doc_status,
                    "style": style,
                    "allow_edit": allow_edit_value,
                },
            )
            changed = True
        else:
            # Update if drifted
            if st.get("doc_status") != doc_status:
                st.set("doc_status", doc_status)
                changed = True
            if st.get("style") != style:
                st.set("style", style)
                changed = True

        if _ensure_roles_on_row(st, "allow_edit", roles):
            changed = True

    _ensure_state("Draft", 0, "Primary", roles_draft)
    _ensure_state("Pending Signature", 0, "Warning", roles_pending)
    _ensure_state("Signed", 1, "Success", roles_signed)
    _ensure_state("Cancelled", 2, "Danger", roles_cancelled)

    # --- Transitions (merge/update, no deletes) ---
    meta_tr = frappe.get_meta("Workflow Transition")
    has_condition_field = meta_tr.has_field("condition")

    def _ensure_transition(
        state: str,
        action_name: str,
        next_state: str,
        allow_self_approval: int = 1,
        condition: str | None = None,
        roles: list[str] | None = None,
    ) -> None:
        nonlocal changed
        tr = _find_transition_row(wf, state, action_name, next_state)
        if not tr:
            data: dict[str, Any] = {
                "state": state,
                "action": action_name,
                "next_state": next_state,
                "allow_self_approval": allow_self_approval,
            }
            if has_condition_field and condition:
                data["condition"] = condition
            # Prepare initial allowed value depending on child field type for transitions
            roles_to_seed = list(roles or [])
            if not roles_to_seed:
                roles_to_seed = ["System Manager"]

            # Determine child doctype for 'transitions' table on Workflow
            trans_field = (
                wf_meta.get_field("transitions") if (wf_meta := frappe.get_meta("Workflow")) else None
            )
            trans_child_doctype = getattr(trans_field, "options", None) if trans_field else None

            allowed_value = None
            if trans_child_doctype:
                tr_child_meta = frappe.get_meta(trans_child_doctype)
                tr_child_fd = tr_child_meta.get_field("allowed")
                if tr_child_fd:
                    ft = str(tr_child_fd.fieldtype or "")
                    if ft in ("Table", "Table MultiSelect", "Table Multiselect"):
                        allowed_value = [{"role": r} for r in roles_to_seed]
                    elif ft in ("MultiSelect", "Small Text", "Text", "Data"):
                        allowed_value = "\n".join(sorted(set(roles_to_seed)))
                    elif ft == "Link":
                        allowed_value = str(roles_to_seed[0])

            if allowed_value is None:
                allowed_value = [{"role": r} for r in roles_to_seed]

            data["allowed"] = allowed_value

            tr = wf.append("transitions", data)
            changed = True
        else:
            # Update if drifted
            if tr.get("allow_self_approval") != allow_self_approval:
                tr.set("allow_self_approval", allow_self_approval)
                changed = True
            if has_condition_field:
                current_cond = tr.get("condition") or ""
                desired_cond = condition or ""
                if current_cond != desired_cond:
                    tr.set("condition", desired_cond)
                    changed = True

        if roles:
            if _ensure_roles_on_row(tr, "allowed", roles):
                changed = True

    _ensure_transition(
        state="Draft",
        action_name=action_request,
        next_state="Pending Signature",
        allow_self_approval=1,
        condition=None,
        roles=roles_draft,
    )

    _ensure_transition(
        state="Pending Signature",
        action_name=action_submit,
        next_state="Signed",
        allow_self_approval=1,
        condition="doc.signature",  # requires signature field set/truthy
        roles=roles_pending,
    )

    _ensure_transition(
        state="Signed",
        action_name=action_cancel,
        next_state="Cancelled",
        allow_self_approval=1,
        condition=None,
        roles=roles_signed,
    )

    # Save workflow.
    # Insert allowing missing mandatory child rows first (some sites require staged population).
    if created:
        # Insert while skipping mandatory and link validations to allow staged population
        wf.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)

        # reload from DB to operate on persisted rows and avoid validation-time link checks
        try:
            wf = frappe.get_doc("Workflow", WF_NAME)
        except Exception:
            # if reload fails, at least commit and rethrow later
            frappe.db.commit()
            _site_log(f"Workflow '{WF_NAME}' inserted but reload failed; aborting safe merge.")
            raise

        # Ensure role child rows exist on persisted rows
        # States
        for state_name, roles in [
            ("Draft", roles_draft),
            ("Pending Signature", roles_pending),
            ("Signed", roles_signed),
            ("Cancelled", roles_cancelled),
        ]:
            st = _find_state_row(wf, state_name)
            if st:
                if _ensure_roles_on_row(st, "allow_edit", list(roles)):
                    changed = True

        # Transitions
        transitions_to_check = [
            ("Draft", action_request, "Pending Signature", roles_draft),
            ("Pending Signature", action_submit, "Signed", roles_pending),
            ("Signed", action_cancel, "Cancelled", roles_signed),
        ]
        for state, action_name, next_state, roles in transitions_to_check:
            tr = _find_transition_row(wf, state, action_name, next_state)
            if tr:
                if _ensure_roles_on_row(tr, "allowed", list(roles)):
                    changed = True

        if changed:
            wf.save(ignore_permissions=True)
    else:
        if changed:
            wf.save(ignore_permissions=True)

    frappe.db.commit()
    _site_log(f"Workflow '{WF_NAME}' installed/updated (changed={changed}).")


# ----------------------------
# Consent Settings defaults
# ----------------------------


def _ensure_settings_defaults() -> None:
    """
    Ensure singleton exists and seed baseline mappings without overwriting existing rows.
    """
    _ensure_singleton_exists("Consent Settings")

    settings = frappe.get_single("Consent Settings")

    desired_defaults = [
        {
            "variable_name": "customer_name",
            "source_doctype": "Customer",
            "form_link_field": "customer",
            "source_fieldname": "customer_name",
        },
        {
            "variable_name": "customer_email",
            "source_doctype": "Customer",
            "form_link_field": "customer",
            "source_fieldname": "email_id",
        },
        {
            "variable_name": "customer_phone",
            "source_doctype": "Customer",
            "form_link_field": "customer",
            "source_fieldname": "mobile_no",
        },
    ]

    existing = {m.get("variable_name", "") for m in (settings.get("mappings") or [])}

    changed = False
    for row in desired_defaults:
        if row["variable_name"] not in existing:
            settings.append(
                "mappings",
                {
                    "enabled": 1,
                    "variable_name": row["variable_name"],
                    "source_doctype": row["source_doctype"],
                    "form_link_field": row["form_link_field"],
                    "source_fieldname": row["source_fieldname"],
                    "default_value": "",
                },
            )
            changed = True

    # Enable auto fill if the field exists
    if frappe.get_meta("Consent Settings").has_field("enable_auto_fill"):
        if settings.get("enable_auto_fill") != 1:
            settings.set("enable_auto_fill", 1)
            changed = True

    if changed:
        settings.save(ignore_permissions=True)
        frappe.db.commit()
        _site_log("Consent Settings defaults ensured.")
    else:
        _site_log("Consent Settings already satisfied; no changes.")


def _apply_linked_sources_if_available() -> None:
    """
    Calls Consent Settings' apply_linked_sources() if present.
    """
    try:
        settings = frappe.get_single("Consent Settings")
        fn = getattr(settings, "apply_linked_sources", None)
        if callable(fn):
            fn()
            frappe.db.commit()
            _site_log("apply_linked_sources executed.")
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Consent installer: apply_linked_sources failed")


# ----------------------------
# Public entry point
# ----------------------------


def install_or_update_consent_artifacts() -> dict[str, str]:
    """
    Orchestrates installer in a safe sequence:
    1) Upsert actions and get actual link names.
    2) Upsert workflow states.
    3) Merge/install workflow definition using those link names.
    4) Ensure Consent Settings singleton + defaults.
    5) Apply linked sources if available.
    """
    link_actions = _upsert_workflow_actions()
    _upsert_workflow_states()
    _upsert_workflow(link_actions)
    _ensure_settings_defaults()
    _apply_linked_sources_if_available()
    return {
        "status": "ok",
        "message": "Consent workflow, actions, states, settings & links installed/updated.",
    }
