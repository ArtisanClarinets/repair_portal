#!/bin/bash
# Script: run_all_tests.sh
# Purpose: Run all Cypress test suites for Repair Portal

export CYPRESS_BASE_URL=http://localhost:8000

npx cypress run --spec \
  cypress/e2e/repair_portal_suite.cy.js \
  cypress/e2e/repair_portal_roles.cy.js \
  cypress/e2e/repair_portal_forms.cy.js \
  cypress/e2e/repair_portal_workflows.cy.js \
  cypress/e2e/repair_portal_scripts.cy.js

echo "✅ All Cypress test suites executed."
