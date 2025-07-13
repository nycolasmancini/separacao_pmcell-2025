import { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useAuthStore } from '../store/authStore';

export default function PurchaseItems() {
  const [purchaseItems, setPurchaseItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [groupBy, setGroupBy] = useState('order'); // 'order' or 'none'
  const { user } = useAuthStore();

  useEffect(() => {
    fetchPurchaseItems();
  }, []);

  const fetchPurchaseItems = async () => {
    try {
      setLoading(true);
      const response = await api.get('/orders/purchase-items');
      setPurchaseItems(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching purchase items:', err);
      setError('Erro ao carregar itens em compras');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const groupedItems = groupBy === 'order' 
    ? purchaseItems.reduce((groups, item) => {
        const key = item.order_number;
        if (!groups[key]) {
          groups[key] = {
            order_number: item.order_number,
            client_name: item.client_name,
            order_id: item.order_id,
            items: []
          };
        }
        groups[key].items.push(item);
        return groups;
      }, {})
    : { 'all': { items: purchaseItems } };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-48 mb-6"></div>
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-20 bg-white rounded-lg shadow"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <h3 className="text-red-800 font-medium">Erro</h3>
            <p className="text-red-600 mt-1">{error}</p>
            <button 
              onClick={fetchPurchaseItems}
              className="mt-3 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
            >
              Tentar novamente
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Itens em Compras</h1>
            <p className="text-gray-600 mt-1">
              {purchaseItems.length} {purchaseItems.length === 1 ? 'item' : 'itens'} aguardando compra
            </p>
          </div>

          {/* Controls */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium text-gray-700">Agrupar por:</label>
              <select
                value={groupBy}
                onChange={(e) => setGroupBy(e.target.value)}
                className="block px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              >
                <option value="order">Pedido</option>
                <option value="none">Sem agrupamento</option>
              </select>
            </div>
            
            <button
              onClick={fetchPurchaseItems}
              className="px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 transition-colors"
            >
              Atualizar
            </button>
          </div>
        </div>

        {/* Content */}
        {purchaseItems.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <div className="text-gray-400 text-6xl mb-4">📦</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Nenhum item em compras</h3>
            <p className="text-gray-600">Todos os itens foram processados ou não há itens pendentes.</p>
          </div>
        ) : (
          <div className="space-y-6">
            {Object.entries(groupedItems).map(([groupKey, group]) => (
              <div key={groupKey} className="bg-white rounded-lg shadow overflow-hidden">
                {groupBy === 'order' && (
                  <div className="bg-orange-50 px-6 py-4 border-b border-orange-100">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">
                          Orçamento #{group.order_number}
                        </h3>
                        <p className="text-gray-600">{group.client_name}</p>
                      </div>
                      <div className="text-sm text-gray-600">
                        {group.items.length} {group.items.length === 1 ? 'item' : 'itens'}
                      </div>
                    </div>
                  </div>
                )}

                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Produto
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Código
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Quantidade
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Solicitado em
                        </th>
                        {groupBy === 'none' && (
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Pedido
                          </th>
                        )}
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {group.items.map((item, index) => (
                        <tr key={item.id} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-medium text-gray-900">
                              {item.product_name}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                            {item.product_code}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {item.quantity}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                            {formatDate(item.requested_at)}
                          </td>
                          {groupBy === 'none' && (
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                              <div>
                                <div className="font-medium">#{item.order_number}</div>
                                <div className="text-gray-500">{item.client_name}</div>
                              </div>
                            </td>
                          )}
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                              Pendente
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}