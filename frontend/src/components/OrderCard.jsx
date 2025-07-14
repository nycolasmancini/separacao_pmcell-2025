import { useState, memo } from 'react';
import { useAuthStore } from '../store/authStore';
import { useOrderPresenceStore } from '../store/orderPresenceStore';
import UserAvatar from './UserAvatar';

const OrderCard = memo(function OrderCard({ 
  order, 
  onCardClick, 
  activeUsers = [],
  className = '' 
}) {
  const [isHovered, setIsHovered] = useState(false);
  const { orderAccessUser, currentOrderId } = useAuthStore();
  const { getActiveUsersForOrder } = useOrderPresenceStore();
  
  // Obter todos os usuários ativos deste pedido do store
  const presenceUsers = getActiveUsersForOrder(order.id);
  
  // Verificar se o usuário atual está acessando este pedido
  const isCurrentlyAccessed = currentOrderId === order.id && orderAccessUser;
  
  // Combinar usuário atual (se estiver acessando) com outros usuários ativos
  const allActiveUsers = [];
  
  // Adicionar usuário atual se estiver acessando
  if (isCurrentlyAccessed && orderAccessUser) {
    allActiveUsers.push({
      ...orderAccessUser,
      isCurrent: true
    });
  }
  
  // Adicionar outros usuários ativos do store (evitando duplicatas)
  presenceUsers.forEach(user => {
    const isDuplicate = allActiveUsers.some(existingUser => existingUser.id === user.id);
    if (!isDuplicate) {
      allActiveUsers.push({
        ...user,
        isCurrent: false
      });
    }
  });
  
  // Também incluir activeUsers do props para compatibilidade (evitando duplicatas)
  if (activeUsers && activeUsers.length > 0) {
    activeUsers.forEach(user => {
      const isDuplicate = allActiveUsers.some(existingUser => existingUser.id === user.id);
      if (!isDuplicate) {
        allActiveUsers.push({
          ...user,
          isCurrent: false
        });
      }
    });
  }

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const getProgressColor = (progress) => {
    if (progress === 100) return 'bg-green-500';
    if (progress >= 50) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getStatusBadge = (status) => {
    const badges = {
      pending: { text: 'Pendente', color: 'bg-gray-100 text-gray-800' },
      in_progress: { text: 'Em Separação', color: 'bg-orange-100 text-orange-800' },
      completed: { text: 'Concluído', color: 'bg-green-100 text-green-800' },
      paused: { text: 'Pausado', color: 'bg-yellow-100 text-yellow-800' }
    };
    
    const badge = badges[status] || badges.pending;
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${badge.color}`}>
        {badge.text}
      </span>
    );
  };

  const getUserInitials = (name) => {
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .substring(0, 2)
      .toUpperCase();
  };

  const handleClick = () => {
    if (onCardClick) {
      onCardClick(order);
    }
  };

  return (
    <div
      className={`
        bg-white rounded-lg shadow-md border border-gray-200 p-6 
        cursor-pointer transition-all duration-200 hover:shadow-lg hover:border-orange-300
        ${isHovered ? 'scale-[1.02]' : ''}
        ${className}
      `}
      onClick={handleClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Header com número do orçamento e status */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold text-gray-900">
          Orçamento #{order.order_number}
        </h3>
        {getStatusBadge(order.status)}
      </div>

      {/* Cliente */}
      <div className="mb-3">
        <p className="text-sm text-gray-600 mb-1">Cliente</p>
        <p className="font-medium text-gray-900 truncate" title={order.client}>
          {order.client}
        </p>
      </div>

      {/* Vendedor */}
      <div className="mb-3">
        <p className="text-sm text-gray-600 mb-1">Vendedor</p>
        <p className="font-medium text-gray-900 truncate" title={order.seller}>
          {order.seller}
        </p>
      </div>

      {/* Informações do pedido */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p className="text-sm text-gray-600 mb-1">Itens</p>
          <p className="font-medium text-gray-900">{order.items_count}</p>
        </div>
        <div>
          <p className="text-sm text-gray-600 mb-1">Valor</p>
          <p className="font-medium text-gray-900">{formatCurrency(order.value)}</p>
        </div>
      </div>

      {/* Barra de progresso */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <p className="text-sm text-gray-600">Progresso</p>
          <p className="text-sm font-medium text-gray-900">{order.progress.toFixed(2)}%</p>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all duration-300 ${getProgressColor(order.progress)}`}
            style={{ width: `${order.progress}%` }}
          />
        </div>
      </div>

      {/* Usuários ativos - mostrar todos os usuários acessando */}
      {allActiveUsers.length > 0 && (
        <div className="flex items-center space-x-2">
          <p className="text-xs text-gray-600">
            Acessando ({allActiveUsers.length}):
          </p>
          <div className="flex -space-x-2">
            {allActiveUsers.slice(0, 4).map((user, index) => (
              <div key={user.id || index} className="relative">
                <UserAvatar
                  user={user}
                  size="sm"
                  showTooltip={true}
                  className={`${
                    user.isCurrent 
                      ? 'ring-2 ring-primary-500 ring-offset-2' 
                      : ''
                  }`}
                />
                {/* Indicador de usuário atual */}
                {user.isCurrent && (
                  <div className="absolute -top-1 -right-1 w-3 h-3 bg-primary-500 rounded-full border-2 border-white">
                    <div className="w-full h-full bg-primary-500 rounded-full animate-pulse"></div>
                  </div>
                )}
              </div>
            ))}
            {allActiveUsers.length > 4 && (
              <div className="w-8 h-8 rounded-full bg-gray-400 border-2 border-white flex items-center justify-center text-white text-xs font-medium">
                +{allActiveUsers.length - 4}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
});

export default OrderCard;