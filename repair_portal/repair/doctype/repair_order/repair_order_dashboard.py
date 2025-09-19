# Simple dashboard linking key doctypes from the parent
def get_data():
    return {
        "fieldname": "repair_order",
        "transactions": [
            {
                "label": "Stages",
                "items": [
                    "Clarinet Intake",
                    "Instrument Inspection",
                    "Service Plan",
                    "Repair Estimate",
                    "Final QA Checklist",
                    "Measurement Session",
                    "Repair Task",
                ],
            }
        ],
    }
