# Clarinet Pad Map (`clarinet_pad_map`)

## Purpose
The Clarinet Pad Map DocType creates and manages standardized pad layout templates for different clarinet types (Soprano, Bass, Contrabass). It automatically generates comprehensive pad configurations based on instrument family and variant, enabling technicians to have consistent setup references and ensuring all pads are properly addressed during setup and maintenance.

## Schema Summary
- **Naming:** `autoname: "format:PAD-MAP-{clarinet_model}"` (e.g., PAD-MAP-Bb Soprano)
- **Key Fields:**
  - `clarinet_model` (Data): Model identifier (required) - becomes part of naming
  - `clarinet_family` (Select): Instrument family (Soprano, Bass, Contrabass)
  - `clarinet_variant` (Select): Model variant (Standard, Professional, Student)
  - `total_pads` (Int): Total number of pads in the layout (read-only, calculated)
  - `description` (Text): Map purpose and usage notes
  - `is_active` (Check): Whether this map is currently in use (defaults to 1)
- **Pad Layout:**
  - `pad_entries` (Table): Child table of individual pad specifications
  - Each entry contains position, size, material, and configuration details
- **Metadata:**
  - `created_date` (Date): When the map was created
  - `last_updated` (Datetime): Last modification timestamp

## Business Rules

### Automatic Pad Generation
The system automatically populates pad entries based on the clarinet family:

#### Soprano Clarinet Layout
- **Upper Joint**: G#, A, A#, B, C#, D, D#, E, F, F#, G, G#, A (13 pads)
- **Lower Joint**: B, C, C#, D, E♭, E, F (7 pads)
- **Bell**: F# (1 pad)
- **Total**: 21 pads standard for soprano instruments

#### Bass Clarinet Layout  
- **Upper Joint**: G#, A, A#, B, C#, D, D#, E, F, F#, G, G#, A (13 pads)
- **Lower Joint**: B, C, C#, D, E♭, E, F, G, A (9 pads)
- **Bell**: F#, G# (2 pads)
- **Additional**: Low E♭, Low D, Low C (extended range pads)
- **Total**: 27 pads for standard bass clarinet

### Pad Configuration Rules
- **Open vs. Closed**: Each pad is marked as naturally open or closed
- **Material Standards**: Cork, felt, or synthetic materials based on position
- **Size Specifications**: Diameter measurements for replacement ordering
- **Position Mapping**: Joint location and fingering correlation

### Validation Logic
- Model name must be unique within active maps
- Clarinet family must be selected for auto-population
- Pad entries cannot be manually added during auto-population
- Total pad count is calculated automatically and read-only

## Server Logic (`clarinet_pad_map.py`)

### Lifecycle Hooks

1. **`before_save()`**:
   - **Auto-population Trigger**: Calls `populate_pad_entries()` if pad_entries is empty
   - **Pad Count Update**: Recalculates `total_pads` from child table length
   - **Timestamp Management**: Updates `last_updated` field

2. **`validate()`**:
   - **Model Validation**: Ensures clarinet_model is provided and valid
   - **Family Consistency**: Validates family/variant combinations make sense
   - **Duplicate Prevention**: Prevents multiple active maps for same model

### Auto-population System

**`populate_pad_entries()`**: Main orchestration method
- Determines clarinet family from the model name or family field
- Routes to family-specific population methods
- Handles error cases where family cannot be determined
- Updates total_pads count after population

**`populate_soprano_pads()`**: Soprano-specific pad layout
```python
pads = [
    # Upper Joint - 13 pads
    {"pad_position": "G# (Upper)", "joint": "Upper Joint", "is_open_key": 0, "material": "Cork", "diameter_mm": 12.5},
    {"pad_position": "A (Upper)", "joint": "Upper Joint", "is_open_key": 0, "material": "Cork", "diameter_mm": 13.0},
    # ... continues with complete upper joint layout
    
    # Lower Joint - 7 pads  
    {"pad_position": "B (Lower)", "joint": "Lower Joint", "is_open_key": 1, "material": "Felt", "diameter_mm": 15.0},
    # ... continues with lower joint layout
    
    # Bell - 1 pad
    {"pad_position": "F# (Bell)", "joint": "Bell", "is_open_key": 0, "material": "Cork", "diameter_mm": 11.0}
]
```

**`populate_bass_pads()`**: Bass clarinet extended layout
- Includes all soprano pads plus extended range
- Adds Low E♭, Low D, Low C for extended range instruments
- Larger pad diameters for bass instrument scale
- Additional bell pads for bass clarinet acoustics

**`populate_contrabass_pads()`**: Contrabass ultra-extended layout
- Most comprehensive pad set with lowest range extensions
- Includes all bass clarinet pads plus additional low notes
- Extra-large pad specifications for contrabass scale

### Family Detection Logic
**`determine_clarinet_family()`**: Intelligent family detection
- Checks explicit `clarinet_family` field first
- Falls back to model name parsing for keywords:
  - "Bass" or "bass" → Bass
  - "Contrabass" or "contrabass" → Contrabass
  - Default → Soprano
- Case-insensitive matching for robust detection

## Client Logic (`clarinet_pad_map.js`)

### Form Events
1. **`refresh(frm)`**:
   - **Status Display**: Shows active/inactive status in dashboard
   - **Action Buttons**: Provides "Regenerate Pad Layout" button for maintenance
   - **Info Display**: Shows total pad count and last updated information

2. **`onload(frm)`**:
   - **Auto-population Check**: Triggers pad generation if entries are empty
   - **Model Focus**: Sets cursor to clarinet_model field for new documents

3. **`clarinet_model(frm)`**:
   - **Change Handler**: Triggers pad regeneration when model changes
   - **Family Detection**: Updates family field based on model name
   - **Validation**: Prevents duplicate model names

### Action Buttons
- **"Regenerate Pad Layout"**: 
  - Clears existing pad entries
  - Triggers auto-population based on current family
  - Shows progress indicator during regeneration
  - Refreshes form to display new layout

### UI Enhancements
- **Dashboard Indicators**: Shows active status and pad count summary
- **Color Coding**: Active maps displayed with green indicator
- **Quick Actions**: Easy access to regeneration and status toggle
- **Progress Feedback**: Loading states during pad generation

## Child Table: Clarinet Pad Entry

### Field Structure
- **`pad_position`** (Data): Descriptive pad location (e.g., "G# (Upper)")
- **`joint`** (Select): Physical location (Upper Joint, Lower Joint, Bell)
- **`is_open_key`** (Check): Whether pad is naturally open (1) or closed (0)
- **`material`** (Select): Pad material (Cork, Felt, Synthetic)
- **`diameter_mm`** (Float): Pad diameter for ordering replacements
- **`notes`** (Text): Additional specifications or maintenance notes

### Material Standards
- **Cork**: Traditional material for tone holes, provides good seal
- **Felt**: Softer material for keys that need cushioning
- **Synthetic**: Modern materials for durability and consistency

### Size Specifications
- **Soprano**: 11.0mm - 16.0mm range based on position
- **Bass**: 13.0mm - 20.0mm range for larger instrument scale
- **Contrabass**: 15.0mm - 25.0mm range for largest instruments

## Data Integrity

### Required Fields
- `clarinet_model`: Must be unique and descriptive
- `clarinet_family`: Required for auto-population
- At least one pad entry (auto-generated)

### Computed Fields
- `total_pads`: Always calculated from pad_entries length
- `last_updated`: Auto-set on any modification

### Validation Rules
- Model names must be unique among active maps
- Family/variant combinations must be logical
- Pad entries cannot be empty after save
- Diameters must be positive values

### Default Values
- `is_active`: Defaults to 1 (checked)
- `created_date`: Set to today on creation
- Pad materials: Default to "Cork" unless specified

## Integration Points

### Template System Integration
- **Setup Template**: References pad maps for auto-task creation
- **Task Generation**: Each pad becomes a potential setup task
- **Quality Control**: Pad maps define inspection checkpoints

### Inventory Integration
- **Parts Ordering**: Diameter specifications enable automatic parts lookup
- **Material Planning**: Material types drive inventory requirements
- **Replacement History**: Track pad replacement using map as reference

### Workflow Integration  
- **Setup Workflows**: Pad maps drive task creation in setup templates
- **Inspection Workflows**: Each pad position becomes an inspection point
- **Progress Tracking**: Completion tracking per pad position

## Standard Clarinet Configurations

### Soprano B♭ Clarinet (Standard)
- **Total Pads**: 21
- **Range**: E3 to G7 (written pitch)
- **Special Features**: Register key, thumb hole
- **Common Materials**: Cork for tone holes, felt for mechanical keys

### Bass Clarinet (Extended Range)
- **Total Pads**: 27
- **Range**: B♭1 to G7 (written pitch) 
- **Special Features**: Extended low range to low C, additional bell keys
- **Common Materials**: Mix of cork and synthetic for durability

### Contrabass Clarinet (Professional)
- **Total Pads**: 35+
- **Range**: B♭0 to G7 (written pitch)
- **Special Features**: Ultra-extended range, complex key mechanisms
- **Common Materials**: Synthetic pads for extreme low notes

## Test Plan

### Unit Tests
- Test auto-population for each clarinet family
- Test pad count calculation accuracy
- Test family detection logic with various model names
- Test validation rules for duplicate models

### Integration Tests
- Test pad map creation from setup templates
- Test task generation based on pad entries
- Test inventory integration for parts ordering
- Test workflow progression using pad maps

### Data Tests
- Test pad layout accuracy for standard instruments
- Test material assignments match industry standards
- Test diameter specifications for ordering compatibility
- Test open/closed key assignments for proper setup

## Changelog
- **2025-08-16**: Updated autoname format to remove manual prompts, added comprehensive documentation
- **2025-07-15**: Enhanced auto-population with contrabass support
- **2025-06-20**: Added material specifications and diameter tracking
- **2025-05-10**: Initial implementation with soprano and bass clarinet support

## Dependencies
- **Frappe Framework**: Document management, child table handling
- **Parent Integration**: Setup Template (references pad maps)
- **Child Tables**: Clarinet Pad Entry (pad specifications)
- **Related DocTypes**: Clarinet Initial Setup (uses pad maps for task creation)
