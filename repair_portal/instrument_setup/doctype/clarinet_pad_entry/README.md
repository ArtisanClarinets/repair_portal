# Clarinet Pad Entry (`clarinet_pad_entry`)

## Purpose
The Clarinet Pad Entry DocType stores individual pad specifications within a Clarinet Pad Map, defining the physical characteristics, materials, and configuration details for each pad position on a clarinet. This enables precise setup instructions, parts ordering, and quality control.

## Schema Summary
- **Naming:** Auto-assigned (system managed)
- **Parent Integration:** Child table of Clarinet Pad Map
- **Key Fields:**
  - `pad_position` (Data): Descriptive location identifier (e.g., "G# (Upper)", "Low Eb")
  - `joint` (Select): Physical location (Upper Joint, Lower Joint, Bell)
  - `is_open_key` (Check): Whether pad is naturally open (1) or closed (0)
  - `material` (Select): Pad material type (Cork, Felt, Synthetic)
  - `diameter_mm` (Float): Pad diameter for replacement ordering
  - `notes` (Text): Additional specifications or maintenance notes

## Business Rules

### Pad Position Standards
- **Descriptive Naming**: Positions use musical note names with location qualifiers
- **Unique Positions**: Each position should be unique within a pad map
- **Standard Notation**: Follows common clarinet fingering chart conventions
- **Location Clarity**: Includes joint reference for physical location

### Joint Classifications
- **Upper Joint**: Typically contains 13 pads for soprano clarinets
  - Includes thumb hole, register key, and upper tone holes
  - Positions: G# through A (upper octave)
- **Lower Joint**: Contains 7-9 pads depending on clarinet type
  - Main body tone holes and some key mechanisms
  - Positions: B through F, sometimes extending to G and A
- **Bell**: Contains 1-3 pads depending on clarinet type
  - Low register extensions and bell keys
  - Positions: F#, sometimes G#, Low Eb, Low D, Low C

### Material Standards
- **Cork**: Traditional material, good seal, moderate durability
  - Used for: Most tone holes, register key, thumb hole
  - Characteristics: Natural material, moldable, requires replacement over time
- **Felt**: Soft material for cushioning and specific sealing needs
  - Used for: Key bumpers, soft closure pads, mechanism cushioning
  - Characteristics: Compressible, good for noise reduction
- **Synthetic**: Modern materials for durability and consistency
  - Used for: High-wear positions, professional instruments, extended range keys
  - Characteristics: Consistent performance, longer life, precise manufacturing

### Open Key Logic
- **Closed Keys (is_open_key = 0)**: Default position is sealed/closed
  - Examples: Most tone holes, register key
  - Behavior: Pressed to open, released to close
- **Open Keys (is_open_key = 1)**: Default position is open/venting
  - Examples: Some mechanism keys, certain extended range keys
  - Behavior: Pressed to close, released to open

## Data Structure

### Physical Specifications
- **`diameter_mm`**: Critical for parts ordering and replacement
  - Range: 8.0mm - 25.0mm depending on position and instrument size
  - Precision: Typically specified to 0.5mm increments
  - Usage: Direct input to parts ordering systems

### Location Identification
- **`pad_position`**: Human-readable position identifier
  - Format: "Note (Location)" e.g., "G# (Upper)", "Low Eb (Bell)"
  - Standards: Follows clarinet fingering nomenclature
  - Uniqueness: Should be unique within pad map

### Configuration Details
- **`joint`**: Physical location for technician reference
- **`is_open_key`**: Mechanical behavior specification
- **`material`**: Replacement material specification
- **`notes`**: Free-form additional specifications

## Auto-population Integration

### Family-Specific Generation
Pad entries are automatically generated based on clarinet family:

#### Soprano Clarinet Standard Layout
```python
# Upper Joint - 13 pads
{"pad_position": "G# (Upper)", "joint": "Upper Joint", "is_open_key": 0, "material": "Cork", "diameter_mm": 12.5}
{"pad_position": "A (Upper)", "joint": "Upper Joint", "is_open_key": 0, "material": "Cork", "diameter_mm": 13.0}
{"pad_position": "A# (Upper)", "joint": "Upper Joint", "is_open_key": 0, "material": "Cork", "diameter_mm": 13.5}
# ... continues for full layout

# Lower Joint - 7 pads
{"pad_position": "B (Lower)", "joint": "Lower Joint", "is_open_key": 1, "material": "Felt", "diameter_mm": 15.0}
# ... continues for lower joint

# Bell - 1 pad
{"pad_position": "F# (Bell)", "joint": "Bell", "is_open_key": 0, "material": "Cork", "diameter_mm": 11.0}
```

#### Bass Clarinet Extended Layout
- Includes all soprano positions plus extended range
- Larger diameter specifications for bass scale
- Additional bell keys for extended low range
- More synthetic materials for durability needs

### Size Specifications by Family
- **Soprano Clarinet**: 8.0mm - 16.0mm diameter range
- **Bass Clarinet**: 10.0mm - 20.0mm diameter range  
- **Contrabass Clarinet**: 12.0mm - 25.0mm diameter range

## Integration Points

### Parts Ordering Integration
- **Diameter Specifications**: Direct input to inventory and ordering systems
- **Material Requirements**: Drives material stock planning
- **Position Identification**: Links to parts catalogs and supplier systems
- **Quantity Planning**: Pad counts drive bulk ordering decisions

### Setup Workflow Integration
- **Task Generation**: Each pad position can become a setup task
- **Quality Control**: Pad specifications define inspection checkpoints
- **Progress Tracking**: Individual pad completion tracking
- **Documentation**: Pad specifications included in setup certificates

### Maintenance Integration
- **Replacement History**: Track individual pad replacements
- **Wear Patterns**: Monitor which positions need frequent replacement
- **Performance Analysis**: Correlate pad specifications with instrument performance
- **Preventive Maintenance**: Schedule replacements based on pad history

## Data Validation

### Required Fields
- **`pad_position`**: Must be descriptive and specific
- **`joint`**: Must be valid joint selection
- **`material`**: Must be valid material type

### Value Validation
- **`diameter_mm`**: Must be positive value, typically 8.0-25.0mm range
- **`is_open_key`**: Boolean value (0 or 1)
- **Position Uniqueness**: Each position should be unique within pad map

### Business Logic Validation
- **Joint Consistency**: Pad positions should align with joint assignments
- **Material Appropriateness**: Materials should be suitable for position type
- **Size Reasonableness**: Diameters should be within expected ranges for clarinet type

## Quality Control Standards

### Pad Sealing Requirements
- **Cork Pads**: Must provide air-tight seal, moldable to tone hole
- **Felt Pads**: Must provide cushioning while maintaining seal
- **Synthetic Pads**: Must maintain consistent seal over extended use

### Replacement Criteria
- **Wear Indicators**: Cracking, hardening, sealing failure
- **Performance Impact**: Affects intonation, response, or leaking
- **Maintenance Schedule**: Preventive replacement based on usage
- **Quality Standards**: Must meet or exceed original specifications

## Usage Examples

### Standard Soprano Clarinet Pad Map
```
Total Pads: 21
Upper Joint:
- G# (Upper): 12.5mm Cork, Closed Key
- A (Upper): 13.0mm Cork, Closed Key  
- Register Key: 8.0mm Cork, Closed Key
- Thumb Hole: 14.0mm Cork, Closed Key
[... complete upper joint layout]

Lower Joint:
- B (Lower): 15.0mm Felt, Open Key
- C (Lower): 14.5mm Cork, Closed Key
[... complete lower joint layout]

Bell:
- F# (Bell): 11.0mm Cork, Closed Key
```

### Bass Clarinet Extended Map
```
Total Pads: 27
[Includes all soprano positions plus:]
Extended Range:
- Low Eb (Bell): 18.0mm Synthetic, Closed Key
- Low D (Bell): 19.0mm Synthetic, Closed Key
- Low C (Bell): 20.0mm Synthetic, Closed Key
```

## Test Plan

### Data Generation Tests
- Test auto-population for each clarinet family
- Test pad count accuracy after generation
- Test position uniqueness within maps
- Test material and diameter assignments

### Integration Tests
- Test parts ordering integration with diameter specs
- Test setup task generation from pad entries
- Test quality control checklist generation
- Test maintenance tracking with pad specifications

### Validation Tests
- Test diameter range validation
- Test position naming consistency
- Test material type validation
- Test open/closed key logic

## Changelog
- **2025-08-16**: Added comprehensive documentation and validation standards
- **2025-07-15**: Enhanced material specifications and diameter tracking
- **2025-06-20**: Added support for extended range instruments
- **2025-05-10**: Initial implementation with basic pad specifications

## Dependencies
- **Frappe Framework**: Child table management, data validation
- **Parent DocType**: Clarinet Pad Map (contains pad entry collections)
- **Integration Points**: Parts ordering systems, setup workflows, quality control systems
- **Reference Standards**: Clarinet fingering charts, manufacturer specifications
