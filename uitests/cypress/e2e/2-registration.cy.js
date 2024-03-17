function generateRandomName() {
   const randomString = Math.random().toString(36).substring(2, 15);
   return `test_${randomString}`;
 }

function generateRandomEmail() {
   const randomString = Math.random().toString(36).substring(2, 15);
   return `test${randomString}@wger-test.com`;
 }
 
 function generateRandomPassword() {
   return Math.random().toString(36).substring(2, 15);
 }

describe('register form tests', () => {
   beforeEach(() => {
      cy.visit('user/registration')
   })

   it('Valid data ', () => {
      const name = generateRandomName();
      const email = generateRandomEmail();
      const password = generateRandomPassword();
      
      // Storing credentials for later use
      cy.writeFile('cypress/fixtures/credentials.json', {
         name,
         email,
         password
      });

      cy.get('#id_username').type(name);
      cy.get('#id_email').type(email);
      cy.get('#id_password1').type(password);
      cy.get('#id_password2').type(password);
      cy.get('#submit-id-submit').click();
      cy.wait(3000);
      cy.location('pathname').should('eq', '/en/dashboard');
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