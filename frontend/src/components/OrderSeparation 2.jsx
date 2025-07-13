import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeftIcon, ClockIcon, UserIcon, CurrencyDollarIcon } from '@heroicons/react/24/outline';
import SeparationItemRow from './SeparationItemRow';
import SeparationProgress from './SeparationProgress';
import { useToast } from './ToastContainer';

export default function OrderSeparation() {
  const { orderId } = useParams();
  const navigate = useNavigate();
  const { showToast } = useToast();
  
  const [order, setOrder] = useState(null);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [updating, setUpdating] = useState(false);

  // Buscar dados do pedido
  useEffect(() => {
    if (!orderId) return;
    
    fetchOrderDetails();
  }, [orderId]);

  const fetchOrderDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`/api/orders/${orderId}/detail`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`Erro ao carregar pedido: ${response.status}`);
      }

      const data = await response.json();
      setOrder(data);
      
      // Ordenar itens alfabeticamente por nome do produto
      const sortedItems = [...data.items].sort((a, b) => 
        a.product_name.localeCompare(b.product_name, 'pt-BR', { sensitivity: 'base' })
      );
      setItems(sortedItems);
      
    } catch (err) {
      console.error('Error fetching order details:', err);
      setError(err.message);
      showToast('Erro ao carregar pedido', 'error');
    } finally {
      setLoading(false);
    }
  };

  const updateItem = async (itemId, updates) => {
    try {
      setUpdating(true);
      
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`/api/orders/${orderId}/items`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          updates: [{ item_id: itemId, ...updates }]
        })
      });

      if (!response.ok) {
        throw new Error(`Erro ao atualizar item: ${response.status}`);
      }

      const updatedOrder = await response.json();
      setOrder(updatedOrder);
      
      // Atualizar items mantendo ordem alfabética
      const sortedItems = [...updatedOrder.items].sort((a, b) => 
        a.product_name.localeCompare(b.product_name, 'pt-BR', { sensitivity: 'base' })
      );
      setItems(sortedItems);

      // Mostrar toast de sucesso
      if (updates.separated !== undefined) {
        showToast(
          updates.separated ? 'Item marcado como separado' : 'Item desmarcado',
          'success'
        );
      }
      if (updates.sent_to_purchase !== undefined) {
        showToast(
          updates.sent_to_purchase ? 'Item enviado para compras' : 'Item removido das compras',
          'success'
        );
      }
      
    } catch (err) {
      console.error('Error updating item:', err);
      showToast('Erro ao atualizar item', 'error');
    } finally {
      setUpdating(false);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const formatDate = (dateString) => {
    return new Intl.DateTimeFormat('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(new Date(dateString));
  };

  const handleGoBack = () => {
    navigate('/');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando pedido...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md mx-auto p-6">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Erro ao carregar pedido</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={handleGoBack}
            className="bg-orange-500 text-white px-4 py-2 rounded-lg hover:bg-orange-600 transition-colors"
          >
            Voltar ao Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (!order) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">Pedido não encontrado</p>
          <button
            onClick={handleGoBack}
            className="mt-4 bg-orange-500 text-white px-4 py-2 rounded-lg hover:bg-orange-600 transition-colors"
          >
            Voltar ao Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={handleGoBack}
                className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                title="Voltar ao Dashboard"
              >
                <ArrowLeftIcon className="h-5 w-5" />
              </button>
              <h1 className="text-xl font-semibold text-gray-900">
                Separação - Orçamento #{order.order_number}
              </h1>
            </div>
            <div className="text-sm text-gray-500">
              <ClockIcon className="inline h-4 w-4 mr-1" />
              {formatDate(order.created_at)}
            </div>
          </div>
        </div>
      </div>

      {/* Order Info */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Cliente */}
            <div className="flex items-start space-x-3">
              <UserIcon className="h-5 w-5 text-gray-400 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-gray-500">Cliente</p>
                <p className="text-lg font-semibold text-gray-900">{order.client_name}</p>
              </div>
            </div>

            {/* Vendedor */}
            <div className="flex items-start space-x-3">
              <UserIcon className="h-5 w-5 text-gray-400 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-gray-500">Vendedor</p>
                <p className="text-lg font-semibold text-gray-900">{order.seller_name}</p>
              </div>
            </div>

            {/* Valor */}
            <div className="flex items-start space-x-3">
              <CurrencyDollarIcon className="h-5 w-5 text-gray-400 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-gray-500">Valor Total</p>
                <p className="text-lg font-semibold text-gray-900">{formatCurrency(order.total_value)}</p>
              </div>
            </div>
          </div>

          {/* Progress */}
          <div className="mt-6">
            <SeparationProgress 
              progress={order.progress_percentage}
              totalItems={order.items_count}
              separatedItems={items.filter(item => item.separated).length}
            />
          </div>

          {/* Informações adicionais */}
          {(order.logistics_type || order.package_type || order.observations) && (
            <div className="mt-6 pt-6 border-t border-gray-200">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                {order.logistics_type && (
                  <div>
                    <span className="font-medium text-gray-500">Logística:</span>{' '}
                    <span className="text-gray-900">{order.logistics_type}</span>
                  </div>
                )}
                {order.package_type && (
                  <div>
                    <span className="font-medium text-gray-500">Embalagem:</span>{' '}
                    <span className="text-gray-900">{order.package_type}</span>
                  </div>
                )}
                {order.observations && (
                  <div className="md:col-span-3">
                    <span className="font-medium text-gray-500">Observações:</span>{' '}
                    <span className="text-gray-900">{order.observations}</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Items List */}
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">
              Itens do Pedido ({items.length})
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Clique nos itens para marcar como separados ou enviar para compras
            </p>
          </div>

          <div className="divide-y divide-gray-200">
            {items.map((item, index) => (
              <SeparationItemRow
                key={item.id}
                item={item}
                index={index}
                onUpdate={(updates) => updateItem(item.id, updates)}
                disabled={updating}
              />
            ))}
          </div>

          {items.length === 0 && (
            <div className="px-6 py-12 text-center">
              <p className="text-gray-500">Nenhum item encontrado neste pedido</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}