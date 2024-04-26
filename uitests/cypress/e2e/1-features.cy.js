describe('template spec', () => {
  beforeEach(() => {
    cy.visit('software/features')

  })
  it('Image correct header test', () => {
    cy.get('.header-hero-image')
  })
  it('Get started', () => {
    cy.get('a.btn.btn-primary.rounded-1.bg-dark-blue.py-2.px-5').click();
    cy.url().should('include', 'login');
  })
})