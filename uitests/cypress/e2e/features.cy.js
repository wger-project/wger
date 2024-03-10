describe('template spec', () => {
  beforeEach(() => {
    cy.visit('software/features')

  })
  it('Image correct header test', () => {
    cy.get('.header-hero-image')
  })
  it('Get started', () => {
    cy.get('[data-test ="get started"]').click();
  })
})