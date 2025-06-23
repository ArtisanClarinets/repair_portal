// File: apps/repair_portal/cypress/e2e/smoke_test.cy.js
// Created: 2025-06-16
// Version: 1.0
// Purpose: Smoke test for public-facing Clarinet Repair Portal UI

describe('Repair Portal Smoke Test', () => {
  it('Loads the homepage', () => {
    cy.visit('/')
    cy.contains('Repair Portal').should('exist')
  })

  it('Accesses Repair Request form', () => {
    cy.visit('/repair-requests')
    cy.contains('Repair Request').should('exist')
  })

  it('Checks login requirement for repair request', () => {
    cy.visit('/repair-requests')
    cy.url().should('include', '/login')
  })
})