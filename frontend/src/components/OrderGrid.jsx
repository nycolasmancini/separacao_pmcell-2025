import { useState, useEffect } from 'react';
import OrderCard from './OrderCard';

export default function OrderGrid({ 
  orders = [], 
  loading = false, 
  onOrderClick,
  activeUsers = {},
  className = ''
}) {
  const [filteredOrders, setFilteredOrders] = useState(orders);

  useEffect(() => {
    setFilteredOrders(orders);
  }, [orders]);

  if (loading) {
    return (
      <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 ${className}`}>
        {Array.from({ length: 8 }).map((_, index) => (
          <div
            key={index}
            className="bg-white rounded-lg shadow-md border border-gray-200 p-6 animate-pulse"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="h-6 bg-gray-300 rounded w-32"></div>
              <div className="h-6 bg-gray-300 rounded w-20"></div>
            </div>
            <div className="mb-3">
              <div className="h-4 bg-gray-300 rounded w-16 mb-1"></div>
              <div className="h-5 bg-gray-300 rounded w-full"></div>
            </div>
            <div className="mb-3">
              <div className="h-4 bg-gray-300 rounded w-20 mb-1"></div>
              <div className="h-5 bg-gray-300 rounded w-full"></div>
            </div>
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <div className="h-4 bg-gray-300 rounded w-12 mb-1"></div>
                <div className="h-5 bg-gray-300 rounded w-8"></div>
              </div>
              <div>
                <div className="h-4 bg-gray-300 rounded w-16 mb-1"></div>
                <div className="h-5 bg-gray-300 rounded w-20"></div>
              </div>
            </div>
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <div className="h-4 bg-gray-300 rounded w-16"></div>
                <div className="h-4 bg-gray-300 rounded w-10"></div>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="h-2 bg-gray-300 rounded-full w-1/2"></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (!orders || orders.length === 0) {
    return (
      <div className={`flex flex-col items-center justify-center py-12 ${className}`}>
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
            <svg 
              className="w-8 h-8 text-gray-400" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" 
              />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Nenhum pedido encontrado
          </h3>
          <p className="text-gray-500">
            Não há pedidos para exibir no momento.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 ${className}`}>
      {filteredOrders.map((order) => (
        <OrderCard
          key={order.id}
          order={order}
          onCardClick={onOrderClick}
          activeUsers={activeUsers[order.id] || []}
        />
      ))}
    </div>
  );
}