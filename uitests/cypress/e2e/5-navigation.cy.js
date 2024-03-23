/// <reference types="Cypress" />
describe('navigation dashboard page tests', () => {
    beforeEach(() => {
      cy.visit('dashboard')
  
    })

    it('Find header menu', () => {
        cy.get('#main-navbar-navigation');
        
      })

      it('Visible Training menu', () => {
        cy.get('.nav-item.dropdown').first().click();
        cy.get('ul.dropdown-menu.show').should('be.visible');
  
        cy.get('a.dropdown-item').first().click();
        cy.location('pathname').should('eq', '/en/routine/overview');
        cy.go('back').get('.nav-item.dropdown').first().click();

        cy.get('a.dropdown-item').eq(1).click();
        cy.location('pathname').should('eq', '/en/routine/schedule/overview');
        cy.go('back').get('.nav-item.dropdown').first().click();

        
        cy.get('a.dropdown-item').eq(2).click();
        cy.get('#main-content');
        cy.go('back').get('.nav-item.dropdown').first().click();


        cy.get('a.dropdown-item').eq(3).click();
        cy.location('pathname').should('eq', '/en/measurement/');
        cy.go('back').get('.nav-item.dropdown').first().click();

        cy.get('a.dropdown-item').eq(4).click();
        cy.location('pathname').should('eq', '/en/gallery/overview');
        cy.go('back').get('.nav-item.dropdown').first().click();

        
        cy.get('a.dropdown-item').eq(5).click();
        cy.location('pathname').should('eq', '/en/routine/template/overview');
        cy.go('back').get('.nav-item.dropdown').first().click();


        cy.get('a.dropdown-item').eq(6).click();
        cy.location('pathname').should('eq', '/en/routine/template/public');
        cy.go('back').get('.nav-item.dropdown').first().click();
        
        cy.get('a.dropdown-item').eq(7).click();
        cy.location('pathname').should('eq', '/en/exercise/overview/');
        cy.go('back');

                
      })

      it('Visible Nutrition menu', () => {
        cy.get('.nav-item.dropdown').eq(1).click();
        cy.get('ul.dropdown-menu.show').should('be.visible');
        
        cy.get('a.dropdown-item').eq(8).click();
        cy.location('pathname').should('eq', '/en/nutrition/overview/');
        cy.go('back').get('.nav-item.dropdown').eq(1).click();

        cy.get('a.dropdown-item').eq(9).click()
        cy.location('pathname').should('eq', '/en/nutrition/calculator/bmi/');
        cy.go('back').get('.nav-item.dropdown').eq(1).click();
        
        cy.get('a.dropdown-item').eq(10).click()
        cy.location('pathname').should('eq', '/en/nutrition/calculator/calories/');
        cy.go('back').get('.nav-item.dropdown').eq(1).click();

        cy.get('a.dropdown-item').eq(11).click();
        cy.location('pathname').should('eq', '/en/nutrition/ingredient/overview/');
        cy.go('back');
      })

      it('Visible Body weight', () => {
        cy.get('.nav-item.dropdown').eq(2).click();
        cy.get('ul.dropdown-menu.show').should('be.visible');  

        cy.get('a.dropdown-item').eq(12).click();
        cy.location('pathname').should('eq', '/en/weight/overview');
        cy.go('back').get('.nav-item.dropdown').eq(2).click();

        cy.get('a.dropdown-item').eq(13).click();
        cy.location('pathname').should('eq', '/en/weight/add/');
        cy.go('back');
      })


      it('Visible About this software', () => {
        cy.get('.nav-item.dropdown').eq(3).click();
        cy.get('ul.dropdown-menu.show').should('be.visible'); 
        cy.get('a.dropdown-item').eq(14).click();
        cy.location('pathname').should('eq', '/en/software/about-us');
        cy.go('back');
      })

})