# Instrument Photo (Child Table)

## Purpose
This child table stores all photo/image records linked to an instrument's lifecycle:
- **Hero/Profile Image**
- **Marketing Photo Gallery**
- **Service Photo Log**

## Fields
- `photo` (Attach Image): Filepath or uploaded image.
- `category` (Select): e.g., 'Hero', 'Marketing', 'Service Before', 'Service After', etc.
- `description` (Data/Text): Context for the image.
- `timestamp` (Datetime): When photo was taken/added.
- `uploaded_by` (Link: User): Staff who uploaded.

## Usage
- Photos are attached at inspection, intake, and during repairs or marketing events.
- Media is referenced in both the Instrument Inspection and Instrument Profile doctypes.

## Compliance
- Only users with instrument edit rights can add/delete.
- Media is retained as part of the instrument’s permanent record for provenance and analytics.
