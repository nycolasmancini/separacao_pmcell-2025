import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import StatusFilter from '../StatusFilter';

describe('StatusFilter', () => {
  const mockOrderCounts = {
    pending: 5,
    in_progress: 3,
    completed: 12,
    paused: 1
  };

  it('deve renderizar todos os filtros', () => {
    render(<StatusFilter orderCounts={mockOrderCounts} />);
    
    expect(screen.getByText('Todos')).toBeInTheDocument();
    expect(screen.getByText('Pendentes')).toBeInTheDocument();
    expect(screen.getByText('Em Separação')).toBeInTheDocument();
    expect(screen.getByText('Concluídos')).toBeInTheDocument();
    expect(screen.getByText('Pausados')).toBeInTheDocument();
  });

  it('deve exibir contadores corretos', () => {
    render(<StatusFilter orderCounts={mockOrderCounts} />);
    
    expect(screen.getByText('21')).toBeInTheDocument(); // Total (5+3+12+1)
    expect(screen.getByText('5')).toBeInTheDocument(); // Pendentes
    expect(screen.getByText('3')).toBeInTheDocument(); // Em Separação
    expect(screen.getByText('12')).toBeInTheDocument(); // Concluídos
    expect(screen.getByText('1')).toBeInTheDocument(); // Pausados
  });

  it('deve destacar filtro ativo', () => {
    render(<StatusFilter currentFilter="in_progress" orderCounts={mockOrderCounts} />);
    
    const activeButton = screen.getByText('Em Separação').closest('button');
    expect(activeButton).toHaveClass('bg-orange-600', 'text-white');
  });

  it('deve chamar onFilterChange quando filtro é clicado', () => {
    const mockOnChange = vi.fn();
    render(<StatusFilter onFilterChange={mockOnChange} orderCounts={mockOrderCounts} />);
    
    fireEvent.click(screen.getByText('Pendentes'));
    
    expect(mockOnChange).toHaveBeenCalledWith('pending');
  });

  it('deve aplicar cores corretas para cada filtro', () => {
    render(<StatusFilter orderCounts={mockOrderCounts} />);
    
    const completedButton = screen.getByText('Concluídos').closest('button');
    expect(completedButton).toHaveClass('bg-green-100', 'text-green-800');
    
    const progressButton = screen.getByText('Em Separação').closest('button');
    expect(progressButton).toHaveClass('bg-orange-100', 'text-orange-800');
  });

  it('deve ter hover effects', () => {
    render(<StatusFilter orderCounts={mockOrderCounts} />);
    
    const button = screen.getByText('Todos').closest('button');
    expect(button).toHaveClass('hover:scale-105');
  });

  it('deve ter focus styles', () => {
    render(<StatusFilter orderCounts={mockOrderCounts} />);
    
    const button = screen.getByText('Todos').closest('button');
    expect(button).toHaveClass('focus:outline-none', 'focus:ring-2', 'focus:ring-orange-500');
  });

  it('deve não exibir contador quando é 0', () => {
    const emptyOrderCounts = {
      pending: 0,
      in_progress: 0,
      completed: 0,
      paused: 0
    };
    
    render(<StatusFilter orderCounts={emptyOrderCounts} />);
    
    // O contador '0' não deve ser exibido
    expect(screen.queryByText('0')).not.toBeInTheDocument();
  });

  it('deve calcular total corretamente para filtro "all"', () => {
    render(<StatusFilter orderCounts={mockOrderCounts} />);
    
    const totalButton = screen.getByText('Todos').closest('button');
    expect(totalButton).toHaveTextContent('21'); // 5+3+12+1
  });

  it('deve aplicar className personalizado', () => {
    const { container } = render(
      <StatusFilter orderCounts={mockOrderCounts} className="custom-class" />
    );
    
    expect(container.firstChild).toHaveClass('custom-class');
  });
});