// File: apps/repair_portal/cypress/e2e/repair_portal_forms.cy.js
// Created: 2025-06-16
// Version: 1.0
// Purpose: Form submission tests for Repair Portal

describe('Repair Portal Form Submissions', () => {

  beforeEach(() => {
    cy.visit('/login')
    cy.get('input[name="login_email"]').type('tech@example.com')
    cy.get('input[name="login_password"]').type('techpass')
    cy.get('button[type="submit"]').click()
  })

  it('Submit Repair Order', () => {
    cy.visit('/app/repair-order/new')
    cy.get('[data-fieldname="customer"]').type('John Smith')
    cy.get('[data-fieldname="issue_description"]').type('Key binding issue')
    cy.get('[data-fieldname="instrument"]').type('Bb Clarinet')
    cy.get('button[data-label="Save"]').click()
    cy.contains('Saved').should('exist')
  })

  it('Submit QA Checklist Item', () => {
    cy.visit('/app/qa-checklist-item/new')
    cy.get('[data-fieldname="check_item"]').type('Seal pads verified')
    cy.get('[data-fieldname="status"]').select('Passed')
    cy.get('button[data-label="Save"]').click()
    cy.contains('Saved').should('exist')
  })

  it('Submit Intake Checklist Item', () => {
    cy.visit('/app/intake-checklist-item/new')
    cy.get('[data-fieldname="item"]').type('Case received')
    cy.get('[data-fieldname="checked"]').click()
    cy.get('button[data-label="Save"]').click()
    cy.contains('Saved').should('exist')
  })

})