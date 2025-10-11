# Instruments Owned

Child table capturing instrument ownership metadata for Player Profiles.

## Fields
- **Instrument Profile** (`instrument_profile`, Link → Instrument Profile) – required reference to the detailed instrument record.
- **Instrument** (`instrument`, Link → Instrument) – optional ERPNext Instrument master.
- **Serial Number** (`serial_number`, Data) – resolved serial value for list views.
- **Model** (`model`, Data) – marketing/model descriptor.
- **Customer** (`customer`, Link → Customer, required) – owning customer account.
- **Ownership Start Date** (`ownership_start_date`, Date) – when the instrument was assigned.
- **Notes** (`notes`, Small Text) – freeform remarks.

## Validation
The controller validates that linked Customer and Instrument Profile documents exist.
