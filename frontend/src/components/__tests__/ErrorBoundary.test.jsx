import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ErrorBoundary, { ErrorFallback, ComponentErrorBoundary } from '../ErrorBoundary';

// Component que vai gerar erro para testar
const ThrowError = ({ shouldThrow = false }) => {
  if (shouldThrow) {
    throw new Error('Test error');
  }
  return <div>No error</div>;
};

describe('ErrorBoundary Component', () => {
  // Suprimir console.error durante os testes
  const originalError = console.error;
  beforeAll(() => {
    console.error = vi.fn();
  });

  afterAll(() => {
    console.error = originalError;
  });

  it('should render children when there is no error', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={false} />
      </ErrorBoundary>
    );

    expect(screen.getByText('No error')).toBeInTheDocument();
  });

  it('should render error UI when there is an error', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByText('Ops! Algo deu errado')).toBeInTheDocument();
    expect(screen.getByText(/Ocorreu um erro inesperado/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /tentar novamente/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /recarregar página/i })).toBeInTheDocument();
  });

  it('should render PMCELL logo in error UI', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByText('PMCELL')).toBeInTheDocument();
    expect(screen.getByText('Separação de Pedidos')).toBeInTheDocument();
  });

  it('should show technical details in development mode', () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'development';

    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByText('Detalhes técnicos')).toBeInTheDocument();

    process.env.NODE_ENV = originalEnv;
  });

  it('should reset error state when reset button is clicked', async () => {
    const user = userEvent.setup();
    const { rerender } = render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByText('Ops! Algo deu errado')).toBeInTheDocument();

    const resetButton = screen.getByRole('button', { name: /tentar novamente/i });
    await user.click(resetButton);

    // Renderizar novamente sem erro
    rerender(
      <ErrorBoundary>
        <ThrowError shouldThrow={false} />
      </ErrorBoundary>
    );

    expect(screen.getByText('No error')).toBeInTheDocument();
  });

  it('should use custom fallback when provided', () => {
    const CustomFallback = () => <div>Custom error message</div>;

    render(
      <ErrorBoundary fallback={CustomFallback}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByText('Custom error message')).toBeInTheDocument();
    expect(screen.queryByText('Ops! Algo deu errado')).not.toBeInTheDocument();
  });
});

describe('ErrorFallback Component', () => {
  it('should render error fallback with default props', () => {
    const mockError = new Error('Test error');
    render(<ErrorFallback error={mockError} />);

    expect(screen.getByText('Erro')).toBeInTheDocument();
    expect(screen.getByText(/Ocorreu um erro ao carregar este componente/)).toBeInTheDocument();
  });

  it('should render with custom title and message', () => {
    const mockError = new Error('Test error');
    render(
      <ErrorFallback 
        error={mockError} 
        title="Custom Title"
        message="Custom error message"
      />
    );

    expect(screen.getByText('Custom Title')).toBeInTheDocument();
    expect(screen.getByText('Custom error message')).toBeInTheDocument();
  });

  it('should call onReset when reset button is clicked', async () => {
    const user = userEvent.setup();
    const mockOnReset = vi.fn();
    const mockError = new Error('Test error');

    render(<ErrorFallback error={mockError} onReset={mockOnReset} />);

    const resetButton = screen.getByRole('button', { name: /tentar novamente/i });
    await user.click(resetButton);

    expect(mockOnReset).toHaveBeenCalledOnce();
  });

  it('should show error details in development mode', () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'development';

    const mockError = new Error('Test error message');
    render(<ErrorFallback error={mockError} />);

    expect(screen.getByText('Detalhes do erro')).toBeInTheDocument();

    process.env.NODE_ENV = originalEnv;
  });
});

describe('ComponentErrorBoundary', () => {
  it('should render children when there is no error', () => {
    render(
      <ComponentErrorBoundary>
        <ThrowError shouldThrow={false} />
      </ComponentErrorBoundary>
    );

    expect(screen.getByText('No error')).toBeInTheDocument();
  });

  it('should render error boundary when there is an error', () => {
    render(
      <ComponentErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ComponentErrorBoundary>
    );

    // Should render the default ErrorBoundary UI
    expect(screen.getByText('Ops! Algo deu errado')).toBeInTheDocument();
  });
});