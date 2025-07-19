# 🛠️ Technical Debt Log – Customer Module

_Last Updated: 2025-07-16_

## 🔧 Minor
- [ ] Use Frappe ORM instead of raw SQL in `customer_type.py` `_deduplicate_default()`.
- [ ] Add fallback handling to `create_customer()` for users missing `doc.full_name`.
- [ ] Improve error visibility in client portal load failure (e.g. track via `frappe.log_error`).
- [ ] Expand dashboard cards to include context-sensitive filtering (e.g., `customer={{ doc.name }}`).

## 🧪 Testing
- [ ] Add tests for workflow transitions using `frappe.workflow.apply_workflow()`.
- [ ] Add unit tests for consent log and entry doctypes.

## ⚠️ UX
- [ ] Add visual cues or tooltips for frozen profile states in JS.
- [ ] Restore deleted `web_form` folder with public intake wizard.

## 🚫 Deprecated
- [ ] Validate removal of `customer/web_form` from version control history.

## 🗂️ Future Enhancements
- [ ] Add activity timeline to `Customer`.
- [ ] Enable tagging or categorization by usage segment (e.g. student, pro, institution).

---

**Maintainers:** Priscilla – Frappe Engineer
**Reviewed By:** Internal QA, 2025-07
