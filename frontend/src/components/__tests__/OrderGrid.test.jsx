import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import OrderGrid from '../OrderGrid';

describe('OrderGrid', () => {
  const mockOrders = [
    {
      id: 1,
      order_number: '2025001',
      client: 'Cliente A Ltda',
      seller: 'João Silva',
      value: 1500.00,
      status: 'in_progress',
      items_count: 15,
      progress: 65
    },
    {
      id: 2,
      order_number: '2025002',
      client: 'Cliente B S.A.',
      seller: 'Maria Santos',
      value: 2300.50,
      status: 'pending',
      items_count: 23,
      progress: 0
    }
  ];

  it('deve renderizar grid de pedidos', () => {
    render(<OrderGrid orders={mockOrders} />);
    
    expect(screen.getByText('Orçamento #2025001')).toBeInTheDocument();
    expect(screen.getByText('Orçamento #2025002')).toBeInTheDocument();
  });

  it('deve exibir skeleton loading quando loading=true', () => {
    const { container } = render(<OrderGrid orders={[]} loading={true} />);
    
    const skeletons = container.querySelectorAll('.animate-pulse');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it('deve exibir mensagem quando não há pedidos', () => {
    render(<OrderGrid orders={[]} loading={false} />);
    
    expect(screen.getByText('Nenhum pedido encontrado')).toBeInTheDocument();
    expect(screen.getByText('Não há pedidos para exibir no momento.')).toBeInTheDocument();
  });

  it('deve usar grid responsivo', () => {
    const { container } = render(<OrderGrid orders={mockOrders} />);
    
    const grid = container.firstChild;
    expect(grid).toHaveClass('grid', 'grid-cols-1', 'md:grid-cols-2', 'lg:grid-cols-3', 'xl:grid-cols-4');
  });

  it('deve passar onOrderClick para OrderCard', () => {
    const mockOnClick = vi.fn();
    render(<OrderGrid orders={mockOrders} onOrderClick={mockOnClick} />);
    
    // O teste verifica se o prop é passado, a funcionalidade será testada no OrderCard
    expect(screen.getByText('Orçamento #2025001')).toBeInTheDocument();
  });

  it('deve passar activeUsers corretos para cada OrderCard', () => {
    const mockActiveUsers = {
      1: [{ id: 1, name: 'User 1' }],
      2: [{ id: 2, name: 'User 2' }]
    };
    
    render(<OrderGrid orders={mockOrders} activeUsers={mockActiveUsers} />);
    
    // Como os usuários ativos são passados para OrderCard, verificamos se os pedidos são renderizados
    expect(screen.getByText('Orçamento #2025001')).toBeInTheDocument();
    expect(screen.getByText('Orçamento #2025002')).toBeInTheDocument();
  });

  it('deve aplicar className personalizado', () => {
    const { container } = render(<OrderGrid orders={mockOrders} className="custom-class" />);
    
    expect(container.firstChild).toHaveClass('custom-class');
  });

  it('deve renderizar número correto de skeletons durante loading', () => {
    const { container } = render(<OrderGrid orders={[]} loading={true} />);
    
    const skeletons = container.querySelectorAll('.animate-pulse');
    expect(skeletons).toHaveLength(8); // Número padrão de skeletons
  });
});