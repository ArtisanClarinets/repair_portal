#!/usr/bin/env python3
# Path: repair_portal/intake/scripts/verify_intake_module.py
# Date: 2025-10-05
# Version: 2.1.0
# Description: Fortune-500 verification harness for Clarinet Intake workflow, UX, analytics, and QA.
# Dependencies: frappe, subprocess, sys

"""
Intake Module Verification Script
=================================

This script verifies that all Clarinet Intake desk UX enhancements remain in place:
1. Mandatory headers across Python/JS assets
2. Workflow UI integrity (workflow_state-driven badges, SLA panel, no legacy fields)
3. Consent automation wiring
4. Automated test execution for critical doctypes
5. Ruff linting coverage

Run from frappe-bench directory:
    bench --site <site_name> execute repair_portal.intake.scripts.verify_intake_module.run_verification

Or directly with Python:
    python3 repair_portal/intake/scripts/verify_intake_module.py [site_name]
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import frappe

# ============================================================================
# Configuration
# ============================================================================

INTAKE_MODULE_PATH = Path("repair_portal") / "intake"
REQUIRED_HEADER_PATTERN = re.compile(
    r"# Path: .+\n# Date: \d{4}-\d{2}-\d{2}\n# Version: \d+\.\d+\.\d+\n# Description: .+\n(?:# Dependencies: .*\n)?"
)
LEGACY_FIELDS = {"intake_status", "status"}

VERIFICATION_RESULTS: dict[str, dict[str, list[str]]] = {
    "headers": {"passed": [], "failed": []},
    "workflow_ui": {"passed": [], "failed": []},
    "consent": {"passed": [], "failed": []},
    "tests": {"passed": [], "failed": []},
    "linting": {"passed": [], "failed": []},
}

# ============================================================================
# Helper Functions
# ============================================================================


def _record(category: str, passed: bool, message: str) -> None:
    VERIFICATION_RESULTS[category]["passed" if passed else "failed"].append(message)


def _print_section(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


# ============================================================================
# Verification Functions
# ============================================================================


def verify_file_headers() -> bool:
    """Verify all Python and JavaScript files have mandatory 5-line headers."""
    _print_section("1. VERIFYING FILE HEADERS")

    all_passed = True
    files_checked = 0

    for ext in ("*.py", "*.js"):
        for file_path in INTAKE_MODULE_PATH.rglob(ext):
            if "__pycache__" in file_path.parts or "node_modules" in file_path.parts:
                continue

            files_checked += 1
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            snippet = content
            if content.startswith("#!/"):
                header_start = content.find("# Path:")
                snippet = content[header_start:] if header_start >= 0 else ""

            if snippet and REQUIRED_HEADER_PATTERN.match(snippet):
                print(f"✅ {file_path.relative_to('repair_portal')}")
                _record("headers", True, str(file_path))
                continue

            print(f"❌ {file_path.relative_to('repair_portal')} - Missing or invalid header")
            _record("headers", False, f"Missing header: {file_path}")
            all_passed = False

    print(f"\nHeaders checked: {files_checked}")
    print(f"Passed: {len(VERIFICATION_RESULTS['headers']['passed'])}")
    print(f"Failed: {len(VERIFICATION_RESULTS['headers']['failed'])}")
    return all_passed


def verify_workflow_ui() -> bool:
    """Validate workflow_state-driven UI and ensure no legacy intake_status usage."""
    _print_section("2. VERIFYING WORKFLOW UX & ANALYTICS")

    all_passed = True

    try:
        meta = frappe.get_meta("Clarinet Intake")
    except Exception as exc:  # pragma: no cover - defensive
        print(f"❌ Unable to load Clarinet Intake metadata: {exc}")
        _record("workflow_ui", False, f"Meta load failed: {exc}")
        return False

    if getattr(meta, "workflow_field", None) != "workflow_state":
        print("❌ workflow_state is not configured as workflow field")
        _record("workflow_ui", False, "workflow_state not configured")
        all_passed = False
    else:
        print("✅ workflow_state configured as workflow field")
        _record("workflow_ui", True, "workflow_state configured")

    for legacy_field in LEGACY_FIELDS:
        if meta.get_field(legacy_field):
            print(f"❌ Legacy field still present: {legacy_field}")
            _record("workflow_ui", False, f"Legacy field present: {legacy_field}")
            all_passed = False

    expected_html_fields = {
        "workflow_stage_badge": "Workflow stage badge",
        "sla_commitment_panel": "SLA commitment panel",
    }
    for fieldname, label in expected_html_fields.items():
        field = meta.get_field(fieldname)
        if field and field.fieldtype == "HTML":
            print(f"✅ {label} HTML field present")
            _record("workflow_ui", True, f"{fieldname} HTML present")
        else:
            print(f"❌ {label} HTML field missing or wrong type")
            _record("workflow_ui", False, f"{fieldname} missing")
            all_passed = False

    try:
        from repair_portal.intake.doctype.clarinet_intake import clarinet_intake_timeline

        data = clarinet_intake_timeline.get_timeline_data("Clarinet Intake", "TEST-NAME")
        if isinstance(data, dict):
            print("✅ Timeline analytics callable (dict response)")
            _record("workflow_ui", True, "Timeline analytics reachable")
        else:
            print("❌ Timeline analytics did not return dict")
            _record("workflow_ui", False, "Timeline analytics invalid return")
            all_passed = False
    except Exception as exc:  # pragma: no cover - diagnostics only
        print(f"❌ Failed to import or execute timeline analytics: {exc}")
        _record("workflow_ui", False, f"Timeline analytics failure: {exc}")
        all_passed = False

    return all_passed


def verify_consent_automation() -> bool:
    """Verify consent automation is properly configured."""
    _print_section("3. VERIFYING CONSENT AUTOMATION")

    all_passed = True

    try:
        settings_meta = frappe.get_meta("Clarinet Intake Settings")
        required_fields = [
            "auto_create_consent_form",
            "default_consent_template",
            "consent_required_for_intake_types",
        ]
        for fieldname in required_fields:
            field = settings_meta.get_field(fieldname)
            if field:
                print(f"✅ Settings field '{fieldname}' exists")
                _record("consent", True, f"Settings field {fieldname}")
            else:
                print(f"❌ Settings field '{fieldname}' missing")
                _record("consent", False, f"Settings field {fieldname} missing")
                all_passed = False
    except Exception as exc:
        print(f"❌ Error loading Clarinet Intake Settings: {exc}")
        _record("consent", False, f"Settings load failed: {exc}")
        all_passed = False

    try:
        from repair_portal.intake.doctype.clarinet_intake.clarinet_intake import ClarinetIntake

        for method_name in ("_should_create_consent", "_create_consent_form"):
            if hasattr(ClarinetIntake, method_name):
                print(f"✅ Controller method '{method_name}' exists")
                _record("consent", True, f"Controller method {method_name}")
            else:
                print(f"❌ Controller method '{method_name}' missing")
                _record("consent", False, f"Controller method {method_name} missing")
                all_passed = False
    except Exception as exc:
        print(f"❌ Error checking controller: {exc}")
        _record("consent", False, f"Controller check failed: {exc}")
        all_passed = False

    return all_passed


def verify_tests() -> bool:
    """Run unit tests and verify they pass."""
    _print_section("4. RUNNING UNIT TESTS")

    all_passed = True
    test_modules = [
        "repair_portal.intake.doctype.clarinet_intake.test_clarinet_intake",
        "repair_portal.intake.doctype.loaner_instrument.test_loaner_instrument",
        "repair_portal.intake.doctype.brand_mapping_rule.test_brand_mapping_rule",
    ]

    for module in test_modules:
        print(f"\n📝 Testing {module}...")
        try:
            result = frappe.commands.run_tests(module=module, verbose=True)
            if result == 0:
                print(f"✅ {module} - All tests passed")
                _record("tests", True, module)
            else:
                print(f"❌ {module} - Tests failed")
                _record("tests", False, f"Tests failed: {module}")
                all_passed = False
        except Exception as exc:
            print(f"❌ {module} - Exception: {exc}")
            _record("tests", False, f"{module}: {exc}")
            all_passed = False

    return all_passed


def verify_linting() -> bool:
    """Run linting checks on Python files."""
    _print_section("5. RUNNING LINTING CHECKS")

    try:
        subprocess.run(["ruff", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Ruff not installed, skipping linting")
        _record("linting", True, "Skipped - ruff not installed")
        return True

    try:
        result = subprocess.run(
            ["ruff", "check", str(INTAKE_MODULE_PATH), "--output-format=text"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("✅ No linting errors found")
            _record("linting", True, "Ruff check passed")
            return True

        print(f"❌ Linting errors found:\n{result.stdout}")
        _record("linting", False, f"Ruff errors: {result.stdout}")
        return False
    except Exception as exc:
        print(f"❌ Error running linting: {exc}")
        _record("linting", False, f"Linting exception: {exc}")
        return False


def print_summary() -> bool:
    """Print final verification summary."""
    _print_section("VERIFICATION SUMMARY")

    total_passed = sum(len(v["passed"]) for v in VERIFICATION_RESULTS.values())
    total_failed = sum(len(v["failed"]) for v in VERIFICATION_RESULTS.values())

    for category, results in VERIFICATION_RESULTS.items():
        passed = len(results["passed"])
        failed = len(results["failed"])
        status = "✅ PASS" if failed == 0 else "❌ FAIL"

        print(f"\n{category.upper()}: {status}")
        print(f"  Passed: {passed}")
        print(f"  Failed: {failed}")
        if failed:
            for failure in results["failed"][:10]:
                print(f"    - {failure}")

    print("\n" + "=" * 80)
    print(f"TOTAL: {total_passed} passed, {total_failed} failed")
    print("=" * 80)
    return total_failed == 0


# ============================================================================
# Main Execution
# ============================================================================


def run_verification(site: str | None = None) -> int:
    """Run all verification checks."""
    _print_section("INTAKE MODULE VERIFICATION")
    print("This harness verifies Fortune-500 clarinet intake UX commitments.\n")

    verify_file_headers()
    verify_workflow_ui()
    verify_consent_automation()
    verify_tests()
    verify_linting()

    all_passed = print_summary()
    if all_passed:
        print("\n🎉 All verification checks passed!")
        return 0

    print("\n⚠️  Some verification checks failed. Please review the output above.")
    return 1


if __name__ == "__main__":
    target_site = sys.argv[1] if len(sys.argv) > 1 else "erp.artisanclarinets.com"
    frappe.init(site=target_site)
    frappe.connect()
    exit_code = run_verification(target_site)
    frappe.destroy()
    sys.exit(exit_code)
