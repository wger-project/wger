

describe('register form tests', () => {
    beforeEach(() => {
      cy.visit('user/registration')
  
    })
    
    it('Valid data ', () => {
       cy.get('#id_username').type('gnoooooah');
       cy.get('#id_email').type('hhr@example.com');
       cy.get('#id_password1').type('HjKllpnnB');
       cy.get('#id_password2').type('HjKllpnnB');
       cy.get('#submit-id-submit').click();
       cy.wait(3000);
       cy.url().should('include', 'dashboard');
       
      
    })
    it('InValid data email', () => {
        cy.get('#id_username').type('Anisa');
        cy.get('#id_email').type('arfedorekr.com');
        cy.get('#id_password1').type('HjKllpnnB');
        cy.get('#id_password2').type('HjKllpnnB');
        cy.get('#submit-id-submit').click();
        cy.wait(3000);
     })
     it('InValid data username', () => {
      cy.get('#id_username').type(' ');
      cy.get('#id_email').type('arfedorekr@yh.com');
      cy.get('#id_password1').type('HjKllpnnB');
      cy.get('#id_password2').type('HjKllpnnB');
      cy.get('#submit-id-submit').click();
      cy.wait(3000);
   })
   it('InValid data password', () => {
      cy.get('#id_username').type('Zina');
      cy.get('#id_email').type('arfedorekr@yh.com');
      cy.get('#id_password1').type('hhh');
      cy.get('#id_password2').type('hhh');
      cy.get('#submit-id-submit').click();
      cy.wait(3000);
   })
  })