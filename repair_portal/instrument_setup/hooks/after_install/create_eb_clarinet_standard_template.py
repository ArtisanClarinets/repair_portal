import frappe

def create_eb_clarinet_standard_template():
    """
    Creates the 'E♭ Clarinet Standard Setup' template based on the specified
    DocType structure if it does not already exist.
    """
    template_name = "E♭ Clarinet Standard Setup"

    if frappe.db.exists("Setup Template", template_name):
        frappe.msgprint(f"☑️ Setup Template '{template_name}' already exists.")
        return

    print(f"Creating Setup Template: {template_name}...")
    try:
        # Create the parent Setup Template document
        template = frappe.get_doc({
            "doctype": "Setup Template",
            "name": template_name,
            "instrument_type": "E♭ Clarinet",
            "version": "v1.0",
            "description": "A meticulous, data-driven setup process for professional E♭ clarinets, establishing a verifiable, industry-leading standard of performance and transparency.",

            # Populate the 'checklist_items' child table
            "checklist_items": [
                # Part I
                {"task": "Perform Environmental Logging & Acclimatization", "notes": "Case must acclimate for a minimum of 4 hours at 45-55% RH before opening."},
                {"task": "Complete Visual and Tactile Inspection", "notes": "Inspect wood for any fractures and keywork for integrity. Document initial pad/cork condition and upload photos."},
                {"task": "Assess Initial Tenon Fit (Dry Fit)", "notes": "Assemble without any grease. Categorize each tenon fit ('Loose', 'Snug (Ideal)', 'Tight') and log the assessment."},
                {"task": "Execute Standardized Break-In Schedule", "notes": "Log 14 consecutive days of 20-30 minute play sessions, ensuring to swab thoroughly after each use."},
                {"task": "Perform Bore Oiling", "notes": "After the break-in period, apply a light coat of high-quality bore oil, taking extreme care to avoid all pads."},
                # Part II
                {"task": "Verify Tone Hole Geometry", "notes": "Use precision tools to inspect tone hole rims, undercutting, and surface finish. Correct any and all imperfections found."},
                {"task": "Perform Precision Tenon Cork Replacement", "notes": "Replace factory cork with premium natural cork. Sand to a precise, quantifiable diameter and log the final measurements."},
                # Part III
                {"task": "Select and Install All Pads", "notes": "Choose appropriate pads (Leather/Synthetic/Cork). 'Float' pads until perfectly parallel with tone holes and verify the seal using a feeler gauge."},
                {"task": "Optimize Key Heights ('Venting')", "notes": "Measure all key opening heights and adjust key foot corks to match the target specifications for an E♭ clarinet."},
                {"task": "Calibrate Spring Tensions", "notes": "Use a gram tension gauge to measure and adjust all spring tensions to the pre-defined specs for an E♭ clarinet."},
                {"task": "Perform Inter-Key Regulation", "notes": "Ensure all linked key mechanisms (e.g., bridge key) close with perfect synchrony and identical pressure."},
                # Part IV
                {"task": "Validate System-Wide Airtightness", "notes": "Use a Magnehelic gauge. The instrument must achieve a reading of ≤ 0.2 for certification."},
                {"task": "Generate Empirical Pitch Curve", "notes": "Map the instrument's intonation tendencies across its full range using a high-precision tuner and a reference setup."},
                {"task": "Perform Voicing and Micro-Adjustments", "notes": "Correct individual notes falling outside the ±5 cents tolerance by adjusting pad heights or undercutting."},
                {"task": "Complete Final Performance Validation", "notes": "Conduct a holistic play-test to evaluate and document the instrument's response, timbre, and feel."},
                {"task": "Generate Certificate of Acoustic Performance", "notes": "Compile all logs, data, and photos into the final, client-facing report."},
            ],

            # Populate the 'operations_performed' child table
            "operations_performed": [
                # Part I: Assessment
                {"doctype": "Clarinet Setup Operation", "operation_type": "Setup", "section": "Barrel", "component_ref": "Instrument Case", "details": "1. Place the sealed case in a workshop maintained at a stable 45% to 55% relative humidity (RH).\n2. Allow a minimum of four hours for temperature acclimatization before opening.\n3. Log the date, time, and ambient RH."},
                {"doctype": "Clarinet Setup Operation", "operation_type": "Setup", "section": "Upper Joint", "component_ref": "Wood Body & Keywork", "details": "1. Under bright, raking light, inspect all wooden parts for hairline fractures, especially at tenon shoulders and around posts.\n2. Examine keywork plating and check for any bending.\n3. Upload high-resolution photos of all findings."},
                {"doctype": "Clarinet Setup Operation", "operation_type": "Tenon Fitting", "section": "Lower Joint", "component_ref": "All Tenons", "details": "1. Gently assemble the instrument without cork grease to assess the raw fit.\n2. Categorize and log each tenon fit as 'Loose,' 'Snug (Ideal),' or 'Tight'."},
                {"doctype": "Clarinet Setup Operation", "operation_type": "Setup", "section": "Bell", "component_ref": "Full Instrument", "details": "1. For 14 consecutive days, play the instrument for a maximum of 30 minutes per day.\n2. Log this activity daily in the repair_portal.\n3. Disassemble and thoroughly swab each joint immediately after each session."},
                {"doctype": "Clarinet Setup Operation", "operation_type": "Setup", "section": "Barrel", "component_ref": "Bore (Internal)", "details": "1. After the 14-day acclimatization, apply a very small amount of high-quality, non-deteriorating bore oil to a pull-through swab.\n2. Pass the swab through each wooden joint 1-2 times, taking extreme care to avoid contact with pads.\n3. Allow the instrument to rest for several hours, then wipe out any excess oil with a clean swab."},

                # Part II: Integrity
                {"doctype": "Clarinet Setup Operation", "operation_type": "Tone Hole Repair", "section": "Upper Joint", "component_ref": "All Tone Holes", "details": "1. Inspect each tone hole rim to ensure it is perfectly flat and smooth.\n2. Verify undercutting profile against design specifications.\n3. Correct any surface imperfections with a precision tone hole facing tool.\n4. Log a pass/fail status for each tone hole."},
                {"doctype": "Clarinet Setup Operation", "operation_type": "Tenon Fitting", "section": "Upper Joint", "component_ref": "All Tenons", "details": "1. Strip factory cork and clean the tenon groove of all adhesive.\n2. Cut a new cork strip with a 45-degree bevel and apply with contact cement.\n3. Sand the new cork to a perfectly cylindrical shape, iteratively testing the fit with calipers.\n4. Log the final measured diameter for each tenon."},

                # Part III: Sealing & Action
                {"doctype": "Clarinet Setup Operation", "operation_type": "Pad Leveling", "section": "Lower Joint", "component_ref": "All Key Cups", "details": "1. Select pad material (Leather/Synthetic/Cork) and size for each key, ensuring it can be leveled.\n2. Adhere pads using stick shellac.\n3. Gently heat the key cup and 'float' the pad until perfectly parallel with the tone hole.\n4. Verify a perfect, leak-free seal using a 0.0005\" feeler gauge."},
                {"doctype": "Clarinet Setup Operation", "operation_type": "Key Height Adjustment", "section": "Upper Joint", "component_ref": "Key Feet", "details": "1. Measure key opening heights with a digital or feeler gauge.\n2. Adjust the thickness of the cork on the key feet to match the target specifications for an E♭ clarinet stored in the setup profile."},
                {"doctype": "Clarinet Setup Operation", "operation_type": "Spring Tension Adjustment", "section": "Lower Joint", "component_ref": "All Springs", "details": "1. Use a precision gram tension gauge to measure the actuation force.\n2. Adjust the curve of each blue steel needle spring until the force matches the pre-defined specification for an E♭ clarinet."},
                {"doctype": "Clarinet Setup Operation", "operation_type": "Key Height Adjustment", "section": "Upper Joint", "component_ref": "Bridge Key & Linked Mechanisms", "details": "1. Use a feeler gauge to verify that linked keys close with identical pressure and timing.\n2. Make adjustments by meticulously sanding or replacing regulation materials (no paper shims)."},

                # Part IV: Validation
                {"doctype": "Clarinet Setup Operation", "operation_type": "Setup", "section": "Bell", "component_ref": "Full Assembled Instrument", "details": "1. Seal the instrument at the barrel and bell openings.\n2. Introduce low-pressure air into the bore and observe the Magnehelic gauge.\n3. The reading must be ≤ 0.2 on a 0-8 scale. Isolate and correct any leaks if the reading is higher."},
                {"doctype": "Clarinet Setup Operation", "operation_type": "Setup", "section": "Bell", "component_ref": "Full Assembled Instrument", "details": "1. After a thorough warm-up, tune to a reference note.\n2. Play the chromatic scale, recording the stabilized cent deviation for each pitch without 'lipping' it into tune.\n3. Enter the data into the repair_portal to generate the visual pitch curve."},
                {"doctype": "Clarinet Setup Operation", "operation_type": "Setup", "section": "Upper Joint", "component_ref": "Individual Keys/Pads", "details": "1. For notes outside ±5 cents tolerance, make micro-adjustments.\n2. To lower pitch, slightly lower the pad height. To raise pitch, raise the pad height or carefully reshape the undercut.\n3. Update the pitch curve iteratively until the instrument meets the intonation tolerance."},
                {"doctype": "Clarinet Setup Operation", "operation_type": "Setup", "section": "Bell", "component_ref": "Full Assembled Instrument", "details": "Perform a final, holistic play-test to evaluate and document subjective qualities: Response, Timbre, and Feel."}
            ],

            # 'materials_used' is intentionally left empty as per the established pattern
            "materials_used": []
        })

        # Insert the document into the database with admin permissions
        template.insert(ignore_permissions=True)
        frappe.db.commit()
        print(f"✅ Successfully created Setup Template: {template_name}")

    except Exception:
        frappe.log_error(frappe.get_traceback(), "E♭ Clarinet Standard Setup Template Creation Failed")
        frappe.db.rollback()

