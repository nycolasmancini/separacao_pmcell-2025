import { useState, useEffect, useCallback, useRef } from 'react';
import { useToast } from '../components/ToastContainer';

export function useSeparation(orderId) {
  const [order, setOrder] = useState(null);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [updating, setUpdating] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);
  
  const { showToast } = useToast();
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;

  // Fetch inicial dos dados do pedido
  const fetchOrderDetails = useCallback(async () => {
    if (!orderId) return;
    
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
        if (response.status === 404) {
          throw new Error('Pedido não encontrado');
        }
        if (response.status === 401) {
          throw new Error('Acesso negado');
        }
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
      showToast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [orderId, showToast]);

  // Atualização de item
  const updateItem = useCallback(async (itemId, updates) => {
    if (!orderId || updating) return;
    
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
      
      // Atualizar estado local (optimistic update já foi aplicado via WebSocket)
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
      
      // Reverter optimistic update em caso de erro
      await fetchOrderDetails();
    } finally {
      setUpdating(false);
    }
  }, [orderId, updating, showToast, fetchOrderDetails]);

  // Conexão WebSocket
  const connectWebSocket = useCallback(() => {
    if (!orderId) return;

    const token = localStorage.getItem('auth_token');
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/orders?token=${token}`;

    try {
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('WebSocket connected');
        setWsConnected(true);
        reconnectAttemptsRef.current = 0;
        
        // Inscrever-se nas atualizações deste pedido
        wsRef.current.send(JSON.stringify({
          type: 'subscribe',
          order_id: parseInt(orderId)
        }));
      };

      wsRef.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          handleWebSocketMessage(message);
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
        }
      };

      wsRef.current.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason);
        setWsConnected(false);
        
        // Tentar reconectar se não foi um fechamento intencional
        if (event.code !== 1000 && reconnectAttemptsRef.current < maxReconnectAttempts) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000);
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current++;
            connectWebSocket();
          }, delay);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setWsConnected(false);
      };

    } catch (err) {
      console.error('Error creating WebSocket connection:', err);
      setWsConnected(false);
    }
  }, [orderId]);

  // Handler para mensagens WebSocket
  const handleWebSocketMessage = useCallback((message) => {
    if (!message.type || !message.data) return;

    const { type, data } = message;

    switch (type) {
      case 'item_separated':
        if (data.order_id === parseInt(orderId)) {
          // Optimistic update para responsividade
          setItems(prevItems => prevItems.map(item => 
            item.id === data.item_id 
              ? { ...item, separated: true, separated_at: new Date().toISOString() }
              : item
          ));
          setOrder(prevOrder => prevOrder ? {
            ...prevOrder,
            progress_percentage: data.progress_percentage || prevOrder.progress_percentage
          } : null);
        }
        break;

      case 'item_sent_to_purchase':
        if (data.order_id === parseInt(orderId)) {
          setItems(prevItems => prevItems.map(item => 
            item.id === data.item_id 
              ? { ...item, sent_to_purchase: true }
              : item
          ));
        }
        break;

      case 'order_updated':
        if (data.order_id === parseInt(orderId)) {
          setOrder(prevOrder => prevOrder ? {
            ...prevOrder,
            progress_percentage: data.progress_percentage || prevOrder.progress_percentage
          } : null);
        }
        break;

      case 'order_completed':
        if (data.order_id === parseInt(orderId)) {
          showToast('🎉 Pedido concluído!', 'success');
          setOrder(prevOrder => prevOrder ? {
            ...prevOrder,
            progress_percentage: 100,
            status: 'completed'
          } : null);
        }
        break;

      case 'user_joined':
      case 'user_left':
        // Atualizar presença de usuários se necessário
        // Esta funcionalidade pode ser implementada futuramente
        break;

      default:
        console.log('Unknown WebSocket message type:', type);
    }
  }, [orderId, showToast]);

  // Cleanup function
  const cleanup = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close(1000, 'Component unmounting');
      wsRef.current = null;
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
  }, []);

  // Effects
  useEffect(() => {
    fetchOrderDetails();
  }, [fetchOrderDetails]);

  useEffect(() => {
    connectWebSocket();
    return cleanup;
  }, [connectWebSocket, cleanup]);

  // Cleanup on unmount
  useEffect(() => {
    return cleanup;
  }, [cleanup]);

  return {
    order,
    items,
    loading,
    error,
    updating,
    wsConnected,
    updateItem,
    refetch: fetchOrderDetails
  };
}