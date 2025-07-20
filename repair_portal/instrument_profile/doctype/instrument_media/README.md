# Instrument Media (Child Table)

## Purpose
Records all audio and video files demonstrating or documenting the instrument’s playability, sound, or condition over time:
- Playtest audio (e.g., "Demo Rose Etudes")
- Video performance clips
- Condition documentation before/after repairs

## Fields
- `media_file` (Attach): Audio or video file.
- `media_type` (Select): Audio or Video
- `description` (Text): Piece performed, context, or notes.
- `timestamp` (Datetime): When recorded/uploaded.
- `uploaded_by` (Link: User): Who added the media.

## Usage
- Media can be added during intake, inspection, or after service/repair events.
- Public-facing files (marketing) vs. internal (condition) can be marked by category or permission.

## Compliance
- Media is part of the official record, supporting provenance and enhanced marketing.
- Audio/video must be handled per company copyright/media policy.
