# Repair Portal App

## CHANGELOG

### 2025-07-03
- Enforced login on `/my_players` and `/instrument_profile` web controllers.
- Sanitized public `/player_profiles` endpoint to restrict fields and enforce published=1.
- Standardized `serial_number` across all Instrument Profile backend and web form logic.
- Hardened `/api/client_portal.py` endpoint with allow_guest=False and file headers.
- Clarinet Intake QC hold logic updated to release hold on QC pass.
- Secure pagination parameters in `/my_instruments.py`.

**Outstanding:** Portal controller headers (pending directory server error), and review of web form controller `instrument_intake_batch` (blocked by error).

---
