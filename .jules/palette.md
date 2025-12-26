## 2025-12-18 - Improve Form Feedback Accessibility
**Learning:** Dynamic status messages are often missed by screen readers if not marked with ARIA roles.
**Action:** Added `role=status` and `role=alert` to form feedback containers in `mail_in_repair.html`.

## 2025-12-18 - Accessibility for Quote Portal
**Learning:** Quote approval page lacked ARIA live regions for dynamic feedback.
**Action:** Added `role=status` and `role=alert` to feedback containers in `quote/index.html`.
## 2025-12-20 - [Low] Improve Button Accessibility
**Learning:** Custom UI elements, such as buttons created with `add_custom_button`, must have appropriate accessibility attributes to be usable by everyone.
**Action:** Added `aria-label` attributes to the custom buttons in the `Tone Hole Inspection Record` to provide a clear description of their function for screen reader users.
**Action:** Added `role="status"` and `role="alert"` to feedback containers in `quote/index.html`.

## 2025-12-19 - Submit Button Loading State
**Learning:** Users lack feedback during asynchronous form submission, leading to confusion or double-submission.
**Action:** Added disabled state and "Processing..." text to the submit button in `quote/index.html` during API calls.

## 2025-12-21 - Accessible Technician Dashboard
**Learning:** Single Page Applications (SPAs) must manage focus and announcements for loading/error states for screen reader users.
**Action:** Added `role="status"`/`alert` and `aria-live` attributes to `App.vue` loading and error containers.
## 2025-12-22 - SLA Status Accessibility
**Learning:** Color alone is not sufficient to convey information for users with color vision deficiencies.
**Action:** Added icons to the SLA status indicators in the Repair Order list view to provide a non-color-based visual cue.

## 2025-12-22 - Accessible Form Hints
**Learning:** Input hints (small text below inputs) are often skipped by screen readers unless explicitly linked.
**Action:** Added `aria-describedby` to Customer Name, Email, and Phone inputs in `CustomerStep.vue` to programmaticly associate them with their hint text.

## 2025-12-22 - Mail-In Form Loading State
**Learning:** Users need feedback when a form is submitting to avoid confusion and double submissions.
**Action:** Added a loading state (disabled button + "Processing..." text) to the Mail-In Repair form submit button.
