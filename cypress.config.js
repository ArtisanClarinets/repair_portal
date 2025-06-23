// cypress.config.js
// Configuration for Cypress test runner

const { defineConfig } = require('cypress');

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:8000',
    supportFile: false,
    fixturesFolder: false,
    defaultCommandTimeout: 10000,
    video: false
  }
});