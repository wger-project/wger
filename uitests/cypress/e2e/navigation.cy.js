/// <reference types="Cypress" />
describe('navigation dashboard page tests', () => {
    beforeEach(() => {
      cy.visit('dashboard')
  
    })

    it('Find header menu', () => {
        cy.get('#main-navbar-navigation');
        
      })

      it('Visible Training menu', () => {
        cy.get('[data-cy="training"]').click();
        cy.get('ul.dropdown-menu.show').should('be.visible');
        
        cy.get('[data-cy="workout"]').click();
        cy.location('pathname').should('eq', '/en/routine/overview');
        cy.go('back').get('[data-cy="training"]').click();

        cy.get('[data-cy="schedule"]').click();
        cy.location('pathname').should('eq', '/en/routine/schedule/overview');
        cy.go('back').get('[data-cy="training"]').click();
        
        cy.get('[data-cy="calendar"]').click();
        cy.get('#main-content');
        cy.go('back').get('[data-cy="training"]').click();

        cy.get('[data-cy="measurement"]').click();
        cy.location('pathname').should('eq', '/en/measurement/');
        cy.go('back').get('[data-cy="training"]').click();

        cy.get('[data-cy="gallery"]').click();
        cy.location('pathname').should('eq', '/en/gallery/overview');
        cy.go('back').get('[data-cy="training"]').click();
        
        cy.get('[data-cy="your_templates"]').click();
        cy.location('pathname').should('eq', '/en/routine/template/overview');
        cy.go('back').get('[data-cy="training"]').click();

        cy.get('[data-cy="public_templates"]').click();
        cy.location('pathname').should('eq', '/en/routine/template/public');
        cy.go('back').get('[data-cy="training"]').click();
        
        cy.get('[data-cy="exercise"]').click();
        cy.location('pathname').should('eq', '/en/exercise/overview/');
        cy.go('back');

                
      })

      it('Visible Nutrition menu', () => {
        cy.get('[data-cy="nutrition"]').click();
        cy.get('ul.dropdown-menu.show').should('be.visible');
        
        cy.get('[data-cy="nutrition_plans"]').click();
        cy.location('pathname').should('eq', '/en/nutrition/overview/');
        cy.go('back').get('[data-cy="nutrition"]').click();

        cy.get('[data-cy="BMI_calculator"]').click();
        cy.location('pathname').should('eq', '/en/nutrition/calculator/bmi/');
        cy.go('back').get('[data-cy="nutrition"]').click();

        cy.get('[data-cy="ingredient_overview"]').click();
        cy.location('pathname').should('eq', '/en/nutrition/ingredient/overview/');
        cy.go('back');
      })

      it('Visible Body weight', () => {
        cy.get('[data-cy="body_weight"]').click();
        cy.get('ul.dropdown-menu.show').should('be.visible');  

        cy.get('[data-cy="weight_overview"]').click();
        cy.location('pathname').should('eq', '/en/weight/overview');
        cy.go('back').get('[data-cy="body_weight"]').click();

        cy.get('[data-cy="weight_add"]').click();
        cy.location('pathname').should('eq', '/en/weight/add/');
        cy.go('back');
      })


      it('Visible About this software', () => {
        cy.get('[data-cy="about-this-software"]').click();
        cy.get('ul.dropdown-menu.show').should('be.visible'); 
        cy.get('[data-cy="about_us"]').click();
        cy.location('pathname').should('eq', '/en/software/about-us');
        cy.go('back');
      })

})