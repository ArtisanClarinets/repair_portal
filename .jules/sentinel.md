## 2025-05-28 - File Upload Security
**Vulnerability:** Unrestricted file uploads in estimator portal could lead to DoS or malicious file hosting.
**Learning:** `frappe.request.files` streams should be validated for size and mimetype before/during read.
**Prevention:** Enforced 5MB limit and strict mimetype allowlist for estimator uploads.
