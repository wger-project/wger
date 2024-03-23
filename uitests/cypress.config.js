const { defineConfig } = require("cypress");

module.exports = defineConfig({
  e2e: {
    baseUrl:'http://localhost:8000/en/',
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
  },
});
