// File: apps/repair_portal/cypress/e2e/repair_portal_scripts.cy.js
// Created: 2025-06-16
// Version: 1.0
// Purpose: Test custom client-side scripting behaviors in forms

describe('Repair Portal Script Behavior Tests', () => {

  beforeEach(() => {
    cy.visit('/login')
    cy.get('input[name="login_email"]').type('tech@example.com')
    cy.get('input[name="login_password"]').type('techpass')
    cy.get('button[type="submit"]').click()
  })

  it('Dynamic Field Visibility in Repair Order', () => {
    cy.visit('/app/repair-order/new')
    cy.get('[data-fieldname="priority_level"]').select('Urgent')
    cy.get('[data-fieldname="escalation_reason"]').should('be.visible')
  })

  it('Field Auto-population in Repair Task', () => {
    cy.visit('/app/repair-task/new')
    cy.get('[data-fieldname="linked_order"]').type('REPAIR-')
    cy.get('.awesomplete > ul > li').first().click()
    cy.get('[data-fieldname="instrument_serial"]').should('not.have.value', '')
  })

})