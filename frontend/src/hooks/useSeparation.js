import { useState, useEffect, useCallback, useRef } from 'react';
import { useToast } from '../components/ToastContainer';
import { useAuthStore } from '../store/authStore';

export function useSeparation(orderId) {
  const [order, setOrder] = useState(null);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [updating, setUpdating] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);
  
  const { addToast, showSuccess, showError } = useToast();
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
      console.log('useSeparation - Buscando pedido:', {
        orderId,
        hasToken: !!token,
        tokenStart: token?.substring(0, 20) + '...'
      });
      
      const response = await fetch(`/api/orders/${orderId}/detail`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      console.log('useSeparation - Resposta da API:', {
        status: response.status,
        statusText: response.statusText,
        url: response.url,
        headers: Object.fromEntries(response.headers.entries())
      });

      if (!response.ok) {
        let errorMessage = '';
        try {
          const errorData = await response.text();
          console.error('useSeparation - Erro detalhado:', {
            status: response.status,
            statusText: response.statusText,
            body: errorData,
            url: response.url
          });
          
          // Tentar parsear como JSON se possível
          try {
            const jsonError = JSON.parse(errorData);
            errorMessage = jsonError.detail || jsonError.message || errorData;
          } catch {
            errorMessage = errorData;
          }
        } catch (parseError) {
          console.error('useSeparation - Erro ao parsear resposta de erro:', parseError);
          errorMessage = `Erro ${response.status}: ${response.statusText}`;
        }

        if (response.status === 404) {
          throw new Error('Pedido não encontrado');
        }
        if (response.status === 401) {
          throw new Error('Acesso negado - verifique se você está logado');
        }
        if (response.status === 500) {
          throw new Error(`Erro interno do servidor: ${errorMessage}`);
        }
        throw new Error(`Erro ao carregar pedido (${response.status}): ${errorMessage}`);
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
      
      // Verificar se é erro de rede
      const isNetworkError = err.name === 'TypeError' && err.message.includes('Failed to fetch');
      const errorMessage = isNetworkError 
        ? 'Erro de conexão - verifique se o servidor está rodando' 
        : err.message;
      
      setError(errorMessage);
      showError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [orderId, showError]);

  // Atualização de item com retry
  const updateItem = useCallback(async (itemId, updates, retryCount = 0) => {
    if (!orderId || updating) return;
    
    const maxRetries = 2;
    
    try {
      setUpdating(true);
      
      // Log de auditoria
      const currentUser = useAuthStore.getState().user;
      console.log('Auditoria - Atualização de item:', {
        orderId,
        itemId,
        updates,
        user: currentUser?.name,
        userRole: currentUser?.role,
        timestamp: new Date().toISOString()
      });
      
      const token = localStorage.getItem('auth_token');
      const requestBody = {
        updates: [{ item_id: itemId, ...updates }]
      };
      
      console.log('useSeparation - Atualizando item:', {
        orderId,
        itemId,
        updates,
        requestBody,
        url: `/api/orders/${orderId}/items`
      });
      
      const response = await fetch(`/api/orders/${orderId}/items`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
      });

      console.log('useSeparation - Resposta da atualização:', {
        status: response.status,
        statusText: response.statusText,
        url: response.url
      });

      if (!response.ok) {
        let errorMessage = '';
        try {
          const errorData = await response.text();
          console.error('useSeparation - Erro ao atualizar item:', {
            status: response.status,
            statusText: response.statusText,
            body: errorData,
            url: response.url,
            requestBody
          });
          
          try {
            const jsonError = JSON.parse(errorData);
            errorMessage = jsonError.detail || jsonError.message || errorData;
          } catch {
            errorMessage = errorData;
          }
        } catch (parseError) {
          console.error('useSeparation - Erro ao parsear resposta de erro da atualização:', parseError);
          errorMessage = `Erro ${response.status}: ${response.statusText}`;
        }
        
        throw new Error(`Erro ao atualizar item (${response.status}): ${errorMessage}`);
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
        showSuccess(
          updates.separated ? 'Item marcado como separado' : 'Item desmarcado'
        );
      }
      if (updates.sent_to_purchase !== undefined) {
        showSuccess(
          updates.sent_to_purchase ? 'Item enviado para compras' : 'Item removido das compras'
        );
      }
      
    } catch (err) {
      console.error('Error updating item:', err);
      
      // Verificar se é erro de rede
      const isNetworkError = err.name === 'TypeError' && err.message.includes('Failed to fetch');
      
      // Tentar novamente se for erro de rede e ainda temos tentativas
      if (isNetworkError && retryCount < maxRetries) {
        console.log(`Tentando novamente... (tentativa ${retryCount + 1}/${maxRetries})`);
        setUpdating(false);
        
        // Aguardar um pouco antes de tentar novamente
        await new Promise(resolve => setTimeout(resolve, 1000 * (retryCount + 1)));
        
        return updateItem(itemId, updates, retryCount + 1);
      }
      
      const errorMessage = isNetworkError 
        ? 'Erro de conexão ao atualizar item - verifique se o servidor está rodando' 
        : `Erro ao atualizar item: ${err.message}`;
      
      showError(errorMessage);
      
      // Reverter optimistic update em caso de erro
      await fetchOrderDetails();
    } finally {
      setUpdating(false);
    }
  }, [orderId, updating, showError, fetchOrderDetails]);

  // Conexão WebSocket
  const connectWebSocket = useCallback(() => {
    if (!orderId) return;

    const token = localStorage.getItem('auth_token');
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // Para desenvolvimento local, usar porta do backend
    const backendHost = window.location.hostname === 'localhost' 
      ? 'localhost:8000' 
      : window.location.host;
    const wsUrl = `${protocol}//${backendHost}/api/v1/ws/orders?token=${token}`;

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
          showSuccess('🎉 Pedido concluído!');
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
  }, [orderId, showSuccess]);

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