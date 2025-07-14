import { useEffect, useCallback, useRef } from 'react';
import { useOrderPresenceStore } from '../store/orderPresenceStore';
import { useAuthStore } from '../store/authStore';
import api from '../services/api';

/**
 * Hook para gerenciar presença de usuários em pedidos via WebSocket
 */
export function useOrderPresence() {
  const {
    activeUsersByOrder,
    updateOrderPresence,
    addUserToOrder,
    removeUserFromOrder,
    getActiveUsersForOrder,
    getUserCountForOrder,
    isUserActiveInOrder
  } = useOrderPresenceStore();

  const { user, token } = useAuthStore();
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const isConnectedRef = useRef(false);

  // Conectar ao WebSocket
  const connectWebSocket = useCallback(() => {
    if (!user || !token || isConnectedRef.current) {
      return;
    }

    try {
      // CORREÇÃO: Usar o caminho completo da API
      const wsUrl = `ws://localhost:8000/api/v1/ws/orders?token=${token}`;
      console.log('🔌 Connecting to WebSocket for presence updates:', wsUrl);

      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('✅ WebSocket connected for presence updates');
        isConnectedRef.current = true;
        
        // Limpar timeout de reconexão
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
          reconnectTimeoutRef.current = null;
        }
      };

      wsRef.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          console.log('📨 WebSocket message received:', message);

          handleWebSocketMessage(message);
        } catch (error) {
          console.error('❌ Error parsing WebSocket message:', error);
        }
      };

      wsRef.current.onclose = () => {
        console.log('🔌 WebSocket disconnected - attempting to reconnect...');
        isConnectedRef.current = false;
        
        // Tentar reconectar após 3 segundos
        reconnectTimeoutRef.current = setTimeout(() => {
          connectWebSocket();
        }, 3000);
      };

      wsRef.current.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        isConnectedRef.current = false;
      };

    } catch (error) {
      console.error('❌ Error creating WebSocket connection:', error);
    }
  }, [user, token]);

  // Manipular mensagens do WebSocket
  const handleWebSocketMessage = useCallback((message) => {
    const { type, data } = message;

    switch (type) {
      case 'order_access':
        // Usuário acessou um pedido
        if (data.order_id && data.user) {
          console.log('👤 User accessed order:', data);
          addUserToOrder(data.order_id, {
            id: data.user.id,
            name: data.user.name,
            role: data.user.role,
            photo_url: data.user.photo_url
          });
        }
        break;

      case 'presence_update':
        // Atualização de presença em um pedido
        if (data.order_id && data.active_users) {
          console.log('👥 Presence update for order:', data);
          updateOrderPresence(data.order_id, data.active_users.map(u => ({
            id: u.user_id,
            name: u.user_name,
            role: u.role || 'unknown',
            photo_url: u.photo_url || null,
            connected_at: u.connected_at
          })));
        }
        break;

      case 'user_joined':
        // Usuário entrou em um pedido
        if (data.order_id && data.user_id && data.user_name) {
          console.log('➕ User joined order:', data);
          addUserToOrder(data.order_id, {
            id: data.user_id,
            name: data.user_name,
            role: data.role || 'unknown',
            photo_url: data.photo_url || null
          });
        }
        break;

      case 'user_left':
        // Usuário saiu
        if (data.user_id) {
          console.log('➖ User left:', data);
          // Remover usuário de todos os pedidos
          Object.keys(activeUsersByOrder).forEach(orderId => {
            removeUserFromOrder(parseInt(orderId), data.user_id);
          });
        }
        break;

      default:
        console.log('🔄 Unhandled WebSocket message type:', type);
    }
  }, [addUserToOrder, updateOrderPresence, removeUserFromOrder, activeUsersByOrder]);

  // Buscar usuários ativos de um pedido via API
  const fetchActiveUsers = useCallback(async (orderId) => {
    try {
      const response = await api.get(`/auth/orders/${orderId}/active-users`);
      const users = response.data;
      console.log('📥 Fetched active users for order:', { orderId, users });
      
      // Converter formato da API para formato do store
      const formattedUsers = users.map(u => ({
        id: u.user_id,
        name: u.user_name,
        role: 'unknown', // API não retorna role por enquanto
        photo_url: null,  // API não retorna photo_url por enquanto
        connected_at: u.connected_at
      }));
      
      updateOrderPresence(orderId, formattedUsers);
      return formattedUsers;
    } catch (error) {
      console.error('❌ Error fetching active users:', error);
      return [];
    }
  }, [token, updateOrderPresence]);

  // Conectar ao WebSocket quando hook for montado
  useEffect(() => {
    connectWebSocket();

    return () => {
      // Cleanup
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
      isConnectedRef.current = false;
    };
  }, [connectWebSocket]);

  return {
    // Estado
    activeUsersByOrder,
    isConnected: isConnectedRef.current,

    // Métodos para obter dados
    getActiveUsersForOrder,
    getUserCountForOrder,
    isUserActiveInOrder,
    
    // Métodos para atualizar
    fetchActiveUsers,
    updateOrderPresence,
    addUserToOrder,
    removeUserFromOrder,

    // Estado da conexão
    reconnect: connectWebSocket
  };
}