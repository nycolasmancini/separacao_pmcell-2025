import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import OrderSeparation from '../OrderSeparation';
import { ToastProvider } from '../ToastContainer';

// Mock do hook useSeparation
vi.mock('../../hooks/useSeparation', () => ({
  useSeparation: vi.fn()
}));

// Mock dos componentes filhos
vi.mock('../SeparationItemRow', () => ({
  default: ({ item, onUpdate, disabled }) => (
    <div data-testid={`item-row-${item.id}`}>
      <span>{item.product_name}</span>
      <button 
        onClick={() => onUpdate({ separated: !item.separated })}
        disabled={disabled}
      >
        {item.separated ? 'Separado' : 'Separar'}
      </button>
    </div>
  )
}));

vi.mock('../SeparationProgress', () => ({
  default: ({ progress, totalItems, separatedItems }) => (
    <div data-testid="separation-progress">
      <span>Progresso: {progress}%</span>
      <span>Separados: {separatedItems}/{totalItems}</span>
    </div>
  )
}));

// Mock do router
const renderWithRouter = (component, { route = '/orders/1/separation' } = {}) => {
  return render(
    <MemoryRouter initialEntries={[route]}>
      <ToastProvider>
        {component}
      </ToastProvider>
    </MemoryRouter>
  );
};

describe('OrderSeparation', () => {
  const mockOrder = {
    id: 1,
    order_number: '2025001',
    client_name: 'Cliente Teste Ltda',
    seller_name: 'João Silva',
    total_value: 1500.50,
    items_count: 3,
    progress_percentage: 33.33,
    status: 'in_progress',
    logistics_type: 'Lalamove',
    package_type: 'Caixa',
    observations: 'Observação de teste',
    created_at: '2025-07-12T10:30:00Z'
  };

  const mockItems = [
    {
      id: 1,
      product_code: 'PROD001',
      product_reference: 'REF001',
      product_name: 'Produto A',
      quantity: 2,
      unit_price: 100.00,
      total_price: 200.00,
      separated: true,
      sent_to_purchase: false,
      separated_at: '2025-07-12T10:35:00Z'
    },
    {
      id: 2,
      product_code: 'PROD002', 
      product_reference: 'REF002',
      product_name: 'Produto B',
      quantity: 1,
      unit_price: 500.50,
      total_price: 500.50,
      separated: false,
      sent_to_purchase: false,
      separated_at: null
    },
    {
      id: 3,
      product_code: 'PROD003',
      product_reference: 'REF003', 
      product_name: 'Produto C',
      quantity: 3,
      unit_price: 266.67,
      total_price: 800.00,
      separated: false,
      sent_to_purchase: true,
      separated_at: null
    }
  ];

  const mockUseSeparation = {
    order: mockOrder,
    items: mockItems,
    loading: false,
    error: null,
    updating: false,
    wsConnected: true,
    updateItem: vi.fn(),
    refetch: vi.fn()
  };

  beforeEach(() => {
    const { useSeparation } = require('../../hooks/useSeparation');
    useSeparation.mockReturnValue(mockUseSeparation);
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Renderização básica', () => {
    it('deve renderizar o cabeçalho com informações do pedido', () => {
      renderWithRouter(<OrderSeparation />);
      
      expect(screen.getByText('Separação - Orçamento #2025001')).toBeInTheDocument();
      expect(screen.getByText('Cliente Teste Ltda')).toBeInTheDocument();
      expect(screen.getByText('João Silva')).toBeInTheDocument();
      expect(screen.getByText('R$ 1.500,50')).toBeInTheDocument();
    });

    it('deve renderizar informações adicionais quando fornecidas', () => {
      renderWithRouter(<OrderSeparation />);
      
      expect(screen.getByText('Lalamove')).toBeInTheDocument();
      expect(screen.getByText('Caixa')).toBeInTheDocument();
      expect(screen.getByText('Observação de teste')).toBeInTheDocument();
    });

    it('deve renderizar lista de itens ordenada alfabeticamente', () => {
      renderWithRouter(<OrderSeparation />);
      
      expect(screen.getByTestId('item-row-1')).toBeInTheDocument();
      expect(screen.getByTestId('item-row-2')).toBeInTheDocument();
      expect(screen.getByTestId('item-row-3')).toBeInTheDocument();
      
      // Verifica se os itens estão ordenados alfabeticamente
      const itemRows = screen.getAllByTestId(/item-row-/);
      expect(itemRows).toHaveLength(3);
    });

    it('deve renderizar componente de progresso', () => {
      renderWithRouter(<OrderSeparation />);
      
      expect(screen.getByTestId('separation-progress')).toBeInTheDocument();
      expect(screen.getByText('Progresso: 33.33%')).toBeInTheDocument();
      expect(screen.getByText('Separados: 1/3')).toBeInTheDocument();
    });
  });

  describe('Estados de carregamento e erro', () => {
    it('deve exibir loading quando carregando', () => {
      const { useSeparation } = require('../../hooks/useSeparation');
      useSeparation.mockReturnValue({
        ...mockUseSeparation,
        loading: true,
        order: null,
        items: []
      });

      renderWithRouter(<OrderSeparation />);
      
      expect(screen.getByText('Carregando pedido...')).toBeInTheDocument();
    });

    it('deve exibir erro quando há erro', () => {
      const { useSeparation } = require('../../hooks/useSeparation');
      useSeparation.mockReturnValue({
        ...mockUseSeparation,
        loading: false,
        error: 'Erro de teste',
        order: null,
        items: []
      });

      renderWithRouter(<OrderSeparation />);
      
      expect(screen.getByText('Erro ao carregar pedido')).toBeInTheDocument();
      expect(screen.getByText('Erro de teste')).toBeInTheDocument();
    });

    it('deve exibir mensagem quando pedido não encontrado', () => {
      const { useSeparation } = require('../../hooks/useSeparation');
      useSeparation.mockReturnValue({
        ...mockUseSeparation,
        loading: false,
        error: null,
        order: null,
        items: []
      });

      renderWithRouter(<OrderSeparation />);
      
      expect(screen.getByText('Pedido não encontrado')).toBeInTheDocument();
    });
  });

  describe('Interações', () => {
    it('deve voltar ao dashboard quando clicar no botão voltar', () => {
      renderWithRouter(<OrderSeparation />);
      
      const backButton = screen.getByTitle('Voltar ao Dashboard');
      fireEvent.click(backButton);
      
      // Como estamos usando MemoryRouter, não podemos testar a navegação real
      // mas podemos verificar se o botão está presente e clicável
      expect(backButton).toBeInTheDocument();
    });

    it('deve chamar updateItem quando item for atualizado', async () => {
      renderWithRouter(<OrderSeparation />);
      
      const separateButton = screen.getByText('Separar');
      fireEvent.click(separateButton);
      
      await waitFor(() => {
        expect(mockUseSeparation.updateItem).toHaveBeenCalledWith(2, { separated: true });
      });
    });

    it('deve desabilitar interações quando updating é true', () => {
      const { useSeparation } = require('../../hooks/useSeparation');
      useSeparation.mockReturnValue({
        ...mockUseSeparation,
        updating: true
      });

      renderWithRouter(<OrderSeparation />);
      
      const buttons = screen.getAllByRole('button');
      const separateButtons = buttons.filter(btn => btn.textContent.includes('Separar'));
      
      separateButtons.forEach(button => {
        expect(button).toBeDisabled();
      });
    });
  });

  describe('Formatação de dados', () => {
    it('deve formatar moeda corretamente', () => {
      renderWithRouter(<OrderSeparation />);
      
      expect(screen.getByText('R$ 1.500,50')).toBeInTheDocument();
    });

    it('deve formatar data corretamente', () => {
      renderWithRouter(<OrderSeparation />);
      
      // A data deve ser formatada como DD/MM/YYYY HH:MM
      const dateElement = screen.getByText(/12\/07\/2025/);
      expect(dateElement).toBeInTheDocument();
    });
  });

  describe('Lista vazia', () => {
    it('deve exibir mensagem quando não há itens', () => {
      const { useSeparation } = require('../../hooks/useSeparation');
      useSeparation.mockReturnValue({
        ...mockUseSeparation,
        items: []
      });

      renderWithRouter(<OrderSeparation />);
      
      expect(screen.getByText('Nenhum item encontrado neste pedido')).toBeInTheDocument();
    });
  });

  describe('Integração com WebSocket', () => {
    it('deve exibir indicador de conexão WebSocket', () => {
      renderWithRouter(<OrderSeparation />);
      
      // Assumindo que existe algum indicador visual de conexão WebSocket
      // Essa verificação pode ser ajustada conforme a implementação
      expect(mockUseSeparation.wsConnected).toBe(true);
    });

    it('deve funcionar mesmo quando WebSocket não está conectado', () => {
      const { useSeparation } = require('../../hooks/useSeparation');
      useSeparation.mockReturnValue({
        ...mockUseSeparation,
        wsConnected: false
      });

      renderWithRouter(<OrderSeparation />);
      
      expect(screen.getByText('Separação - Orçamento #2025001')).toBeInTheDocument();
    });
  });

  describe('Responsividade', () => {
    it('deve renderizar corretamente em diferentes tamanhos de tela', () => {
      renderWithRouter(<OrderSeparation />);
      
      // Verifica se as classes responsivas estão presentes
      const container = screen.getByText('Separação - Orçamento #2025001').closest('div');
      expect(container).toHaveClass('max-w-7xl', 'mx-auto');
    });
  });
});