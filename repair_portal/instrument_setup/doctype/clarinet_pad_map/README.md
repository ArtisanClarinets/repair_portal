# Clarinet Pad Map Doctype Overview

## Files Reviewed
- clarinet_pad_map.js
- clarinet_pad_map.py

## Purpose
Automates pad mapping for clarinets based on instrument category, supporting standard types and batch population.

## Main Functions
### clarinet_pad_map.js
- Auto-populates top and bottom joint pads for standard clarinet types.
- Adds custom button for pad population and triggers backend population via server call.

### clarinet_pad_map.py
- `validate`: Auto-populates pad tables for French-style clarinets if empty.
- `get_clarinet_type`: Fetches clarinet type from linked instrument model.
- `populate_standard_pad_names`: Populates standard pad names for top and bottom joints.
- Whitelisted method for client-side JS to trigger auto-population.

## Doctypes Created/Updated/Modified
- Updates child tables for `top_joint_pads` and `bottom_joint_pads`.
- Creates `Clarinet Pad Entry` records.
