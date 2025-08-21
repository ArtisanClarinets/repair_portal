import frappe


def create_bb_clarinet_standard_template():
	"""
	Creates the 'B♭ Clarinet Standard Setup' template based on the new structure
	if it does not already exist.
	"""
	template_name = "B♭ Clarinet Standard Setup"

	if frappe.db.exists("Setup Template", template_name):
		frappe.msgprint(f"☑️ Setup Template '{template_name}' already exists.")
		return

	print(f"Creating Setup Template: {template_name}...")
	try:
		# Create the parent Setup Template document
		template = frappe.get_doc(
			{
				"doctype": "Setup Template",
				"name": template_name,
				"instrument_type": "B♭ Clarinet",
				"version": "v1.0",
				"description": "An engineered process that guarantees an instrument's stability, responsiveness, and acoustic potential is verifiably maximized.",
				# Populate the 'checklist_items' child table
				"checklist_items": [
					# Part I
					{
						"task": "Perform Environmental Logging & Acclimatization",
						"notes": "Case must acclimate for 4+ hours at 45-55% RH before opening.",
					},
					{
						"task": "Complete Visual and Tactile Inspection",
						"notes": "Check for wood fractures and keywork integrity. Upload photos.",
					},
					{
						"task": "Assess Initial Tenon Fit (No Grease)",
						"notes": "Categorize each tenon fit as Loose, Snug (Ideal), or Tight.",
					},
					{
						"task": "Execute Standardized Break-In Schedule",
						"notes": "Log 14 consecutive days of 20-30 min play sessions.",
					},
					{
						"task": "Perform Bore Oiling",
						"notes": "Apply high-quality bore oil after the break-in period, avoiding pads.",
					},
					# Part II
					{
						"task": "Verify Tone Hole Geometry",
						"notes": "Use optical comparator to check rims, undercutting, and finish. Correct as needed.",
					},
					{
						"task": "Perform Precision Tenon Cork Replacement",
						"notes": "Replace factory cork, sand to a precise diameter, and log measurements.",
					},
					# Part III
					{
						"task": "Select and Install All Pads",
						"notes": "Use appropriate pad types (Leather/Synth/Cork). Float pads until perfectly level and verify with feeler gauge.",
					},
					{
						"task": "Optimize Key Heights (Venting)",
						"notes": 'Measure all key openings and adjust to meet target specs (e.g., Register Key: 0.026"-0.029").',
					},
					{
						"task": "Calibrate Spring Tensions",
						"notes": "Use a gram gauge to set tensions to spec (e.g., Upper stack: 30-35 grams).",
					},
					{
						"task": "Perform Inter-Key Regulation",
						"notes": "Ensure all linked key mechanisms close with perfect synchrony.",
					},
					# Part IV
					{
						"task": "Validate System-Wide Airtightness",
						"notes": "Perform Magnehelic gauge test. Must achieve a reading of ≤ 0.2.",
					},
					{
						"task": "Generate Empirical Pitch Curve",
						"notes": "Map the instrument's pitch tendencies across the chromatic scale using a precision tuner.",
					},
					{
						"task": "Perform Voicing & Micro-Adjustments",
						"notes": "Correct individual notes outside of ±5 cents tolerance.",
					},
					{
						"task": "Complete Final Performance Validation",
						"notes": "Holistic play-test for response, timbre, and feel.",
					},
					{
						"task": "Generate Certificate of Acoustic Performance",
						"notes": "Compile all logs and data into the final client-facing report.",
					},
				],
				# Populate the 'operations_performed' child table
				"operations_performed": [
					# Part I: Assessment
					{
						"doctype": "Clarinet Setup Operation",
						"operation_type": "Setup",
						"section": "Barrel",
						"component_ref": "Instrument Case",
						"details": "1. Place sealed case in workshop (45-55% RH).\n2. Allow 4+ hours for acclimatization.\n3. Log date, time, and ambient RH in repair_portal.",
					},
					{
						"doctype": "Clarinet Setup Operation",
						"operation_type": "Setup",
						"section": "Upper Joint",
						"component_ref": "Wood Body & Keywork",
						"details": "1. Under bright, raking light, inspect all wooden parts for fractures.\n2. Examine keywork plating and check for bending.\n3. Note factory pad material and condition.\n4. Upload high-resolution photos of all findings.",
					},
					{
						"doctype": "Clarinet Setup Operation",
						"operation_type": "Tenon Fitting",
						"section": "Upper Joint",
						"component_ref": "Upper & Lower Tenons",
						"details": "1. Gently assemble without cork grease.\n2. Assess fit for wobble or excessive force.\n3. Categorize and log each tenon fit as 'Loose,' 'Snug (Ideal),' or 'Tight'.",
					},
					{
						"doctype": "Clarinet Setup Operation",
						"operation_type": "Setup",
						"section": "Bell",
						"component_ref": "Full Instrument",
						"details": "1. For 14 consecutive days, play instrument for 20-30 minutes daily.\n2. Log each session in the repair_portal.\n3. Thoroughly swab all joints after each session.",
					},
					{
						"doctype": "Clarinet Setup Operation",
						"operation_type": "Setup",
						"section": "Barrel",
						"component_ref": "Bore (Internal)",
						"details": "1. After 14-day acclimatization, apply a very small amount of non-deteriorating bore oil to a swab.\n2. Pass through each wooden joint 1-2 times, avoiding all pads.\n3. Allow instrument to rest for several hours, then wipe out excess.",
					},
					# Part II: Integrity
					{
						"doctype": "Clarinet Setup Operation",
						"operation_type": "Tone Hole Repair",
						"section": "Upper Joint",
						"component_ref": "All Tone Holes",
						"details": "1. Inspect each tone hole rim for a perfectly flat and smooth surface.\n2. Verify undercutting profile against design spec.\n3. Correct any imperfections with a precision tone hole facing tool.\n4. Log pass/fail status for each tone hole.",
					},
					{
						"doctype": "Clarinet Setup Operation",
						"operation_type": "Tenon Fitting",
						"section": "Upper Joint",
						"component_ref": "All Tenons",
						"details": "1. Strip factory cork and clean groove with solvent.\n2. Cut and apply new high-quality sheet cork.\n3. Sand the new cork to a perfectly cylindrical shape, iteratively testing the fit.\n4. Log the final measured diameter of the sanded cork for each tenon.",
					},
					# Part III: Sealing & Action
					{
						"doctype": "Clarinet Setup Operation",
						"operation_type": "Pad Leveling",
						"section": "Upper Joint",
						"component_ref": "All Key Cups",
						"details": "1. Select pad material (Leather/Synthetic/Cork) and size for each key.\n2. Adhere pads using stick shellac.\n3. Heat key cup and 'float' the pad until perfectly parallel with the tone hole.\n4. Verify a perfect seal using a 0.0005\" feeler gauge at 4 cardinal points.",
					},
					{
						"doctype": "Clarinet Setup Operation",
						"operation_type": "Key Height Adjustment",
						"section": "Lower Joint",
						"component_ref": "Key Feet",
						"details": "1. Measure key opening heights with a digital gauge.\n2. Adjust thickness of cork/felt on key feet to match target specifications from setup profile.",
					},
					{
						"doctype": "Clarinet Setup Operation",
						"operation_type": "Spring Tension Adjustment",
						"section": "Upper Joint",
						"component_ref": "All Springs",
						"details": "1. Use a precision gram tension gauge to measure actuation force for each key.\n2. Carefully bend blue steel needle springs to match predefined specs (e.g., 30-35g for upper stack).",
					},
					{
						"doctype": "Clarinet Setup Operation",
						"operation_type": "Key Height Adjustment",
						"section": "Lower Joint",
						"component_ref": "Bridge Key & F/C Linkage",
						"details": "1. Use a feeler gauge to verify that linked keys close with identical pressure at the exact same moment.\n2. Adjust by sanding or replacing regulation materials (no paper shims).",
					},
					# Part IV: Validation
					{
						"doctype": "Clarinet Setup Operation",
						"operation_type": "Setup",
						"section": "Bell",
						"component_ref": "Full Assembled Instrument",
						"details": "1. Seal instrument at barrel and bell.\n2. Introduce low-pressure air and observe Magnehelic gauge.\n3. Leakage must be ≤ 0.2 on a 0-8 scale for certification. Isolate and fix any leaks found.",
					},
					{
						"doctype": "Clarinet Setup Operation",
						"operation_type": "Setup",
						"section": "Bell",
						"component_ref": "Full Assembled Instrument",
						"details": "1. After warm-up, tune to a reference pitch (C5).\n2. Record the cent deviation for each note of the chromatic scale.\n3. Enter data to generate the instrument's visual pitch curve.",
					},
					{
						"doctype": "Clarinet Setup Operation",
						"operation_type": "Setup",
						"section": "Upper Joint",
						"component_ref": "Individual Keys/Pads",
						"details": "1. For notes outside ±5 cents, make micro-adjustments.\n2. Lower pitch by slightly lowering pad height. Raise pitch by raising pad height.\n3. Update pitch curve iteratively until instrument meets tolerance.",
					},
					{
						"doctype": "Clarinet Setup Operation",
						"operation_type": "Setup",
						"section": "Bell",
						"component_ref": "Full Assembled Instrument",
						"details": "Final play-test to evaluate and document subjective qualities: Response, Timbre, and Feel.",
					},
				],
				# 'materials_used' is left empty as requested
				"materials_used": [],
			}
		)

		# Insert the document into the database with admin permissions
		template.insert(ignore_permissions=True)
		frappe.db.commit()
		print(f"✅ Successfully created Setup Template: {template_name}")

	except Exception:
		frappe.log_error(frappe.get_traceback(), "B♭ Clarinet Standard Setup Template Creation Failed")
		frappe.db.rollback()
