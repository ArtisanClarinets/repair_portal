import frappe


def get_data():
    return [
        {
            "module_name": "Repair Portal",
            "category": "Modules",
            "label": "Repair Portal",
            "icon": "octicon octicon-tools",
            "type": "module",
            "description": "Clarinet-focused technician repair portal.",
        },
        {
            "module_name": "Intake",
            "category": "Modules",
            "label": "Intake",
            "icon": "octicon octicon-inbox",
            "type": "module",
            "description": "Manage clarinet intake requests and tracking.",
        },
        {
            "module_name": "Inspection",
            "category": "Modules",
            "label": "Inspection",
            "icon": "octicon octicon-search",
            "type": "module",
            "description": "Record inspection findings and clarinet condition.",
        },
        {
            "module_name": "Service Planning",
            "category": "Modules",
            "label": "Service Planning",
            "icon": "octicon octicon-list-unordered",
            "type": "module",
            "description": "Plan and categorize service actions.",
        },
        {
            "module_name": "Repair Logging",
            "category": "Modules",
            "label": "Repair Logging",
            "icon": "octicon octicon-tools",
            "type": "module",
            "description": "Track actual repair operations performed.",
        },
        {
            "module_name": "QA",
            "category": "Modules",
            "label": "QA",
            "icon": "octicon octicon-checklist",
            "type": "module",
            "description": "Perform post-repair quality assurance.",
        },
        {
            "module_name": "Tools",
            "category": "Modules",
            "label": "Tools",
            "icon": "octicon octicon-package",
            "type": "module",
            "description": "Manage tools and pad specifications.",
        }
    ]