import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeftIcon, ClockIcon, UserIcon, CurrencyDollarIcon } from '@heroicons/react/24/outline';
import SeparationItemRow from './SeparationItemRow';
import SeparationProgress from './SeparationProgress';
import { useSeparation } from '../hooks/useSeparation';

export default function OrderSeparation() {
  const { orderId } = useParams();
  const navigate = useNavigate();
  
  const {
    order,
    items,
    loading,
    error,
    updating,
    wsConnected,
    updateItem,
    completeOrder
  } = useSeparation(orderId);


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

  // Função para verificar se o pedido pode ser completado
  const canCompleteOrder = () => {
    if (!order || !items) return false;
    if (order.status === 'completed') return false;
    
    // Calcular quantos itens foram processados (separados + não enviados)
    const separatedCount = items.filter(item => item.separated).length;
    const notSentCount = items.filter(item => item.not_sent).length;
    const processedCount = separatedCount + notSentCount;
    
    // Pode completar APENAS quando TODOS os itens foram processados (100%)
    return processedCount === order.items_count;
  };

  // Função para lidar com a conclusão do pedido
  const handleCompleteOrder = async () => {
    if (!canCompleteOrder()) return;
    
    const confirmed = window.confirm(
      'Tem certeza que deseja finalizar este pedido?\n\n' +
      'Esta ação marcará o pedido como concluído.'
    );
    
    if (confirmed) {
      try {
        await completeOrder();
        // Opcional: navegar de volta após alguns segundos
        setTimeout(() => {
          navigate('/');
        }, 2000);
      } catch (error) {
        // Erro já é tratado no hook useSeparation
        console.error('Error completing order:', error);
      }
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando pedido...</p>
          <p className="text-sm text-gray-500 mt-2">
            {wsConnected ? 'Conectado ao servidor' : 'Conectando com o servidor...'}
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    const isNetworkError = error.includes('Failed to fetch') || error.includes('500');
    const isNotFound = error.includes('404') || error.includes('não encontrado');
    
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="text-center max-w-md">
          <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-red-500 text-2xl">⚠️</span>
          </div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">
            {isNotFound ? 'Pedido não encontrado' : 'Erro ao carregar pedido'}
          </h2>
          <p className="text-gray-600 mb-4">{error}</p>
          
          {isNetworkError && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
              <p className="text-sm text-yellow-800">
                Verifique se o servidor está rodando e tente novamente.
              </p>
            </div>
          )}
          
          <div className="space-y-2">
            <button
              onClick={() => window.location.reload()}
              className="w-full bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors"
            >
              Tentar Novamente
            </button>
            <button
              onClick={handleGoBack}
              className="w-full bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-lg transition-colors"
            >
              Voltar ao Dashboard
            </button>
          </div>
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
            <div className="flex items-center space-x-4 text-sm text-gray-500">
              <div className="flex items-center space-x-1">
                <div className={`h-2 w-2 rounded-full ${wsConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <span>{wsConnected ? 'Conectado' : 'Desconectado'}</span>
              </div>
              <div className="flex items-center">
                <ClockIcon className="inline h-4 w-4 mr-1" />
                {formatDate(order.created_at)}
              </div>
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
            
            {/* Completion Button */}
            {canCompleteOrder() && (
              <div className="mt-4 flex justify-center">
                <button
                  onClick={handleCompleteOrder}
                  disabled={updating}
                  className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-6 py-2 rounded-lg font-medium transition-colors duration-200 flex items-center gap-2"
                >
                  {updating ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      Finalizando...
                    </>
                  ) : (
                    <>
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      Finalizar Pedido
                    </>
                  )}
                </button>
              </div>
            )}
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