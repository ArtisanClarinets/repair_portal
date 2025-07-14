# Auto-injected test_ignore list to bypass test runner dependency resolution issues
# Last Updated: 2025-07-13

__version__ = '0.0.1'

# Prevent Frappe test runner from trying to auto-create fixtures
# during test runs — avoids TypeError from dependency sorting

test_ignore = [
    "Client Profile", "Client Profile Type", "Consent Log", "Consent Log Entry",
    "Player Profile", "Instruments Owned",
    "Instrument Profile", "Client Instrument Profile", "Pad Condition",
    "Intake Entry", "Document History", "Instrument Document History",
    "Repair Log", "Clarinet Repair Log", "Service Logs", "External Work Logs",
    "Customer External Work Log", "Instrument Condition Record",
    "Warranty Modification Log", "Instrument Tracker", "Instrument Intake Batch",
    "Clarinet Intake", "Intake Checklist Item", "Intake Accessory Item",
    "Loaner Instrument", "Loaner Return Check", "Consent Form Template",
    "Customer Consent Form", "Clarinet Initial Setup", "Clarinet Setup Operation",
    "Setup Checklist Item", "Setup Template", "Material Usage",
    "Inspection Finding", "Clarinet Setup Log"
]
