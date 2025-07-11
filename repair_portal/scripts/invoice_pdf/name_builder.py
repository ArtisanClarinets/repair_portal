import subprocess
import os
import re

def format_instrument_name(raw_description):
    """
    Parses a raw instrument description to extract key, model, and plating,
    and then formats it into a standardized name.

    Args:
        raw_description (str): The description line from the OCR text.

    Returns:
        str: A formatted string like "Model — Key of Key — Plating".
    """
    # --- Mappings for codes ---
    # Maps invoice codes to their proper names.
    key_map = {
        "BB": "B♭",
        "A ": "A", # Space prevents matching 'A' in 'CLARINET'
        "CLAR LA": "A"
    }
    plating_map = {
        "NP": "Nickel Plating",
        "SP": "Silver Plating"
    }
    # A list of known models. Sorted by length descending to match longer,
    # more specific names first (e.g., "BCXXI" before "RC").
    known_models = sorted(
        ["BCXXI", "PRODIGE", "PREMIUM", "FESTIVAL", "MOPANE", "GALA", "E12F", "R13", "RC"],
        key=len,
        reverse=True
    )

    # Normalize the input string for consistent matching
    text = raw_description.upper().replace('\n', ' ')

    # --- Extraction Logic ---
    # 1. Find the instrument's key
    found_key = "Unknown"
    for code, name in key_map.items():
        if text.startswith(code):
            found_key = name
            break

    # 2. Find the instrument's model name
    found_model = ""
    for model in known_models:
        if model in text:
            # Special handling to prevent "R13" from matching "RC"
            if found_model and model in found_model:
                continue
            found_model = model.title()
            break
    
    # Append "Mopane" if it's part of the description but not the primary model
    if "MOPANE" in text and "Mopane" not in found_model:
        found_model = f"{found_model} Mopane".strip()

    # Fallback for unknown models
    if not found_model:
        found_model = "Unknown Model"

    # 3. Find the key plating
    found_plating = ""
    for code, name in plating_map.items():
        # Search for the code as a whole word to avoid partial matches
        if re.search(r'\b' + re.escape(code) + r'\b', text):
            found_plating = name
            break

    # --- Assembly ---
    # Build the final formatted name from the extracted parts.
    name_parts = [found_model]
    if found_key != "Unknown":
        name_parts.append(f"Key of {found_key}")
    if found_plating:
        name_parts.append(found_plating)

    return " — ".join(name_parts)

def extract_model_info_from_invoice(pdf_path):
    """
    Orchestrates the extraction of model information from a PDF invoice.
    It converts the PDF to an image, runs OCR, and then parses the text.

    Args:
        pdf_path (str): The full path to the PDF file.

    Returns:
        A list of dictionaries, each containing the formatted model name
        and the original model number.
    """
    if not os.path.exists(pdf_path):
        print(f"Error: File not found at {pdf_path}")
        return []
        
    print(f"Processing {pdf_path}...")
    base_name = os.path.basename(pdf_path).replace('.pdf', '')

    # 1. Convert PDF to a high-resolution image for better OCR results
    image_output_path = f"temp_image_{base_name}"
    try:
        subprocess.run(
            ["pdftocairo", "-png", "-singlefile", pdf_path, image_output_path],
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
    except FileNotFoundError:
        print("Error: 'pdftocairo' command not found. Is Poppler installed and in your PATH?")
        return []
    except subprocess.CalledProcessError as e:
        print(f"Error with pdftocairo: {e.stderr}")
        return []

    # 2. Use Tesseract to perform OCR on the generated image
    image_file = image_output_path + ".png"
    text_output_path = f"extracted_text_{base_name}"
    try:
        subprocess.run(
            ["tesseract", image_file, text_output_path],
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
    except FileNotFoundError:
        print("Error: 'tesseract' command not found. Is Tesseract installed and in your PATH?")
        os.remove(image_file)
        return []
    except subprocess.CalledProcessError as e:
        print(f"Error with Tesseract: {e.stderr}")
        os.remove(image_file) # Clean up
        return []

    # 3. Read the OCR text for parsing
    try:
        with open(text_output_path + ".txt", 'r', encoding='utf-8') as f:
            text_content = f.read()
    except FileNotFoundError:
        print(f"Error: Tesseract did not produce an output file for {pdf_path}")
        os.remove(image_file)
        return []

    # --- Parsing Logic ---
    # This regex finds all item model numbers (like BC...) and then uses a
    # lookahead to grab all text until the next model number or the end of the file.
    # This effectively splits the text into blocks, one for each item.
    item_blocks = re.findall(r"((?:BC|PC)\S+[\s\S]*?)(?=(?:BC|PC)\S+|$)", text_content)
    
    extracted_items = []
    for block in item_blocks:
        # Find the model number within the block
        model_number_match = re.search(r"((?:BC|PC)\S+)", block)
        if not model_number_match:
            continue
        model_number = model_number_match.group(1).strip()

        # Find the most likely description line within the same block.
        # Descriptions typically start with a key (BB, A) or "STUDENT".
        description_match = re.search(
            r"(?:BB|A |CLAR LA|STUDENT).*?(?:CASE|GIGBAG|DM\*|\n)",
            block,
            re.IGNORECASE | re.DOTALL
        )
        if not description_match:
            continue
        raw_description = description_match.group(0).strip()
        
        # Call the formatting function to get the standardized name
        formatted_name = format_instrument_name(raw_description)

        extracted_items.append({
            "Formatted Name": formatted_name,
            "Model Number": model_number
        })

    # 4. Clean up the temporary files
    os.remove(image_file)
    os.remove(text_output_path + ".txt")

    return extracted_items

# --- Example of how to run the script ---
if __name__ == '__main__':
    # Place your PDF invoices in a folder named 'invoices'
    # or update the path accordingly.
    invoice_folder = '.' 
    
    # Find all PDF files in the specified folder
    pdf_files = [f for f in os.listdir(invoice_folder) if f.lower().endswith('.pdf')]

    if not pdf_files:
        print(f"No PDF files found in the '{invoice_folder}' directory.")
    else:
        print(f"Found {len(pdf_files)} PDF files to process...")

    all_extracted_data = []
    for pdf_file in pdf_files:
        full_path = os.path.join(invoice_folder, pdf_file)
        extracted_data = extract_model_info_from_invoice(full_path)
        if extracted_data:
            print(f"--- Extracted from {pdf_file} ---")
            for item in extracted_data:
                print(f"  Model Number: {item['Model Number']}")
                print(f"  Formatted Name: {item['Formatted Name']}")
            print("-" * (25 + len(pdf_file)))
            all_extracted_data.extend(extracted_data)
        else:
            print(f"Could not extract data from {pdf_file}")

    print("\n--- All Extracted Data ---")
    print(all_extracted_data)