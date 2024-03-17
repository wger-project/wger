describe('Login form', () => {
    beforeEach(() => {
      cy.visit('user/login')
  
    })
    it('Valid Login', () => {
      // Reading credentials
      cy.fixture('credentials').then((creds) => {
        const { name, email, password } = creds;
        cy.get('#id_username').type(name);
        cy.get('#id_password').type(password);
        cy.get('#submit-id-submit').click();
        cy.wait(3000);
        cy.url().should('include', 'dashboard');
      });
    })       
    it('Get started', () => {
       cy.get('#main-sidebar').find('a[href="/en/user/registration"]').click();
       cy.wait(3000);
       cy.url().should('include', 'registration');
    })
    it('Login/Register', () => {
      cy.get('#main-navbar-navigation').find('a[href="#"]').click();
      cy.get('ul.dropdown-menu.show').should('be.visible');
      cy.get('ul.dropdown-menu.show').find('a[href="/en/user/login"]').click();
      cy.url().should('include', 'login');
      cy.go('forward').get('#main-navbar-navigation').find('a[href="#"]').click();

      cy.get('ul.dropdown-menu.show').find('a[href="/en/user/registration"]').click(); 
      cy.url().should('include', 'registration');
      cy.go('forward').get('#main-navbar-navigation').find('a[href="#"]').click();

     
      cy.get('ul.dropdown-menu.show').find('a[href="/en/user/password/reset/"]').click(); 
      cy.url().should('include', 'reset');
         

   })
    
  })