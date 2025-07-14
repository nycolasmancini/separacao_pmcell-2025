import { useState } from 'react';
import { 
  CheckCircleIcon, 
  XCircleIcon,
  ShoppingCartIcon,
  EllipsisVerticalIcon,
  ClockIcon
} from '@heroicons/react/24/outline';

export default function SeparationItemRow({ item, index, onUpdate, disabled = false }) {
  const [showMenu, setShowMenu] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);

  const handleSeparatedToggle = async () => {
    if (disabled || isUpdating) return;
    
    setIsUpdating(true);
    try {
      // Se o item está sendo marcado como separado E está em compras,
      // remove das compras e marca como separado
      if (!item.separated && item.sent_to_purchase) {
        await onUpdate({ separated: true, sent_to_purchase: false });
      } else {
        await onUpdate({ separated: !item.separated });
      }
    } catch (error) {
      console.error('Error toggling separated status:', error);
      // The error is already handled by the parent component and shows a toast
      // Just ensure we reset the updating state
    } finally {
      setIsUpdating(false);
    }
  };

  const handleSendToPurchase = async () => {
    if (disabled || isUpdating) return;
    
    setIsUpdating(true);
    setShowMenu(false);
    try {
      await onUpdate({ sent_to_purchase: true });
    } catch (error) {
      console.error('Error sending to purchase:', error);
      // Error is handled by parent component
    } finally {
      setIsUpdating(false);
    }
  };

  const handleMarkNotSent = async () => {
    if (disabled || isUpdating) return;
    
    setIsUpdating(true);
    setShowMenu(false);
    try {
      await onUpdate({ sent_to_purchase: false });
    } catch (error) {
      console.error('Error removing from purchase:', error);
      // Error is handled by parent component
    } finally {
      setIsUpdating(false);
    }
  };

  const handleMarkAsNotSent = async () => {
    if (disabled || isUpdating) return;
    
    setIsUpdating(true);
    setShowMenu(false);
    try {
      await onUpdate({ not_sent: true });
    } catch (error) {
      console.error('Error marking as not sent:', error);
      // Error is handled by parent component
    } finally {
      setIsUpdating(false);
    }
  };


  const formatDateTime = (dateString) => {
    if (!dateString) return null;
    return new Intl.DateTimeFormat('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    }).format(new Date(dateString));
  };

  // Background color and styling based on item state
  const getItemStyling = () => {
    if (item.sent_to_purchase) return {
      bg: 'bg-blue-50',
      textColor: ''
    };
    if (item.separated) return {
      bg: 'bg-green-50',
      textColor: ''
    };
    if (item.not_sent) return {
      bg: 'bg-red-50 border-l-4 border-red-500',
      textColor: 'text-red-700'
    };
    return {
      bg: index % 2 === 0 ? 'bg-white' : 'bg-gray-50',
      textColor: ''
    };
  };
  
  const itemStyling = getItemStyling();
  
  // Estado visual do item
  const getItemStatus = () => {
    if (item.sent_to_purchase) {
      return {
        badge: 'Em Compras',
        badgeColor: 'bg-blue-100 text-blue-800',
        icon: <ShoppingCartIcon className="h-4 w-4" />,
        iconColor: 'text-blue-500'
      };
    }
    if (item.separated) {
      return {
        badge: 'Separado',
        badgeColor: 'bg-green-100 text-green-800',
        icon: <CheckCircleIcon className="h-4 w-4" />,
        iconColor: 'text-green-500'
      };
    }
    if (item.not_sent) {
      return {
        badge: 'Não Enviado',
        badgeColor: 'bg-red-600 text-white border border-red-700',
        icon: <XCircleIcon className="h-4 w-4" />,
        iconColor: 'text-red-600'
      };
    }
    return {
      badge: 'Pendente',
      badgeColor: 'bg-gray-100 text-gray-800',
      icon: <ClockIcon className="h-4 w-4" />,
      iconColor: 'text-gray-400'
    };
  };

  const status = getItemStatus();

  return (
    <div 
      className={`${itemStyling.bg} px-6 py-4 hover:bg-orange-50 transition-colors relative`}
      onMouseLeave={() => setShowMenu(false)}
    >
      <div className="flex items-center space-x-4">
        {/* Checkbox para separado */}
        <div className="flex-shrink-0">
          <button
            onClick={handleSeparatedToggle}
            disabled={disabled || isUpdating || item.not_sent}
            className={`
              w-6 h-6 rounded-md border-2 flex items-center justify-center transition-all
              ${item.separated 
                ? 'bg-green-500 border-green-500 text-white' 
                : item.not_sent 
                ? 'bg-red-600 border-red-600 text-white'
                : 'border-gray-300 hover:border-orange-400'
              }
              ${(disabled || isUpdating || item.sent_to_purchase || item.not_sent) 
                ? 'opacity-50 cursor-not-allowed' 
                : 'cursor-pointer'
              }
            `}
            title={
              item.sent_to_purchase 
                ? 'Item em compras' 
                : item.not_sent 
                ? 'Item enviado (não enviado = enviado para fins de contagem)' 
                : (item.separated ? 'Desmarcar como separado' : 'Marcar como separado')
            }
          >
            {isUpdating ? (
              <div className="animate-spin rounded-full h-3 w-3 border border-current border-t-transparent"></div>
            ) : (item.separated || item.not_sent) ? (
              <CheckCircleIcon className="h-4 w-4" />
            ) : null}
          </button>
        </div>

        {/* Informações do produto */}
        <div className="flex-1 min-w-0 grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Código */}
          <div className="md:col-span-1">
            <p className={`text-sm font-medium truncate ${itemStyling.textColor || 'text-gray-900'}`} title={item.product_code}>
              {item.product_code}
            </p>
          </div>

          {/* Nome do produto (modelo + descrição) */}
          <div className="md:col-span-1">
            <p className={`text-sm font-medium ${itemStyling.textColor || 'text-gray-900'}`} title={item.product_name}>
              {item.product_name}
            </p>
          </div>

          {/* Quantidade */}
          <div className="md:col-span-1">
            <p className={`text-sm ${itemStyling.textColor || 'text-gray-900'}`}>
              <span className="font-medium">{item.quantity}</span>
              <span className={`ml-1 ${itemStyling.textColor ? 'text-red-500' : 'text-gray-500'}`}>UN</span>
            </p>
          </div>
        </div>

        {/* Status e ações */}
        <div className="flex-shrink-0 flex items-center space-x-3">
          {/* Badge de status */}
          <div className="flex items-center space-x-2">
            <div className={status.iconColor}>
              {status.icon}
            </div>
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${status.badgeColor}`}>
              {status.badge}
            </span>
          </div>

          {/* Menu de ações */}
          <div className="relative">
            <button
              onClick={() => setShowMenu(!showMenu)}
              disabled={disabled || isUpdating}
              className={`
                p-1 text-gray-400 hover:text-gray-600 transition-colors
                ${(disabled || isUpdating) ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
              `}
              title="Mais ações"
            >
              <EllipsisVerticalIcon className="h-5 w-5" />
            </button>

            {/* Dropdown menu */}
            {showMenu && (
              <div className="absolute right-0 top-8 mt-1 w-56 bg-white rounded-md shadow-lg border border-gray-200 z-10">
                <div className="py-1">
                  {!item.sent_to_purchase && !item.not_sent && (
                    <>
                      <button
                        onClick={handleSendToPurchase}
                        className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-2"
                      >
                        <ShoppingCartIcon className="h-4 w-4" />
                        <span>Enviar para compras</span>
                      </button>
                      <button
                        onClick={handleMarkAsNotSent}
                        className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-2"
                      >
                        <XCircleIcon className="h-4 w-4" />
                        <span>Marcar como não enviado</span>
                      </button>
                    </>
                  )}
                  {item.sent_to_purchase && (
                    <button
                      onClick={handleMarkNotSent}
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-2"
                    >
                      <XCircleIcon className="h-4 w-4" />
                      <span>Remover das compras</span>
                    </button>
                  )}
                  {item.not_sent && (
                    <button
                      onClick={() => onUpdate({ not_sent: false })}
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-2"
                    >
                      <ClockIcon className="h-4 w-4" />
                      <span>Marcar como pendente</span>
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Data de separação */}
      {item.separated_at && (
        <div className="mt-2 ml-10 text-xs text-gray-500">
          <ClockIcon className="inline h-3 w-3 mr-1" />
          Separado em {formatDateTime(item.separated_at)}
        </div>
      )}
    </div>
  );
}