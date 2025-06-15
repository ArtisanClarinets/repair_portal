from setuptools import setup, find_packages

# Path: setup.py
# Version: v1.0
# Updated: 2025-06-11
# Purpose: Setup script for Repair Portal Frappe App

setup(
    name="repair_portal",
    version="1.0.0",
    description="Technician-focused Clarinet Repair Portal for ERPNext v15",
    author="Dylan Thompson / MRW Artisan Instruments",
    author_email="support@artisanclarinets.com",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["frappe"],
    entry_points={"frappe.app": ["repair_portal = repair_portal"]},
)
