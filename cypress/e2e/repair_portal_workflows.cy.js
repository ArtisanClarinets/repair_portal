// File: apps/repair_portal/cypress/e2e/repair_portal_workflows.cy.js
// Created: 2025-06-16
// Version: 1.0
// Purpose: Workflow transition tests for Repair Portal

describe('Repair Portal Workflow Tests', () => {

  before(() => {
    cy.visit('/login')
    cy.get('input[name="login_email"]').type('tech@example.com')
    cy.get('input[name="login_password"]').type('techpass')
    cy.get('button[type="submit"]').click()
  })

  it('Advance Repair Task to In Progress', () => {
    cy.visit('/app/repair-task')
    cy.get('table').contains('td', 'Pending').first().click()
    cy.get('button[data-label="Start Task"]').click()
    cy.contains('Status: In Progress').should('exist')
  })

  it('Complete QA Review Workflow', () => {
    cy.visit('/app/qa-checklist-item')
    cy.get('table').contains('td', 'Pending Review').first().click()
    cy.get('button[data-label="Mark Passed"]').click()
    cy.contains('Status: Passed').should('exist')
  })

})