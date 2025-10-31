#!/usr/bin/env python3
# Path: repair_portal/scripts/analyze_doctype_organization.py
# Date: 2025-10-28
# Version: 1.0.0
# Description: Analyze DocType organization and propose relocations for better cohesion
# Dependencies: json, pathlib

import json
from pathlib import Path
from collections import defaultdict

# Root path for the app
APP_ROOT = Path("/home/frappe/frappe-bench/apps/repair_portal/repair_portal")

# Existing modules
MODULES = {
    "customer": "Customer management and profiles",
    "enhancements": "Upgrade requests and enhancements",
    "inspection": "Instrument inspection workflow",
    "instrument_profile": "Instrument profiles and tracking",
    "instrument_setup": "Clarinet setup and pad mapping",
    "intake": "Instrument intake and loaner management",
    "inventory": "Pad count and inventory tracking",
    "lab": "Measurement sessions and lab work",
    "player_profile": "Player profiles and preferences",
    "qa": "Quality assurance and final checks",
    "repair": "Repair orders and operations",
    "repair_logging": "Repair task logging and materials",
    "repair_portal": "Central portal DocTypes (mixed)",
    "repair_portal_settings": "Settings and configurations",
    "service_planning": "Service plans and estimates",
    "stock": "Stock entry overrides",
    "tools": "Tool management and calibration",
    "trade_shows": "Trade show operations",
}

def get_doctype_info(json_path):
    """Extract key information from DocType JSON"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, dict) or data.get("doctype") != "DocType":
            return None
        
        name = data.get("name")
        module = data.get("module")
        is_child = data.get("istable", 0) == 1
        
        # Analyze fields to understand relationships
        fields = data.get("fields", [])
        links = []
        tables = []
        
        for field in fields:
            if not isinstance(field, dict):
                continue
            
            fieldtype = field.get("fieldtype")
            options = field.get("options")
            fieldname = field.get("fieldname")
            
            if fieldtype == "Link" and options:
                links.append((fieldname, options))
            elif fieldtype == "Table" and options:
                tables.append((fieldname, options))
        
        return {
            "name": name,
            "module": module,
            "is_child": is_child,
            "links": links,
            "tables": tables,
            "path": json_path.relative_to(APP_ROOT)
        }
    except:
        return None

def analyze_repair_portal_doctypes():
    """Analyze all DocTypes in repair_portal/repair_portal/doctype/"""
    portal_doctype_dir = APP_ROOT / "repair_portal" / "doctype"
    
    if not portal_doctype_dir.exists():
        print("Error: repair_portal/doctype directory not found")
        return []
    
    doctypes = []
    for doctype_dir in sorted(portal_doctype_dir.iterdir()):
        if not doctype_dir.is_dir():
            continue
        
        json_file = doctype_dir / f"{doctype_dir.name}.json"
        if json_file.exists():
            info = get_doctype_info(json_file)
            if info:
                doctypes.append(info)
    
    return doctypes

def suggest_module_for_doctype(doctype_info):
    """Suggest the most appropriate module for a DocType based on its characteristics"""
    name = doctype_info["name"]
    name_lower = name.lower()
    links = doctype_info["links"]
    tables = doctype_info["tables"]
    
    # Keyword-based categorization
    suggestions = []
    
    # Intake-related
    if any(kw in name_lower for kw in ["intake", "loaner", "arrival", "shipment"]):
        suggestions.append(("intake", "Name contains intake/loaner/arrival/shipment keywords"))
    
    # Player-related
    if any(kw in name_lower for kw in ["player"]):
        suggestions.append(("player_profile", "Name contains player keywords"))
    
    # Instrument-related
    if any(kw in name_lower for kw in ["instrument"]) and "intake" not in name_lower:
        suggestions.append(("instrument_profile", "Name contains instrument keywords"))
    
    # Repair-related
    if any(kw in name_lower for kw in ["repair", "estimate", "quotation"]):
        suggestions.append(("repair", "Name contains repair keywords"))
    
    # Service planning
    if any(kw in name_lower for kw in ["service_plan", "enrollment"]):
        suggestions.append(("service_planning", "Name contains service plan keywords"))
    
    # QA-related
    if any(kw in name_lower for kw in ["qa_", "qa ", "quality"]):
        suggestions.append(("qa", "Name contains QA keywords"))
    
    # Rental-related
    if any(kw in name_lower for kw in ["rental", "contract"]):
        suggestions.append(("intake", "Name contains rental keywords (rental is part of intake)"))
    
    # Technician/bench
    if any(kw in name_lower for kw in ["technician", "bench"]):
        suggestions.append(("repair", "Name contains technician/bench keywords"))
    
    # Material/BOM
    if any(kw in name_lower for kw in ["material", "bom", "class_parts"]):
        suggestions.append(("repair", "Name contains material/BOM keywords"))
    
    # Mail-in
    if "mail" in name_lower:
        suggestions.append(("intake", "Name contains mail-in keywords"))
    
    # Warranty
    if "warranty" in name_lower:
        suggestions.append(("repair", "Name contains warranty keywords"))
    
    # Check link relationships
    link_targets = [target for _, target in links]
    
    # If links to Clarinet Intake -> intake module
    if "Clarinet Intake" in link_targets:
        suggestions.append(("intake", "Links to Clarinet Intake"))
    
    # If links to Repair Order -> repair module
    if "Repair Order" in link_targets:
        suggestions.append(("repair", "Links to Repair Order"))
    
    # If links to Service Plan -> service_planning
    if "Service Plan" in link_targets:
        suggestions.append(("service_planning", "Links to Service Plan"))
    
    # If links to Player Profile -> player_profile
    if "Player Profile" in link_targets:
        suggestions.append(("player_profile", "Links to Player Profile"))
    
    # If links to Instrument -> instrument_profile
    if "Instrument" in link_targets and "intake" not in name_lower:
        suggestions.append(("instrument_profile", "Links to Instrument"))
    
    # Return most common suggestion
    if suggestions:
        module_counts = defaultdict(list)
        for module, reason in suggestions:
            module_counts[module].append(reason)
        
        # Get module with most reasons
        best_module = max(module_counts.items(), key=lambda x: len(x[1]))
        return best_module[0], module_counts[best_module[0]]
    
    return None, []

def main():
    """Main analysis function"""
    print("=" * 80)
    print("DOCTYPE ORGANIZATION ANALYSIS")
    print("=" * 80)
    print()
    
    # Analyze repair_portal/doctype/
    print("Analyzing DocTypes in repair_portal/repair_portal/doctype/...")
    doctypes = analyze_repair_portal_doctypes()
    print(f"Found {len(doctypes)} DocTypes\n")
    
    # Categorize by type
    parent_doctypes = [d for d in doctypes if not d["is_child"]]
    child_doctypes = [d for d in doctypes if d["is_child"]]
    
    print(f"Parent DocTypes: {len(parent_doctypes)}")
    print(f"Child DocTypes: {len(child_doctypes)}")
    print()
    
    # Analyze each DocType and suggest relocation
    relocations = defaultdict(list)
    keep_in_portal = []
    
    for doctype in parent_doctypes:
        suggested_module, reasons = suggest_module_for_doctype(doctype)
        
        if suggested_module and suggested_module != "repair_portal":
            relocations[suggested_module].append({
                "doctype": doctype,
                "reasons": reasons
            })
        else:
            keep_in_portal.append(doctype)
    
    # Print relocation recommendations
    print("RELOCATION RECOMMENDATIONS")
    print("=" * 80)
    print()
    
    for module in sorted(relocations.keys()):
        items = relocations[module]
        print(f"\n📦 Relocate to '{module}' module ({len(items)} DocTypes):")
        print("-" * 80)
        
        for item in items:
            doctype_info = item["doctype"]
            reasons = item["reasons"]
            print(f"\n  • {doctype_info['name']}")
            print(f"    Current: {doctype_info['path']}")
            print(f"    Reasons:")
            for reason in reasons[:3]:  # Limit to top 3 reasons
                print(f"      - {reason}")
            if doctype_info["links"]:
                link_summary = ", ".join([t for _, t in doctype_info["links"][:3]])
                print(f"    Links to: {link_summary}")
            if len(doctype_info["links"]) > 3:
                print(f"      ... and {len(doctype_info['links']) - 3} more")
    
    print()
    print()
    print("KEEP IN REPAIR_PORTAL MODULE")
    print("=" * 80)
    print(f"DocTypes that should remain in repair_portal module: {len(keep_in_portal)}")
    print()
    for doctype in keep_in_portal:
        print(f"  • {doctype['name']}")
        if doctype["links"]:
            link_summary = ", ".join([t for _, t in doctype["links"][:3]])
            print(f"    Links: {link_summary}")
    
    print()
    print()
    print("SUMMARY STATISTICS")
    print("=" * 80)
    total_relocate = sum(len(items) for items in relocations.values())
    print(f"Total DocTypes analyzed: {len(parent_doctypes)}")
    print(f"Recommended for relocation: {total_relocate}")
    print(f"Remain in repair_portal: {len(keep_in_portal)}")
    print()
    
    print("Relocations by target module:")
    for module in sorted(relocations.keys()):
        print(f"  {module}: {len(relocations[module])} DocTypes")
    
    print()
    print("=" * 80)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
