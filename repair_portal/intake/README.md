# Intake Module

This module handles the initial customer engagement and instrument intake process.

## DocTypes
- **Instrument Intake Form**: Captures serial number, customer, and intake date.
- **Customer Upgrade Request**: Tracks customer-initiated requests for modifications or upgrades.
- **Customer Consent Form**: Legal agreement authorizing inspection and repair. Also includes signature capture.

## Purpose
To formally document instrument reception, gather consent, and initiate service pipeline entry.

## Permissions
- Customer (Owner): Read/Create
- Technician: Read
- Service Manager: Full

## Linked Modules
- Inspection (post-intake diagnostic)
- Repair Logging (initiated after Service Plan)

## Last Updated
June 2025