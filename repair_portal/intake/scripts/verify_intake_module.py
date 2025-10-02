#!/usr/bin/env python3
# Path: repair_portal/intake/scripts/verify_intake_module.py
# Date: 2025-10-01
# Version: 1.0.0
# Description: End-to-end verification script for intake module fixes and enhancements.
# Dependencies: frappe, subprocess, sys

"""
Intake Module Verification Script
==================================

This script verifies that all intake module enhancements work correctly:
1. All mandatory headers present
2. Workflow field exists and is properly configured
3. Consent automation is properly wired
4. Tests execute successfully
5. No linting errors or security issues

Run from frappe-bench directory:
    bench --site <site_name> execute repair_portal.intake.scripts.verify_intake_module.run_verification

Or directly with Python:
    python3 repair_portal/intake/scripts/verify_intake_module.py
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import frappe

# ============================================================================
# Configuration
# ============================================================================

INTAKE_MODULE_PATH = Path("repair_portal") / "intake"
REQUIRED_HEADER_PATTERN = re.compile(
	r"# Path: .+\n# Date: \d{4}-\d{2}-\d{2}\n# Version: \d+\.\d+\.\d+\n# Description: .+\n(?:# Dependencies: .*\n)?"
)

VERIFICATION_RESULTS: dict[str, dict[str, Any]] = {
	"headers": {"passed": [], "failed": []},
	"workflow": {"passed": [], "failed": []},
	"consent": {"passed": [], "failed": []},
	"tests": {"passed": [], "failed": []},
	"linting": {"passed": [], "failed": []},
}


# ============================================================================
# Verification Functions
# ============================================================================

def verify_file_headers() -> bool:
	"""Verify all Python and JavaScript files have mandatory 5-line headers."""
	print("\n" + "=" * 80)
	print("1. VERIFYING FILE HEADERS")
	print("=" * 80)
	
	all_passed = True
	files_checked = 0
	
	# Check all .py and .js files in intake module
	for ext in ["*.py", "*.js"]:
		for file_path in INTAKE_MODULE_PATH.rglob(ext):
			# Skip __pycache__ and node_modules
			if "__pycache__" in str(file_path) or "node_modules" in str(file_path):
				continue
			
			files_checked += 1
			content = file_path.read_text(encoding="utf-8")
			
			if REQUIRED_HEADER_PATTERN.match(content):
				VERIFICATION_RESULTS["headers"]["passed"].append(str(file_path))
				print(f"✅ {file_path.relative_to('repair_portal')}")
			else:
				VERIFICATION_RESULTS["headers"]["failed"].append(str(file_path))
				print(f"❌ {file_path.relative_to('repair_portal')} - Missing or invalid header")
				all_passed = False
	
	print(f"\nHeaders checked: {files_checked}")
	print(f"Passed: {len(VERIFICATION_RESULTS['headers']['passed'])}")
	print(f"Failed: {len(VERIFICATION_RESULTS['headers']['failed'])}")
	
	return all_passed


def verify_workflow_field() -> bool:
	"""Verify intake_status field exists in Clarinet Intake DocType."""
	print("\n" + "=" * 80)
	print("2. VERIFYING WORKFLOW FIELD")
	print("=" * 80)
	
	try:
		# Check if field exists in DocType
		meta = frappe.get_meta("Clarinet Intake")
		field = meta.get_field("intake_status")
		
		if not field:
			print("❌ intake_status field not found in Clarinet Intake")
			VERIFICATION_RESULTS["workflow"]["failed"].append("intake_status field missing")
			return False
		
		# Verify field properties
		checks = [
			(field.fieldtype == "Select", "Field type must be Select"),
			(field.label == "Intake Status", "Field label must be 'Intake Status'"),
			(field.options and "Pending" in field.options, "Field options must include workflow states"),
		]
		
		all_passed = True
		for check, error_msg in checks:
			if check:
				print(f"✅ {error_msg}")
				VERIFICATION_RESULTS["workflow"]["passed"].append(error_msg)
			else:
				print(f"❌ {error_msg}")
				VERIFICATION_RESULTS["workflow"]["failed"].append(error_msg)
				all_passed = False
		
		return all_passed
		
	except Exception as e:
		print(f"❌ Error checking workflow field: {e}")
		VERIFICATION_RESULTS["workflow"]["failed"].append(f"Exception: {e}")
		return False


def verify_consent_automation() -> bool:
	"""Verify consent automation is properly configured."""
	print("\n" + "=" * 80)
	print("3. VERIFYING CONSENT AUTOMATION")
	print("=" * 80)
	
	all_passed = True
	
	# Check settings DocType has required fields
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
				VERIFICATION_RESULTS["consent"]["passed"].append(f"Settings field {fieldname}")
			else:
				print(f"❌ Settings field '{fieldname}' missing")
				VERIFICATION_RESULTS["consent"]["failed"].append(f"Settings field {fieldname} missing")
				all_passed = False
				
	except Exception as e:
		print(f"❌ Error checking settings: {e}")
		VERIFICATION_RESULTS["consent"]["failed"].append(f"Settings check failed: {e}")
		all_passed = False
	
	# Check controller has required methods
	try:
		from repair_portal.intake.doctype.clarinet_intake.clarinet_intake import ClarinetIntake
		
		required_methods = ["_should_create_consent", "_create_consent_form"]
		
		for method_name in required_methods:
			if hasattr(ClarinetIntake, method_name):
				print(f"✅ Controller method '{method_name}' exists")
				VERIFICATION_RESULTS["consent"]["passed"].append(f"Controller method {method_name}")
			else:
				print(f"❌ Controller method '{method_name}' missing")
				VERIFICATION_RESULTS["consent"]["failed"].append(f"Controller method {method_name} missing")
				all_passed = False
				
	except Exception as e:
		print(f"❌ Error checking controller: {e}")
		VERIFICATION_RESULTS["consent"]["failed"].append(f"Controller check failed: {e}")
		all_passed = False
	
	return all_passed


def verify_tests() -> bool:
	"""Run unit tests and verify they pass."""
	print("\n" + "=" * 80)
	print("4. RUNNING UNIT TESTS")
	print("=" * 80)
	
	all_passed = True
	
	test_modules = [
		"repair_portal.intake.doctype.clarinet_intake.test_clarinet_intake",
		"repair_portal.intake.doctype.loaner_instrument.test_loaner_instrument",
		"repair_portal.intake.doctype.brand_mapping_rule.test_brand_mapping_rule",
	]
	
	for module in test_modules:
		print(f"\n📝 Testing {module}...")
		try:
			# Run tests using Frappe's test runner
			result = frappe.commands.run_tests(module=module, verbose=True)
			
			if result == 0:  # Success
				print(f"✅ {module} - All tests passed")
				VERIFICATION_RESULTS["tests"]["passed"].append(module)
			else:
				print(f"❌ {module} - Tests failed")
				VERIFICATION_RESULTS["tests"]["failed"].append(module)
				all_passed = False
				
		except Exception as e:
			print(f"❌ {module} - Exception: {e}")
			VERIFICATION_RESULTS["tests"]["failed"].append(f"{module}: {e}")
			all_passed = False
	
	return all_passed


def verify_linting() -> bool:
	"""Run linting checks on Python files."""
	print("\n" + "=" * 80)
	print("5. RUNNING LINTING CHECKS")
	print("=" * 80)
	
	all_passed = True
	
	# Check if ruff is available
	try:
		subprocess.run(["ruff", "--version"], capture_output=True, check=True)
	except (subprocess.CalledProcessError, FileNotFoundError):
		print("⚠️  Ruff not installed, skipping linting")
		VERIFICATION_RESULTS["linting"]["passed"].append("Skipped - ruff not installed")
		return True
	
	# Run ruff check
	try:
		result = subprocess.run(
			["ruff", "check", str(INTAKE_MODULE_PATH), "--output-format=text"],
			capture_output=True,
			text=True,
		)
		
		if result.returncode == 0:
			print("✅ No linting errors found")
			VERIFICATION_RESULTS["linting"]["passed"].append("Ruff check passed")
		else:
			print(f"❌ Linting errors found:\n{result.stdout}")
			VERIFICATION_RESULTS["linting"]["failed"].append(f"Ruff errors: {result.stdout}")
			all_passed = False
			
	except Exception as e:
		print(f"❌ Error running linting: {e}")
		VERIFICATION_RESULTS["linting"]["failed"].append(f"Linting exception: {e}")
		all_passed = False
	
	return all_passed


def print_summary():
	"""Print final verification summary."""
	print("\n" + "=" * 80)
	print("VERIFICATION SUMMARY")
	print("=" * 80)
	
	total_passed = sum(len(v["passed"]) for v in VERIFICATION_RESULTS.values())
	total_failed = sum(len(v["failed"]) for v in VERIFICATION_RESULTS.values())
	
	for category, results in VERIFICATION_RESULTS.items():
		passed = len(results["passed"])
		failed = len(results["failed"])
		status = "✅ PASS" if failed == 0 else "❌ FAIL"
		
		print(f"\n{category.upper()}: {status}")
		print(f"  Passed: {passed}")
		print(f"  Failed: {failed}")
		
		if failed > 0 and len(results["failed"]) <= 10:  # Show first 10 failures
			for failure in results["failed"][:10]:
				print(f"    - {failure}")
	
	print("\n" + "=" * 80)
	print(f"TOTAL: {total_passed} passed, {total_failed} failed")
	print("=" * 80)
	
	return total_failed == 0


# ============================================================================
# Main Execution
# ============================================================================

def run_verification() -> int:
	"""Run all verification checks."""
	print("\n" + "=" * 80)
	print("INTAKE MODULE VERIFICATION")
	print("=" * 80)
	print("\nThis script verifies:")
	print("  1. All files have mandatory headers")
	print("  2. Workflow field is properly configured")
	print("  3. Consent automation is wired correctly")
	print("  4. Unit tests execute successfully")
	print("  5. No linting errors exist")
	print("\n" + "=" * 80)
	
	# Run all checks
	results = [
		verify_file_headers(),
		verify_workflow_field(),
		verify_consent_automation(),
		verify_tests(),
		verify_linting(),
	]
	
	# Print summary
	all_passed = print_summary()
	
	if all_passed:
		print("\n🎉 All verification checks passed!")
		return 0
	else:
		print("\n⚠️  Some verification checks failed. Please review the output above.")
		return 1


if __name__ == "__main__":
	# If run directly with Python
	import frappe
	
	# Initialize Frappe
	if not frappe._dict:
		site = sys.argv[1] if len(sys.argv) > 1 else "erp.artisanclarinets.com"
		frappe.init(site)
		frappe.connect()
	
	exit_code = run_verification()
	sys.exit(exit_code)
