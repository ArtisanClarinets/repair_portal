import frappe
def get_context(context):
    context.items = frappe.db.get_list("Item",  # Or "Website Item" for published products
        fields=["item_code", "item_name", "description", "standard_rate"],
        filters={"disabled": 0},  # Exclude disabled items
        order_by="item_name asc"
    )
		if not frappe.db.exists("Website Item", {"item_code": item.item_code}):
    		context.fallback = True