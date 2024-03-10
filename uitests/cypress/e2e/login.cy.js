describe('Login form', () => {
    beforeEach(() => {
      cy.visit('user/login')
  
    })
    it('Valid Login', () => {
      cy.get('#id_username').type('Apgnah');
      cy.get('#id_password').type('HjKllpnnB');
      cy.get('#submit-id-submit').click();
      cy.wait(3000);
      cy.url().should('include', 'dashboard');
   })       
    it('Get started', () => {
       cy.get('[data-test="registration"]').click();
       cy.wait(3000);
       cy.url().should('include', 'registration');
    })
    
  })