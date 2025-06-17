// File: repair_portal/cypress/e2e/repair_portal_edge_cases.cy.js
// Date: 2025-06-16
// Version: 1.0
// Purpose: Covers edge cases for Repair Portal forms and workflows

describe('Repair Portal Edge Case Testing', () => {
  beforeEach(() => {
    cy.login('Administrator', 'admin')
  });

  it('should prevent form submission with missing required fields', () => {
    cy.visit('/app/repair-order');
    cy.get('button[data-label="New"]').click();
    cy.get('button[data-label="Save"]').click();
    cy.contains('This field is required').should('exist');
  });

  it('should handle invalid link field entry gracefully', () => {
    cy.visit('/app/repair-order');
    cy.get('button[data-label="New"]').click();
    cy.get('input[data-fieldname="customer"]').type('NonexistentCustomer{enter}');
    cy.contains('Not a valid Customer').should('exist');
  });

  it('should not allow invalid status transition', () => {
    cy.visit('/app/repair-task');
    cy.get('button[data-label="New"]').click();
    cy.get('select[data-fieldname="status"]').select('Completed');
    cy.get('button[data-label="Save"]').click();
    cy.contains('Cannot set status to Completed without work log').should('exist');
  });
});