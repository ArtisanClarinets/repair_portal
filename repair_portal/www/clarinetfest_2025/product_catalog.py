import frappe

def get_context(context):
    # Fetch published items with fallback to unpublished
    context.items = get_website_items() or get_fallback_items()
    
    # Add dynamic event-specific context
    context.event = {
        "title": "ClarinetFest 2025",
        "booth": "MRW Artisan Instruments",
        "contact": frappe.db.get_value("Contact", {"email_id": "sales@mrw.com"}, "*")
    }

def get_website_items():
    return frappe.db.get_list("Website Item",
        fields=["name", "item_name", "website_image", "web_long_description", 
                "price", "in_stock", "route"],
        filters={"published": 1},
        order_by="item_name"
    )

def get_fallback_items():
    return frappe.db.get_list("Item",
        fields=["item_code as name", "item_name", "image as website_image", 
                "description as web_long_description", "standard_rate as price",
                "concat('item/', item_code) as route"],
        filters={"show_in_website": 1, "disabled": 0},
        order_by="item_name"
    )
