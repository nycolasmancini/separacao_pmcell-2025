import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import App from './App'

describe('App', () => {
  it('renders login page by default', () => {
    render(<App />)
    const heading = screen.getByText('PMCELL')
    expect(heading).toBeInTheDocument()
  })

  it('renders login form', () => {
    render(<App />)
    const pinText = screen.getByText('Digite seu PIN de acesso')
    expect(pinText).toBeInTheDocument()
  })

  it('has proper route structure', () => {
    render(<App />)
    // Should render login page when not authenticated
    expect(screen.getByText('Separação de Pedidos')).toBeInTheDocument()
  })
})