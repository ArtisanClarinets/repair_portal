# File: repair_portal/repair_portal/hooks.py
# Restored and updated on: 2025-06-13
# Version: 1.2
# Purpose: Complete app definition including instrument_profile and repair module Doctypes

app_name = 'repair_portal'
app_title = 'Repair Portal'
app_publisher = 'MRW Artisan Instruments'
app_description = 'Clarinet repair portal for technicians and managers'
app_email = 'support@artisanclarinets.com'
app_license = 'MIT'

fixtures = [
    {
        'dt': 'Workspace',
        'filters': [
            [
                'name',
                'in',
                [
                    'Enhancements',
                    'Inspection',
                    'Intake',
                    'Instrument Setup',
                    'Instrument Profile',
                    'QA',
                    'Repair Logging',
                    'Service Planning',
                    'Tools',
                    'Repairs',
                ],
            ]
        ],
    },
    {'dt': 'Report', 'filters': [['ref_doctype', 'like', '%']]},
    {'dt': 'Workflow', 'filters': [['name', '!=', '']]},
    {'dt': 'Print Format', 'filters': [['name', '!=', '']]},
    {'dt': 'Notification', 'filters': [['enabled', '=', 1]]},
    {'dt': 'Role'},
    {'dt': 'Role Profile'},
    {'dt': 'Custom Field'},
    {'dt': 'Property Setter'},
    {'dt': 'Client Script', 'filters': [['enabled', '=', 1]]},
    {
        'dt': 'DocType',
        'filters': [['name', 'in', ['Repair Order', 'Repair Task', 'Repair Order Settings']]],
    },
]

website_generators = ['Instrument Profile']
