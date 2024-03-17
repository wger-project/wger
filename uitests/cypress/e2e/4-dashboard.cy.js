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
        cy.get('div[class="MuiStack-root css-1xhj18k"]');
    })
    it('add weight entry', () => {
       
      cy.get('#react-weight-dashboard').find('button').click();    
      cy.get('#weight').clear().type(60);
      cy.get('div[class="MuiStack-root css-zpn2w"]').find('button').click();
      cy.wait(2000);
      cy.get('#react-weight-dashboard');
      
        })
      

        it('add invalid data weight entry', () => {
       
          cy.get('#react-weight-dashboard').find('button').click();     
          cy.get('div[class="MuiStack-root css-zpn2w"]').find('button').click();
          cy.wait(2000);
          cy.get('form');
         })


            it('close weight entry', () => {
       
              cy.get('#react-weight-dashboard').find('button').click();    
              cy.wait(3000);   
              cy.get('svg[class="MuiSvgIcon-root MuiSvgIcon-fontSizeMedium css-vubbuv"]').first().click();
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
