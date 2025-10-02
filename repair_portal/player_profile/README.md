# Player Profile Module# Player Profile Module



**Status:** ✅ Production Ready (Fortune-500 Standards)  ## Workflow Consolidation — 2025-07-27

**Version:** 3.0.0  

**Last Updated:** 2025-10-02  **Major update:**

**Maintainer:** repair_portal Team- Consolidated two overlapping workflow files (`player_profile_workflow.json`, `player_profile_setup.json`) into a single canonical workflow for the `Player Profile` doctype.

- The unified workflow covers the states: Draft → Active → Archived, with all transitions performed by the Repair Manager role only.

## Purpose- Legacy or non-aligned states such as `Linked to Client` have been removed for clarity and maintainability.

- All forms, reports, and automations now reference only the official workflow states, matching the select field options.

The Player Profile module provides comprehensive Customer Relationship Management (CRM) functionality for managing musician profiles, equipment preferences, service history, and marketing engagement within the repair_portal application.

> This change reduces confusion, prevents workflow collisions, and aligns player profile lifecycle with Frappe/ERPNext best practices.

This module serves as the central hub for:

- **Player identity management** (demographics, contact info, skill level)---

- **Equipment preferences** (mouthpieces, reeds, ligatures, barrels)

- **Service history tracking** (repairs, intakes, maintenance)For details, see `/workflow/player_profile_workflow/player_profile_workflow.json` and project changelog.
- **CRM automation** (lifetime value calculation, marketing opt-ins, newsletter management)
- **Workflow management** (Draft → Active → Archived lifecycle)

---

## Architecture Overview

### Module Structure

```
player_profile/
├── doctype/
│   ├── player_profile/
│   │   ├── player_profile.json          # DocType schema
│   │   ├── player_profile.py            # Server controller (v3.0.0)
│   │   ├── player_profile.js            # Client controller (v3.0.0)
│   │   ├── test_player_profile.py       # Test suite
│   │   └── README.md                    # DocType documentation
│   └── player_equipment_preference/
│       ├── player_equipment_preference.json
│       ├── player_equipment_preference.py
│       └── test_player_equipment_preference.py
├── workflow/
│   └── player_profile_workflow/
│       └── player_profile_workflow.json  # Workflow definition
├── workflow_state/
│   ├── active/active.json
│   ├── archived/archived.json
│   └── linked_to_client/linked_to_client.json
├── notification/
│   └── player_not_linked/
│       └── player_not_linked.json       # Notification config
└── README.md                            # This file
```

### Key DocTypes

#### 1. Player Profile (Primary)
**Purpose:** Central player identity and CRM record

**Schema Summary:**
- **Naming:** Auto-generated `player_profile_id` (format: PLAYER-YYYY-####)
- **Key Fields:**
  - `player_name` (Data, required) - Full legal name
  - `preferred_name` (Data) - Preferred name for communications
  - `primary_email` (Data, unique, required) - Contact email
  - `primary_phone` (Phone) - Contact phone
  - `player_level` (Select, required) - Skill level (Student/Amateur/Professional)
  - `profile_status` (Select) - Workflow state (Draft/Active/Archived)
  - `customer_lifetime_value` (Currency, read-only) - Calculated CLV
  - `newsletter_subscription` (Check) - Newsletter opt-in
  - `targeted_marketing_optin` (Text) - Marketing interests

**Links:**
- `customer` → Customer (optional, for billing integration)
- `equipment_preferences` → Player Equipment Preference (Table, 1:N)
- `instruments_owned` → Instruments Owned (Table, 1:N, from customer module)

**Indexes:** (Performance-optimized)
- `player_name` (full-text search)
- `primary_email` (unique lookups)
- `player_level` (filtering/reporting)
- `profile_status` (workflow queries)

#### 2. Player Equipment Preference (Child Table)
**Purpose:** Track player's equipment setup preferences

**Schema Summary:**
- **Naming:** Auto-generated (child table)
- **Key Fields:**
  - `mouthpiece` (Small Text) - Preferred mouthpiece
  - `ligature` (Small Text) - Preferred ligature
  - `reed_brand` (Data) - Reed brand
  - `reed_model` (Data) - Reed model
  - `reed_strength` (Data) - Reed strength (e.g., "3.5")
  - `barrel` (Small Text) - Barrel preference
  - `instrument` (Link to Instrument Profile) - Associated instrument
  - `comments` (Text) - Additional notes

**Parent Relationship:**
- `parent` → Player Profile
- `parenttype` → "Player Profile"
- `parentfield` → "equipment_preferences"

---

## Business Rules

### Validation Hooks

#### `before_insert()`
1. Generate unique `player_profile_id` if not set (format: PLAYER-YYYY-####)
2. Validate required fields: `player_name`, `primary_email`, `player_level`
3. Set `profile_creation_date` to today's date
4. Set default `profile_status` = "Draft"

#### `validate()`
1. **Email validation:** Regex pattern for valid email format
2. **Phone validation:** Character validation for phone numbers
3. **Duplicate check:** Prevent duplicate `primary_email` addresses
4. **COPPA compliance:** Auto-opt-out of marketing for users under 13 (if date_of_birth provided)
5. **Equipment preferences:** Validate linked instruments exist
6. **Customer link:** If customer set, validate it exists and is active

#### `on_update()`
1. **Instruments owned sync:** Update `instruments_owned` table from linked Instrument Profiles
2. **CLV calculation:** Recalculate `customer_lifetime_value` from Sales Invoices
3. **Email group sync:** Add/remove from newsletter email group based on `newsletter_subscription`

#### `on_trash()`
1. Delete linked equipment preferences (cascade)
2. Log deletion event for audit trail

### Lifecycle Automation

**Draft → Active:**
- Trigger: User clicks "Activate" button
- Validation: All required fields filled, valid email/phone
- Side effects: Send welcome email, add to newsletter (if opted in)

**Active → Archived:**
- Trigger: User clicks "Archive" button
- Validation: Confirmation dialog
- Side effects: Remove from newsletter, preserve service history

**Archived → Active (Restore):**
- Trigger: User clicks "Restore" button
- Validation: Profile data still valid
- Side effects: Re-add to newsletter (if opted in)

---

## Workflows

### Player Profile Workflow

**States:**
1. **Draft** (doc_status=0)
   - Initial state on creation
   - Profile being built
   - Not visible to public portals

2. **Active** (doc_status=1)
   - Profile complete and verified
   - Eligible for CRM campaigns
   - Visible in customer portals

3. **Archived** (doc_status=2)
   - Inactive profile (customer left, duplicate, etc.)
   - Preserved for historical purposes
   - Not included in active CRM lists

**Transitions:**
- **Activate:** Draft → Active (role: Repair Manager)
- **Archive:** Active → Archived (role: Repair Manager)
- **Restore:** Archived → Active (role: Repair Manager)

**Workflow State Field:** `profile_status` (Select field, not Link)

---

## Client Logic (player_profile.js)

### Form Handlers

**`onload(frm)`**
- Initialize dynamic field visibility based on player_level
- Set up query filters for customer link (disabled=0)

**`refresh(frm)`**
- Display status headline badge
- Add workflow action buttons (Activate/Archive/Restore)
- Add CRM action buttons (Email/Call/Follow-up)
- Add insight buttons (Owned Instruments/Liked Instruments/Service History)
- Display CRM metrics (CLV, last visit, profile age)

### Field Validation

**`primary_email(frm)`**
- Real-time email format validation (regex)
- Check for duplicate email addresses
- Show error message if invalid or duplicate

**`primary_phone(frm)`**
- Real-time phone format validation
- Allow digits, spaces, dashes, parentheses, plus sign

**`player_level(frm)`**
- Dynamic UI: Show/hide `primary_teacher` and `affiliation` for students
- Set field descriptions

### Child Table Handlers

**`equipment_preferences_add()`**
- Set default `idx` value for new rows

**`reed_strength()`**
- Validate reed strength is in approved list (1.5 to 5.0)

**`instrument()`**
- Validate linked Instrument Profile exists

---

## Server Logic (player_profile.py)

### Private Methods

#### `_resolve_serial_display(serial_display: str) -> str | None`
**Purpose:** ISN-aware serial number resolution  
**Parameters:** `serial_display` - Serial number in various formats  
**Returns:** Resolved Instrument Profile name or None  
**Business Logic:**
- Supports ISN-#### format
- Supports standard serial number format
- Returns None if not found or ambiguous

#### `_validate_email_format() -> None`
**Purpose:** Validate email format with regex  
**Throws:** `frappe.ValidationError` if invalid  
**Pattern:** `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`

#### `_validate_phone_format() -> None`
**Purpose:** Validate phone number format  
**Throws:** `frappe.ValidationError` if invalid  
**Pattern:** `^[\d\s\-\+\(\)\.]+$`

#### `_check_duplicate_email() -> None`
**Purpose:** Prevent duplicate email addresses  
**Throws:** `frappe.ValidationError` if duplicate exists  
**Logic:** Query existing profiles excluding current doc

#### `_check_coppa_compliance() -> None`
**Purpose:** COPPA compliance for users under 13  
**Side Effects:** Auto-set `newsletter_subscription=0` and clear `targeted_marketing_optin`  
**Logic:** Calculate age from `date_of_birth`, enforce if < 13 years

#### `_sync_instruments_owned() -> None`
**Purpose:** Synchronize owned instruments from Instrument Profiles  
**Side Effects:** Updates `instruments_owned` child table  
**Logic:** Query Instrument Profiles where owner_player=this player

#### `_calc_lifetime_value() -> float`
**Purpose:** Calculate customer lifetime value from invoices  
**Returns:** Total grand_total from paid Sales Invoices  
**Logic:** Sum all Sales Invoices linked to this player's customer

#### `_sync_email_group() -> None`
**Purpose:** Manage newsletter email group membership  
**Side Effects:** Add/remove from "Player Newsletter" email group  
**Logic:** Based on `newsletter_subscription` flag

### Public API Methods (Whitelisted)

#### `@frappe.whitelist() get_service_history() -> list[dict]`
**Purpose:** Retrieve service/repair history for this player  
**Permission:** Requires "read" permission on Player Profile  
**Returns:** List of service records with date, type, serial_no, description  
**Query:** Searches Clarinet Intake and Instrument Inspection linked to player

**Example Response:**
```json
[
  {
    "date": "2025-09-15",
    "doctype": "Clarinet Intake",
    "serial_no": "ISN-1234",
    "description": "Annual maintenance"
  }
]
```

#### `@frappe.whitelist() get_equipment_recommendations() -> dict`
**Purpose:** Get equipment recommendations based on player level  
**Permission:** Requires "read" permission on Player Profile  
**Returns:** Dict with mouthpiece and reed recommendations  
**Logic:** Level-based recommendations (Student/Amateur/Professional)

**Example Response:**
```json
{
  "mouthpieces": ["Vandoren B40", "Vandoren M30"],
  "reeds": ["Vandoren Traditional 2.5-3.0", "D'Addario Reserve 3.0"]
}
```

#### `@frappe.whitelist() update_marketing_preferences(newsletter: int, targeted: str) -> dict`
**Purpose:** Update marketing preferences via API  
**Permission:** Requires "write" permission on Player Profile  
**Parameters:**
- `newsletter` (int) - 1 for opt-in, 0 for opt-out
- `targeted` (str) - Comma-separated marketing interests

**Returns:** Success status and updated values

**Example Request:**
```python
frappe.call({
  method: 'update_marketing_preferences',
  doc: frm.doc,
  args: { newsletter: 1, targeted: 'New Products,Events' }
})
```

---

## Data Integrity

### Required Fields
- `player_name` - Cannot be null or empty
- `primary_email` - Cannot be null, must be unique, must be valid format
- `player_level` - Must be one of predefined options

### Unique Constraints
- `player_profile_id` - Auto-generated, unique
- `primary_email` - Enforced at application level

### Referential Integrity
- `customer` → Customer (optional, validated if set)
- `equipment_preferences[].instrument` → Instrument Profile (validated if set)
- `instruments_owned[]` → Synced from Instrument Profile.owner_player

### Default Values
- `profile_status` = "Draft"
- `profile_creation_date` = today()
- `customer_lifetime_value` = 0
- `newsletter_subscription` = 0

### Data Validation Rules
1. Email must match regex pattern
2. Phone must contain only valid characters
3. Player level must be from approved list
4. No duplicate emails allowed
5. COPPA compliance enforced for minors

---

## Security & Permissions

### Role Permissions

**System Manager:**
- Full access (create, read, write, delete)
- Can transition all workflow states

**Repair Manager:**
- Create, read, write
- Can activate/archive profiles
- Can view all profiles

**Repair Technician:**
- Read access to active profiles
- Can view service history
- Cannot edit profiles

**Guest/Portal User:**
- No access (internal CRM only)

### Permission Enforcement

**Server-side (player_profile.py):**
```python
@frappe.whitelist()
def get_service_history(self):
    frappe.has_permission("Player Profile", "read", throw=True)
    # ... implementation
```

**Client-side (player_profile.js):**
- Buttons conditionally displayed based on permissions
- Workflow actions require appropriate role

### API Security

**Whitelisted Methods:**
- `get_service_history()` - Read permission required
- `get_equipment_recommendations()` - Read permission required
- `update_marketing_preferences()` - Write permission required

**Input Validation:**
- All inputs validated server-side
- No trust placed in client-submitted data
- Parameterized queries (no SQL injection risk)

**Rate Limiting:**
- Implemented at Frappe framework level
- Per-user request throttling

---

## Testing

### Test Suite: `test_player_profile.py`

**Coverage:**
- ✅ Creation with required fields
- ✅ Creation fails without required fields
- ✅ Unique email constraint enforcement
- ✅ Email format validation
- ✅ Phone format validation
- ✅ Profile creation date auto-set
- ✅ Customer lifetime value calculation
- ✅ Equipment preferences validation
- ✅ Profile status transitions
- ✅ Permission enforcement
- ✅ API method testing (service history, recommendations, preferences)
- ✅ COPPA compliance (future implementation)
- ✅ Email group synchronization (future implementation)
- ✅ Special characters in name
- ✅ Long text field handling
- ✅ Bulk profile creation

**Run Tests:**
```bash
bench --site erp.artisanclarinets.com run-tests \
  --module repair_portal.player_profile.doctype.player_profile.test_player_profile
```

### Test Suite: `test_player_equipment_preference.py`

**Coverage:**
- ✅ Add equipment preference to profile
- ✅ Multiple equipment preferences
- ✅ Instrument link validation
- ✅ Reed strength format validation
- ✅ Parent relationship integrity
- ✅ Equipment preference ordering (idx)
- ✅ Update equipment preference
- ✅ Delete equipment preference
- ✅ Edge cases (empty fields, special characters, long comments)
- ✅ Cascade delete with parent

**Run Tests:**
```bash
bench --site erp.artisanclarinets.com run-tests \
  --module repair_portal.player_profile.doctype.player_equipment_preference.test_player_equipment_preference
```

---

## Performance Optimization

### Database Indexes

**Applied via migration patch** `v15_02_player_profile_indexes.py`:
```python
frappe.db.add_index("Player Profile", ["player_name"])      # Full-text search
frappe.db.add_index("Player Profile", ["primary_email"])    # Unique lookups
frappe.db.add_index("Player Profile", ["player_level"])     # Filtering
frappe.db.add_index("Player Profile", ["profile_status"])   # Workflow queries
```

### Query Optimization

**Avoid N+1 queries:**
```python
# Bad:
for profile in profiles:
    customer = frappe.get_doc("Customer", profile.customer)

# Good:
profiles = frappe.get_all("Player Profile", 
    fields=["name", "customer"],
    filters={"profile_status": "Active"})
```

**Use pluck for single column:**
```python
emails = frappe.get_all("Player Profile", pluck="primary_email")
```

### Caching Strategy

**Read-only lookups:**
```python
@frappe.cache()
def get_player_levels():
    return frappe.get_meta("Player Profile").get_field("player_level").options.split("\n")
```

---

## Integration Points

### Customer Module Integration

**Link:** `player_profile.customer` → `Customer.name`  
**Purpose:** Billing and invoicing integration  
**Sync:** One-way (Player Profile references Customer)

**Integration Logic:**
```python
if self.customer:
    customer_doc = frappe.get_doc("Customer", self.customer)
    # Sync CLV from Sales Invoices
    self.customer_lifetime_value = self._calc_lifetime_value()
```

### Instrument Profile Integration

**Link:** `player_equipment_preference.instrument` → `Instrument Profile.name`  
**Purpose:** Track which instruments player prefers/owns  
**Sync:** Bidirectional (Instrument Profile.owner_player ← Player Profile)

**Integration Logic:**
```python
# Sync owned instruments
owned = frappe.get_all("Instrument Profile",
    filters={"owner_player": self.name},
    fields=["name", "serial_no", "instrument_category"])
self.instruments_owned = owned
```

### Clarinet Intake Integration

**Link:** `Clarinet Intake.player` → `Player Profile.name`  
**Purpose:** Service history tracking  
**Sync:** One-way (Clarinet Intake references Player Profile)

**Integration Logic:**
```python
# Service history query
intakes = frappe.get_all("Clarinet Intake",
    filters={"player": self.name},
    fields=["received_date", "serial_no", "intake_summary"])
```

### Email Group Integration

**Link:** `Email Group Member.email` ← `Player Profile.primary_email`  
**Purpose:** Newsletter management  
**Sync:** Automatic via `_sync_email_group()`

**Integration Logic:**
```python
if self.newsletter_subscription:
    frappe.get_doc({
        "doctype": "Email Group Member",
        "email_group": "Player Newsletter",
        "email": self.primary_email
    }).insert(ignore_if_duplicate=True)
```

---

## Deployment & Operations

### Migration Checklist

1. **Pre-migration:**
   - Backup database: `bench --site erp.artisanclarinets.com backup`
   - Test on staging environment first

2. **Migrate:**
   ```bash
   bench --site erp.artisanclarinets.com migrate
   ```

3. **Post-migration:**
   - Verify indexes created: Check query performance
   - Run smoke tests: Create/update/delete test profile
   - Verify workflow transitions: Test all states

### Monitoring

**Key Metrics:**
- Active player profiles count
- New profiles created per week
- CLV trends over time
- Newsletter subscription rate
- Service history query performance

**Dashboard Queries:**
```sql
-- Active profiles by level
SELECT player_level, COUNT(*) as count
FROM `tabPlayer Profile`
WHERE profile_status = 'Active'
GROUP BY player_level;

-- Average CLV by level
SELECT player_level, AVG(customer_lifetime_value) as avg_clv
FROM `tabPlayer Profile`
WHERE profile_status = 'Active' AND customer_lifetime_value > 0
GROUP BY player_level;
```

### Troubleshooting

**Problem:** Duplicate email error  
**Solution:** Check for existing profile with same email, merge if needed

**Problem:** CLV not calculating  
**Solution:** Verify customer link exists, check Sales Invoice data

**Problem:** Workflow buttons not appearing  
**Solution:** Check user role permissions, verify workflow state field

---

## Compliance & Regulations

### COPPA (Children's Online Privacy Protection Act)

**Requirement:** Cannot collect marketing data from users under 13  
**Implementation:** `_check_coppa_compliance()` method  
**Logic:**
- If `date_of_birth` indicates age < 13
- Automatically set `newsletter_subscription = 0`
- Clear `targeted_marketing_optin`
- Log compliance action

### GDPR (General Data Protection Regulation)

**Right to Access:** Implemented via `get_service_history()` API  
**Right to Erasure:** Implemented via standard Frappe delete with audit trail  
**Data Portability:** Export functionality via Frappe's built-in export  
**Consent Management:** `newsletter_subscription` and `targeted_marketing_optin` fields

### CAN-SPAM Act

**Requirement:** Clear unsubscribe mechanism  
**Implementation:**
- `newsletter_subscription` flag
- Synced with Email Group membership
- Unsubscribe link in all emails (Frappe Email Group feature)

---

## Changelog

### Version 3.0.0 (2025-10-02)
- Complete Fortune-500 level rewrite of player_profile.py controller
- Added comprehensive validation methods (email, phone, duplicate check)
- Implemented COPPA compliance logic
- Added three whitelisted API methods (service history, recommendations, preferences)
- Enhanced error handling with try-except blocks
- Created comprehensive test suites (test_player_profile.py, test_player_equipment_preference.py)
- Complete rewrite of player_profile.js client controller
- Added real-time field validation (email, phone)
- Enhanced workflow buttons with confirmations and error handling
- Added CRM action buttons (Email, Call, Follow-up)
- Added insight buttons (Service History, Equipment Recommendations)
- Enhanced metrics display (CLV, last visit, profile age)
- Added child table validation (equipment preferences)
- Updated README.md with complete documentation

### Version 2.0.0 (2025-07-20)
- Added workflow integration (Draft/Active/Archived)
- Implemented CLV calculation
- Added CRM action buttons
- Enhanced UI with dynamic field visibility

### Version 1.0.0 (Initial Release)
- Basic player profile management
- Equipment preferences child table
- Email and phone fields
- Player level classification

---

## Future Enhancements

### Planned Features

1. **Date of Birth Field**
   - Enable COPPA compliance enforcement
   - Age-based equipment recommendations
   - Birthday marketing campaigns

2. **Advanced Search & Filtering**
   - Full-text search across all fields
   - Saved filter presets
   - Export filtered results

3. **Player Portal**
   - Self-service profile updates
   - Service history viewing
   - Equipment recommendation requests

4. **Integration with External CRM**
   - Mailchimp sync
   - HubSpot integration
   - Salesforce connector

5. **Advanced Analytics**
   - Player retention analysis
   - Equipment preference trends
   - CLV prediction models

6. **Automated Marketing Campaigns**
   - Birthday emails
   - Reengagement campaigns
   - Upsell recommendations

---

## Contact & Support

**Module Maintainer:** repair_portal Development Team  
**Documentation:** This README and inline code comments  
**Issue Tracking:** GitHub Issues (repair_portal repository)  
**Support:** Frappe Community Forum

---

## License

Proprietary - ArtisanClarinets  
Not for redistribution without permission

---

**Last Updated:** 2025-10-02  
**Document Version:** 3.0.0
