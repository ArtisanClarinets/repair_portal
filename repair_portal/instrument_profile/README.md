# Instrument Profile Module

### 📦 Purpose
Central hub for managing customer and inventory instruments. Supports full tracking lifecycle across setup, repair, inspection, and historical data. Website-enabled.

### 📂 Contents
- **DocTypes**: Instrument Profile, Instrument Condition Record
- **Web Form**: Customer instrument registration
- **Page**: Instrument History (public view)
- **Report**: Inventory status breakdown
- **Workspace**: Dashboard + navigation + public access
- **Dashboard Chart**: Status distribution
- **Workflow**: Status transitions (New → Active → In Repair → Retired)
- **Python Logic**: Validation, Web context rendering

### 🔁 Linked Components
- Clarinet Initial Setup
- Condition Notes
- Customers

### 🧪 Testing
- Unit test: `test_instrument_profile.py`
- Manual test: creation, public access, dashboard rendering

### ✅ Status
**PRODUCTION READY** (as of 2025-06-14)

---
_Last rebuilt and validated by Repair Portal Dev GPT_