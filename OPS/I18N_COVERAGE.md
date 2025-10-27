# I18N Coverage

## Assets Reviewed
- Customer approval portal page (`repair_portal/www/customer_approval.html`).
- Customer approval and payment confirmation emails.
- Warranty reminder emails.
- Portal security helper messaging.

## Locales
- ✅ Spanish (`repair_portal/translations/es_customer_portal.csv`) covers all newly introduced user-facing strings.
- Existing global translation packs remain intact (no removals).

## Validation Steps
1. Ensured every literal string in portal templates and emails is wrapped with `frappe._` for translation.
2. Added Spanish translations for subjects, button labels, error messages, and scheduler notifications.
3. Verified tests render the portal context without translation errors.

## Follow-Up
- Translate the new strings into French and German during the next localization sprint.
- Automate extraction by adding `bench --site $SITE translate` to CI once the environment supports it.
