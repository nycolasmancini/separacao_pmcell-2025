import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import SeparationItemRow from '../SeparationItemRow';

describe('SeparationItemRow', () => {
  const mockItem = {
    id: 1,
    product_code: 'PROD001',
    product_reference: 'REF001',
    product_name: 'Produto de Teste',
    quantity: 5,
    unit_price: 100.50,
    total_price: 502.50,
    separated: false,
    sent_to_purchase: false,
    separated_at: null
  };

  const mockOnUpdate = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Renderização básica', () => {
    it('deve renderizar informações do produto corretamente', () => {
      render(
        <SeparationItemRow 
          item={mockItem} 
          index={0} 
          onUpdate={mockOnUpdate} 
        />
      );

      expect(screen.getByText('PROD001')).toBeInTheDocument();
      expect(screen.getByText('REF001')).toBeInTheDocument();
      expect(screen.getByText('Produto de Teste')).toBeInTheDocument();
      expect(screen.getByText('5')).toBeInTheDocument();
      expect(screen.getByText('R$ 100,50')).toBeInTheDocument();
      expect(screen.getByText('R$ 502,50')).toBeInTheDocument();
    });

    it('deve aplicar cor de fundo correta (zebra striping)', () => {
      const { container: container1 } = render(
        <SeparationItemRow 
          item={mockItem} 
          index={0} 
          onUpdate={mockOnUpdate} 
        />
      );

      const { container: container2 } = render(
        <SeparationItemRow 
          item={mockItem} 
          index={1} 
          onUpdate={mockOnUpdate} 
        />
      );

      const row1 = container1.firstChild;
      const row2 = container2.firstChild;

      expect(row1).toHaveClass('bg-white');
      expect(row2).toHaveClass('bg-gray-50');
    });

    it('deve exibir status pendente para item não separado', () => {
      render(
        <SeparationItemRow 
          item={mockItem} 
          index={0} 
          onUpdate={mockOnUpdate} 
        />
      );

      expect(screen.getByText('Pendente')).toBeInTheDocument();
    });

    it('deve exibir status separado para item separado', () => {
      const separatedItem = { 
        ...mockItem, 
        separated: true, 
        separated_at: '2025-07-12T10:30:00Z' 
      };

      render(
        <SeparationItemRow 
          item={separatedItem} 
          index={0} 
          onUpdate={mockOnUpdate} 
        />
      );

      expect(screen.getByText('Separado')).toBeInTheDocument();
      expect(screen.getByText(/Separado em/)).toBeInTheDocument();
    });

    it('deve exibir status em compras para item enviado para compras', () => {
      const purchaseItem = { 
        ...mockItem, 
        sent_to_purchase: true 
      };

      render(
        <SeparationItemRow 
          item={purchaseItem} 
          index={0} 
          onUpdate={mockOnUpdate} 
        />
      );

      expect(screen.getByText('Em Compras')).toBeInTheDocument();
    });
  });

  describe('Interações do checkbox', () => {
    it('deve permitir marcar item como separado', async () => {
      render(
        <SeparationItemRow 
          item={mockItem} 
          index={0} 
          onUpdate={mockOnUpdate} 
        />
      );

      const checkbox = screen.getByRole('button', { name: /marcar como separado/i });
      fireEvent.click(checkbox);

      await waitFor(() => {
        expect(mockOnUpdate).toHaveBeenCalledWith({ separated: true });
      });
    });

    it('deve permitir desmarcar item separado', async () => {
      const separatedItem = { ...mockItem, separated: true };
      
      render(
        <SeparationItemRow 
          item={separatedItem} 
          index={0} 
          onUpdate={mockOnUpdate} 
        />
      );

      const checkbox = screen.getByRole('button', { name: /desmarcar como separado/i });
      fireEvent.click(checkbox);

      await waitFor(() => {
        expect(mockOnUpdate).toHaveBeenCalledWith({ separated: false });
      });
    });

    it('deve desabilitar checkbox quando item está em compras', () => {
      const purchaseItem = { ...mockItem, sent_to_purchase: true };
      
      render(
        <SeparationItemRow 
          item={purchaseItem} 
          index={0} 
          onUpdate={mockOnUpdate} 
        />
      );

      const checkbox = screen.getByRole('button', { name: /item em compras/i });
      expect(checkbox).toBeDisabled();
    });

    it('deve desabilitar checkbox quando disabled prop é true', () => {
      render(
        <SeparationItemRow 
          item={mockItem} 
          index={0} 
          onUpdate={mockOnUpdate}
          disabled={true}
        />
      );

      const checkbox = screen.getByRole('button');
      expect(checkbox).toBeDisabled();
    });
  });

  describe('Menu de ações', () => {
    it('deve abrir menu ao clicar no botão de ações', () => {
      render(
        <SeparationItemRow 
          item={mockItem} 
          index={0} 
          onUpdate={mockOnUpdate} 
        />
      );

      const menuButton = screen.getByRole('button', { name: /mais ações/i });
      fireEvent.click(menuButton);

      expect(screen.getByText('Enviar para compras')).toBeInTheDocument();
    });

    it('deve enviar item para compras', async () => {
      render(
        <SeparationItemRow 
          item={mockItem} 
          index={0} 
          onUpdate={mockOnUpdate} 
        />
      );

      const menuButton = screen.getByRole('button', { name: /mais ações/i });
      fireEvent.click(menuButton);

      const sendToPurchaseButton = screen.getByText('Enviar para compras');
      fireEvent.click(sendToPurchaseButton);

      await waitFor(() => {
        expect(mockOnUpdate).toHaveBeenCalledWith({ sent_to_purchase: true });
      });
    });

    it('deve remover item das compras', async () => {
      const purchaseItem = { ...mockItem, sent_to_purchase: true };
      
      render(
        <SeparationItemRow 
          item={purchaseItem} 
          index={0} 
          onUpdate={mockOnUpdate} 
        />
      );

      const menuButton = screen.getByRole('button', { name: /mais ações/i });
      fireEvent.click(menuButton);

      const removeFromPurchaseButton = screen.getByText('Remover das compras');
      fireEvent.click(removeFromPurchaseButton);

      await waitFor(() => {
        expect(mockOnUpdate).toHaveBeenCalledWith({ sent_to_purchase: false });
      });
    });

    it('deve fechar menu ao clicar fora', () => {
      const { container } = render(
        <SeparationItemRow 
          item={mockItem} 
          index={0} 
          onUpdate={mockOnUpdate} 
        />
      );

      const menuButton = screen.getByRole('button', { name: /mais ações/i });
      fireEvent.click(menuButton);

      expect(screen.getByText('Enviar para compras')).toBeInTheDocument();

      // Simular mouse leave no container
      fireEvent.mouseLeave(container.firstChild);

      expect(screen.queryByText('Enviar para compras')).not.toBeInTheDocument();
    });
  });

  describe('Estados de loading', () => {
    it('deve exibir spinner quando atualizando', () => {
      render(
        <SeparationItemRow 
          item={mockItem} 
          index={0} 
          onUpdate={() => Promise.resolve()} 
        />
      );

      const checkbox = screen.getByRole('button', { name: /marcar como separado/i });
      fireEvent.click(checkbox);

      // O spinner deve aparecer durante a atualização
      expect(screen.getByRole('button')).toContainHTML('animate-spin');
    });

    it('deve desabilitar interações durante atualização', () => {
      render(
        <SeparationItemRow 
          item={mockItem} 
          index={0} 
          onUpdate={mockOnUpdate}
          disabled={true}
        />
      );

      const menuButton = screen.getByRole('button', { name: /mais ações/i });
      expect(menuButton).toBeDisabled();
    });
  });

  describe('Formatação de dados', () => {
    it('deve formatar preços em real brasileiro', () => {
      render(
        <SeparationItemRow 
          item={mockItem} 
          index={0} 
          onUpdate={mockOnUpdate} 
        />
      );

      expect(screen.getByText('R$ 100,50')).toBeInTheDocument();
      expect(screen.getByText('R$ 502,50')).toBeInTheDocument();
    });

    it('deve formatar data de separação corretamente', () => {
      const separatedItem = { 
        ...mockItem, 
        separated: true, 
        separated_at: '2025-07-12T14:30:00Z' 
      };

      render(
        <SeparationItemRow 
          item={separatedItem} 
          index={0} 
          onUpdate={mockOnUpdate} 
        />
      );

      // Verifica se a data está formatada como DD/MM HH:MM
      expect(screen.getByText(/Separado em \d{2}\/\d{2} \d{2}:\d{2}/)).toBeInTheDocument();
    });

    it('deve truncar textos longos', () => {
      const longNameItem = {
        ...mockItem,
        product_name: 'Nome de Produto Muito Longo que Deve Ser Truncado Para Não Quebrar Layout'
      };

      render(
        <SeparationItemRow 
          item={longNameItem} 
          index={0} 
          onUpdate={mockOnUpdate} 
        />
      );

      const productName = screen.getByTitle(longNameItem.product_name);
      expect(productName).toBeInTheDocument();
    });
  });

  describe('Acessibilidade', () => {
    it('deve ter títulos apropriados nos botões', () => {
      render(
        <SeparationItemRow 
          item={mockItem} 
          index={0} 
          onUpdate={mockOnUpdate} 
        />
      );

      expect(screen.getByTitle('Marcar como separado')).toBeInTheDocument();
      expect(screen.getByTitle('Mais ações')).toBeInTheDocument();
    });

    it('deve ter títulos apropriados para itens em diferentes estados', () => {
      const purchaseItem = { ...mockItem, sent_to_purchase: true };
      
      render(
        <SeparationItemRow 
          item={purchaseItem} 
          index={0} 
          onUpdate={mockOnUpdate} 
        />
      );

      expect(screen.getByTitle('Item em compras')).toBeInTheDocument();
    });
  });

  describe('Responsividade', () => {
    it('deve aplicar classes responsivas corretas', () => {
      const { container } = render(
        <SeparationItemRow 
          item={mockItem} 
          index={0} 
          onUpdate={mockOnUpdate} 
        />
      );

      const gridContainer = container.querySelector('.grid');
      expect(gridContainer).toHaveClass('grid-cols-1', 'md:grid-cols-6');
    });
  });
});