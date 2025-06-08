import frappe

def execute(filters=None):
    columns = [
        {"label": "Item Code", "fieldname": "item", "fieldtype": "Link", "options": "Item"},
        {"label": "Total Quantity Used", "fieldname": "qty", "fieldtype": "Float"}
    ]

    data = frappe.db.sql("""
        SELECT
            mu.item,
            SUM(mu.quantity) as qty
        FROM `tabMaterial Usage` mu
        JOIN `tabClarinet Initial Setup` cis ON mu.parent = cis.name
        GROUP BY mu.item
    """, as_dict=True)

    return columns, data