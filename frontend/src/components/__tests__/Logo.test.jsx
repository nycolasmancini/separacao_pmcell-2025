import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import Logo, { LogoIcon, LogoText } from '../Logo';

describe('Logo Component', () => {
  it('should render logo with default props', () => {
    render(<Logo />);
    
    expect(screen.getByText('PMCELL')).toBeInTheDocument();
    expect(screen.getByText('Separação de Pedidos')).toBeInTheDocument();
    expect(screen.getByText('P')).toBeInTheDocument();
  });

  it('should render with different sizes', () => {
    const { rerender } = render(<Logo size="sm" />);
    expect(screen.getByText('PMCELL')).toBeInTheDocument();

    rerender(<Logo size="lg" />);
    expect(screen.getByText('PMCELL')).toBeInTheDocument();
  });

  it('should render with different variants', () => {
    const { rerender } = render(<Logo variant="white" />);
    expect(screen.getByText('PMCELL')).toBeInTheDocument();

    rerender(<Logo variant="minimal" />);
    expect(screen.getByText('PMCELL')).toBeInTheDocument();
  });

  it('should apply custom className', () => {
    const { container } = render(<Logo className="custom-class" />);
    expect(container.firstChild).toHaveClass('custom-class');
  });
});

describe('LogoIcon Component', () => {
  it('should render icon only', () => {
    render(<LogoIcon />);
    
    expect(screen.getByText('P')).toBeInTheDocument();
    expect(screen.queryByText('PMCELL')).not.toBeInTheDocument();
  });

  it('should render with different sizes', () => {
    const { rerender } = render(<LogoIcon size="sm" />);
    expect(screen.getByText('P')).toBeInTheDocument();

    rerender(<LogoIcon size="lg" />);
    expect(screen.getByText('P')).toBeInTheDocument();
  });
});

describe('LogoText Component', () => {
  it('should render text only', () => {
    render(<LogoText />);
    
    expect(screen.getByText('PMCELL')).toBeInTheDocument();
    expect(screen.getByText('Separação de Pedidos')).toBeInTheDocument();
    expect(screen.queryByText('P')).not.toBeInTheDocument();
  });

  it('should render with different variants', () => {
    const { rerender } = render(<LogoText variant="primary" />);
    expect(screen.getByText('PMCELL')).toBeInTheDocument();

    rerender(<LogoText variant="white" />);
    expect(screen.getByText('PMCELL')).toBeInTheDocument();
  });
});