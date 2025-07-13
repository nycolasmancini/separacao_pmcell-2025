import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Toast from '../Toast';

describe('Toast', () => {
  it('deve renderizar mensagem corretamente', () => {
    render(<Toast message="Teste de mensagem" />);
    
    expect(screen.getByText('Teste de mensagem')).toBeInTheDocument();
  });

  it('deve aplicar estilos corretos para cada tipo', () => {
    const { rerender, container } = render(<Toast message="Success" type="success" />);
    expect(container.firstChild).toHaveClass('bg-green-50', 'text-green-800');
    
    rerender(<Toast message="Error" type="error" />);
    expect(container.firstChild).toHaveClass('bg-red-50', 'text-red-800');
    
    rerender(<Toast message="Warning" type="warning" />);
    expect(container.firstChild).toHaveClass('bg-yellow-50', 'text-yellow-800');
    
    rerender(<Toast message="Info" type="info" />);
    expect(container.firstChild).toHaveClass('bg-blue-50', 'text-blue-800');
  });

  it('deve exibir ícone correto para cada tipo', () => {
    const { rerender, container } = render(<Toast message="Test" type="success" />);
    expect(container.querySelector('.text-green-400')).toBeInTheDocument();
    
    rerender(<Toast message="Test" type="error" />);
    expect(container.querySelector('.text-red-400')).toBeInTheDocument();
    
    rerender(<Toast message="Test" type="warning" />);
    expect(container.querySelector('.text-yellow-400')).toBeInTheDocument();
    
    rerender(<Toast message="Test" type="info" />);
    expect(container.querySelector('.text-blue-400')).toBeInTheDocument();
  });

  it('deve fechar automaticamente após duration', async () => {
    const mockOnClose = vi.fn();
    render(<Toast message="Auto close" duration={100} onClose={mockOnClose} />);
    
    await waitFor(() => {
      expect(mockOnClose).toHaveBeenCalled();
    }, { timeout: 500 });
  });

  it('deve fechar quando botão close é clicado', () => {
    const mockOnClose = vi.fn();
    const { container } = render(<Toast message="Manual close" onClose={mockOnClose} />);
    
    const closeButton = screen.getByRole('button');
    fireEvent.click(closeButton);
    
    // Deve iniciar animação de saída
    expect(container.firstChild).toHaveClass('translate-x-full', 'opacity-0');
  });

  it('não deve fechar automaticamente quando duration é 0', async () => {
    const mockOnClose = vi.fn();
    render(<Toast message="No auto close" duration={0} onClose={mockOnClose} />);
    
    // Aguarda um tempo para garantir que não foi chamado
    await new Promise(resolve => setTimeout(resolve, 200));
    
    expect(mockOnClose).not.toHaveBeenCalled();
  });

  it('deve aplicar className personalizado', () => {
    const { container } = render(<Toast message="Test" className="custom-class" />);
    
    expect(container.firstChild).toHaveClass('custom-class');
  });

  it('deve ter animação de entrada', () => {
    const { container } = render(<Toast message="Animated" />);
    
    const toast = container.firstChild;
    expect(toast).toHaveClass('translate-x-0', 'opacity-100');
  });

  it('deve remover do DOM após animação de saída', async () => {
    const mockOnClose = vi.fn();
    const { container } = render(<Toast message="Remove test" onClose={mockOnClose} />);
    
    const closeButton = screen.getByRole('button');
    fireEvent.click(closeButton);
    
    // Aguarda animação completa (300ms)
    await waitFor(() => {
      expect(container.firstChild).toBeNull();
    }, { timeout: 500 });
  });

  it('deve usar tipo info como padrão', () => {
    const { container } = render(<Toast message="Default type" />);
    
    expect(container.firstChild).toHaveClass('bg-blue-50', 'text-blue-800');
  });
});