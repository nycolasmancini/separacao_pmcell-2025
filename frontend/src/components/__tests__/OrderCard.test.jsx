import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import OrderCard from '../OrderCard';

describe('OrderCard', () => {
  const mockOrder = {
    id: 1,
    order_number: '2025001',
    client: 'Cliente Teste Ltda',
    seller: 'João Silva',
    value: 1500.50,
    status: 'in_progress',
    items_count: 15,
    progress: 65
  };

  const mockActiveUsers = [
    { id: 1, name: 'Maria Santos' },
    { id: 2, name: 'Pedro Costa' }
  ];

  it('deve renderizar informações do pedido corretamente', () => {
    render(<OrderCard order={mockOrder} />);
    
    expect(screen.getByText('Orçamento #2025001')).toBeInTheDocument();
    expect(screen.getByText('Cliente Teste Ltda')).toBeInTheDocument();
    expect(screen.getByText('João Silva')).toBeInTheDocument();
    expect(screen.getByText('15')).toBeInTheDocument();
    expect(screen.getByText('R$ 1.500,50')).toBeInTheDocument();
    expect(screen.getByText('65.00%')).toBeInTheDocument();
  });

  it('deve exibir badge de status correto', () => {
    render(<OrderCard order={mockOrder} />);
    
    expect(screen.getByText('Em Separação')).toBeInTheDocument();
  });

  it('deve chamar onCardClick quando clicado', () => {
    const mockOnClick = vi.fn();
    render(<OrderCard order={mockOrder} onCardClick={mockOnClick} />);
    
    fireEvent.click(screen.getByText('Orçamento #2025001'));
    
    expect(mockOnClick).toHaveBeenCalledWith(mockOrder);
  });

  it('deve exibir usuários ativos', () => {
    render(<OrderCard order={mockOrder} activeUsers={mockActiveUsers} />);
    
    expect(screen.getByText('Acessando:')).toBeInTheDocument();
    expect(screen.getByText('MS')).toBeInTheDocument(); // Iniciais de Maria Santos
    expect(screen.getByText('PC')).toBeInTheDocument(); // Iniciais de Pedro Costa
  });

  it('deve exibir contador quando há mais de 3 usuários ativos', () => {
    const manyUsers = [
      { id: 1, name: 'User 1' },
      { id: 2, name: 'User 2' },
      { id: 3, name: 'User 3' },
      { id: 4, name: 'User 4' },
      { id: 5, name: 'User 5' }
    ];
    
    render(<OrderCard order={mockOrder} activeUsers={manyUsers} />);
    
    expect(screen.getByText('+2')).toBeInTheDocument();
  });

  it('deve exibir cor correta da barra de progresso', () => {
    const completedOrder = { ...mockOrder, progress: 100 };
    const { container } = render(<OrderCard order={completedOrder} />);
    
    const progressBar = container.querySelector('.bg-green-500');
    expect(progressBar).toBeInTheDocument();
  });

  it('deve aplicar hover effect', () => {
    const { container } = render(<OrderCard order={mockOrder} />);
    const card = container.firstChild;
    
    fireEvent.mouseEnter(card);
    expect(card).toHaveClass('scale-[1.02]');
    
    fireEvent.mouseLeave(card);
    expect(card).not.toHaveClass('scale-[1.02]');
  });

  it('deve truncar texto longo do cliente', () => {
    const longClientOrder = {
      ...mockOrder,
      client: 'Cliente com Nome Muito Longo Ltda EIRELI ME CNPJ 12.345.678/0001-90'
    };
    
    render(<OrderCard order={longClientOrder} />);
    
    const clientElement = screen.getByText(longClientOrder.client);
    expect(clientElement).toHaveClass('truncate');
  });
});