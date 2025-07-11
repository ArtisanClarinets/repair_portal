import frappe
from frappe.utils import get_url_to_form
from collections import defaultdict
from webshop.webshop.product_data_engine import ProductQuery

FLAG = "show_in_clarinetfest_2025"      # Check field on **Item**

@frappe.whitelist()
def get_catalog_items(search=None):
    """
    AJAX endpoint called by the browser.

    * Uses ProductQuery so we inherit all the price / stock / cart logic.
    * Adds an extra filter so only ClarinetFest items appear.
    * Accepts an optional ?search=<term> to support your live filter box
      after a full reload (nice-to-have, not mandatory).
    """

    # ---- build a ProductQuery instance ----
    pq = ProductQuery.ProductQuery()         # same engine as /all-products
    pq.page_length = 99999                   # we want *everything* in one call
    pq.settings.hide_variants = 0            # show variants if flagged

    # inject our custom filter straight onto the Website Item query
    # Website Item has no FLAG, so we first collect the *item codes*
    flagged = frappe.get_all(
        "Item",
        filters={FLAG: 1, "disabled": 0},
        pluck="item_code"
    )
    if not flagged:
        return {"items": {}, "count": 0}

    pq.filters.append(["item_code", "in", flagged])

    # optional free-text search coming from JS
    if search:
        pq.build_search_filters(search)

    raw = pq.query_items(start=0)[0]         # we only need the list, not the count
    buckets = defaultdict(list)

    for itm in raw:
        # Use Website Item.route if it exists, else Desk form
        website_route = itm.route            # already in the row
        if not website_route:
            website_route = get_url_to_form("Item", itm.item_code)

        itm.route = "/" + website_route.lstrip("/")
        key = (itm.item_group or "").strip().lower()
        buckets[key].append(itm)

    return {"items": buckets, "count": len(raw)}
