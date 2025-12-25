## 2025-05-28 - Customer Lookup Optimization

**Learning:** `Customer` DocType has a `linked_user` field for direct user-to-customer mapping.
**Action:** Replaced inefficient 2-step (User -> Email -> Customer) lookup with single indexed query on `linked_user`.
