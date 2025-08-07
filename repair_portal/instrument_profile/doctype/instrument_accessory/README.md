# Instrument Accessory (Child Table)

## Purpose
Captures all accessories currently paired or historically associated with an instrument profile:
- Original case, barrels, bell, mouthpiece
- Aftermarket or upgraded parts (e.g., custom barrels, bells, ligatures, etc.)
- Accessory logs are used for sales bundles, service reference, and provenance.

## Fields
- `item` (Data): Accessory type/name (e.g., Case, Barrel, Bell).
- `desc` (Text): Detailed description (e.g., "BAM Trekking Case", "Fobes Debut 66mm Barrel").
- `serial_no` (Optional, Data): Serial/ID if present (for tracking unique accessories).
- `acquired_date` (Date): When added to instrument.
- `removed_date` (Date): If/when it left the instrument's profile.
- `current` (Check): If it is currently with the instrument.


