/// <reference types="Cypress" />
describe('dashboard page tests', () => {
    beforeEach(() => {
      cy.visit('dashboard')
  
    })
    
    it('workout btn ', () => {
        cy.get('a[href="/en/routine/add"]').click();
        cy.wait(3000);
        cy.get('#page-title');
      
    })

    it('nutritional plan add', () => {
       
        cy.get('#react-nutrition-dashboard').find('button').click();
        cy.wait(2000);
        cy.get('form');
        cy.get('#description').clear().type('Lose weight');
        cy.get('#goalEnergy').click();
        cy.get(' #energy').type('1600');
        cy.get('#protein').type('89');
        cy.get('#carbohydrates').type('48');
        cy.get('#fat').type('117');
        cy.get('div[class="MuiStack-root css-zpn2w"]').find('button').click();
        cy.wait(2000);
        cy.get('div[class="MuiCardContent-root css-1lcvsa9"]');
    })
    it('add weight entry', () => {
       
      cy.get('[data-test ="add weight entry"]').click();    
      cy.get('#id_weight').type(85);
      cy.get('#submit-id-submit').click();
      cy.wait(2000);
      cy.get('#main-content');
      
        })
      

        it('add invalid data weight entry', () => {
       
          cy.get('[data-test ="add weight entry"]').click();    
          cy.get('#submit-id-submit').click();
          cy.wait(2000);
          cy.get('#enweightadd');
         })


            it('close weight entry', () => {
       
              cy.get('[data-test ="add weight entry"]').click(); 
              cy.wait(3000);   
              cy.get('[aria-label="Close"]').click();
              cy.wait(2000);
              cy.get('#content');
               })

                it('language', () => {
                                          
                  cy.get('div[class="btn-group dropup"]').find('button').click();
                  cy.get('a[href="/tr/dashboard"]').click();
                  cy.get('h2').invoke('text').then((actualText) => {
                    const trimmedText = actualText.trim();
                    expect(trimmedText).to.equal('Gösterge Paneli');
                    cy.get('div[class="btn-group dropup"]').find('button').click();
                    cy.get('a[href="/zh-hans/dashboard"]').click();
                    cy.get('h2').invoke('text').then((actualText) => {
                      const trimmedText = actualText.trim();
                      expect(trimmedText).to.equal('儀表板');
                    })
                  });
              
                })
               
  })
