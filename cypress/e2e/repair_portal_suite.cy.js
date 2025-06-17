// File: apps/repair_portal/cypress/e2e/repair_portal_suite.cy.js
// Created: 2025-06-16
// Version: 1.0
// Purpose: Full Cypress UI suite for Clarinet Repair Portal

describe('Clarinet Repair Portal UI Test Suite', () => {

  it('Home Page Loads', () => {
    cy.visit('/')
    cy.contains('Repair Portal').should('exist')
  })

  it('Redirects to Login when accessing Repair Requests page', () => {
    cy.visit('/repair-requests')
    cy.url().should('include', '/login')
  })

  it('Login Page Visible', () => {
    cy.visit('/login')
    cy.contains('Login').should('exist')
  })

  it('Login with Dummy Credentials (Expect Failure)', () => {
    cy.visit('/login')
    cy.get('input[name="login_email"]').type('dummy@example.com')
    cy.get('input[name="login_password"]').type('wrongpassword')
    cy.get('button[type="submit"]').click()
    cy.contains('Invalid Login').should('exist')
  })

  it('Check QA Checklist UI', () => {
    cy.visit('/app/qa-checklist')
    cy.contains('QA Checklist').should('exist')
  })

  it('Check Intake Form UI Loads', () => {
    cy.visit('/app/intake-checklist-item')
    cy.contains('Intake Checklist Item').should('exist')
  })

  it('Check Repair Order UI Loads', () => {
    cy.visit('/app/repair-order')
    cy.contains('Repair Order').should('exist')
  })

  it('Instrument Profile Navigation', () => {
    cy.visit('/app/instrument-profile')
    cy.contains('Instrument Profile').should('exist')
  })

  it('Tools Workspace Access', () => {
    cy.visit('/app/tools')
    cy.contains('Tools').should('exist')
  })

  it('Verify Service Planning UI Loads', () => {
    cy.visit('/app/service-planning')
    cy.contains('Service Planning').should('exist')
  })

})