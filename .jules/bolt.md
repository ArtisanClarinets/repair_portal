## 2024-08-05 - N+1 Query in Client Portal

**Learning:** The `get_my_repairs` function in `repair_portal/api/client_portal.py` was making two separate database calls to fetch instrument profiles, resulting in an N+1 query problem. The first call retrieved the instrument names, and the second retrieved the instrument metadata.

**Action:** I refactored the function to combine these two calls into a single `frappe.get_all` query that retrieves all the necessary fields at once. This eliminates the redundant database call and improves the performance of the API endpoint.
