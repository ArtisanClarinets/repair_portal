Programmatic usage (anywhere in Python)
You (or other server code) can generate a certificate for any setup with:

python
Copy code
doc = frappe.get_doc("Clarinet Initial Setup", "<SETUP_NAME>")
result = doc.generate_certificate(print_format="Clarinet Setup Certificate", attach=1, return_file_url=1)

# result => {"file_url": "...", "file_name": "..."}

If you prefer raw control (exactly what you pasted earlier), the equivalent low-level snippet is:

python
Copy code
html = frappe.get_print("Clarinet Initial Setup", doc.name, "Clarinet Setup Certificate")
pdf = frappe.utils.pdf.get_pdf(html)

# optionally save/attach:

frappe.utils.file_manager.save_file(f"{doc.name} - Setup Certificate.pdf", pdf, doc.doctype, doc.name, is_private=1)
