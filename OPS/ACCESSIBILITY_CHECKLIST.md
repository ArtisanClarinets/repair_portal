# Accessibility Checklist

## Portal Approval Page
- ✅ Primary heading `<h1>` receives programmatic focus on load for keyboard users.
- ✅ Semantic landmark (`<main role="main">`) wraps page content.
- ✅ Status messages use `role="status"` and `role="alert"` with `aria-live` attributes.
- ✅ Form controls include explicit `<label>` elements and `aria-required` where applicable.
- ✅ Decision options grouped with `<fieldset>` and `<legend>` for screen readers.
- ✅ Data tables specify `<th scope>` attributes to support header association.
- ✅ Buttons and links maintain accessible contrast via existing Bootstrap classes.

## Email Templates
- ✅ Table-based layout with consistent padding for screen-reader compatibility.
- ✅ Translatable strings ensure locale-specific messaging without embedded images of text.

## Warranty Reminder Job
- ✅ Logging uses descriptive text for monitoring tools; no accessibility concerns for end users.

## Outstanding Items
- 🔄 Evaluate high-contrast theme variants in future cycles once design tokens are available.
