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
      
      const response = await fetch(`/api/v1/orders/${orderId}/detail`, {
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
      
      // Ordenar itens com nova ordem: pendentes > não enviados > compras > separados
      const sortedItems = [...data.items].sort((a, b) => {
        // Função para determinar prioridade do item
        const getPriority = (item) => {
          if (item.separated) return 4; // Separados por último
          if (item.sent_to_purchase) return 3; // Compras acima dos separados
          if (item.not_sent) return 2; // Não enviados acima das compras
          return 1; // Pendentes primeiro
        };
        
        const priorityA = getPriority(a);
        const priorityB = getPriority(b);
        
        // Se prioridades diferentes, ordenar por prioridade
        if (priorityA !== priorityB) {
          return priorityA - priorityB;
        }
        
        // Se mesma prioridade, ordenar alfabeticamente
        return a.product_name.localeCompare(b.product_name, 'pt-BR', { sensitivity: 'base' });
      });
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
        url: `/api/v1/orders/${orderId}/items`
      });
      
      const response = await fetch(`/api/v1/orders/${orderId}/items`, {
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
          console.error('❌ useSeparation - Erro ao atualizar item:', {
            status: response.status,
            statusText: response.statusText,
            body: errorData,
            url: response.url,
            requestBody,
            orderId,
            itemId,
            updates
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
        
        // Mensagens de erro mais específicas para o usuário
        if (response.status === 404) {
          throw new Error('Item ou pedido não encontrado');
        } else if (response.status === 401) {
          throw new Error('Acesso negado - faça login novamente');
        } else if (response.status === 500) {
          throw new Error('Erro interno do servidor - tente novamente');
        } else {
          throw new Error(`Erro ao atualizar item (${response.status}): ${errorMessage}`);
        }
      }

      const updatedOrder = await response.json();
      console.log('✅ useSeparation - Item atualizado com sucesso:', {
        orderId,
        itemId,
        updates,
        newProgress: updatedOrder.progress_percentage
      });
      
      // Atualizar estado local (optimistic update já foi aplicado via WebSocket)
      setOrder(updatedOrder);
      
      // Atualizar items com nova ordem: pendentes > não enviados > compras > separados
      const sortedItems = [...updatedOrder.items].sort((a, b) => {
        // Função para determinar prioridade do item
        const getPriority = (item) => {
          if (item.separated) return 4; // Separados por último
          if (item.sent_to_purchase) return 3; // Compras acima dos separados
          if (item.not_sent) return 2; // Não enviados acima das compras
          return 1; // Pendentes primeiro
        };
        
        const priorityA = getPriority(a);
        const priorityB = getPriority(b);
        
        // Se prioridades diferentes, ordenar por prioridade
        if (priorityA !== priorityB) {
          return priorityA - priorityB;
        }
        
        // Se mesma prioridade, ordenar alfabeticamente
        return a.product_name.localeCompare(b.product_name, 'pt-BR', { sensitivity: 'base' });
      });
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
      if (updates.not_sent !== undefined) {
        showSuccess(
          updates.not_sent ? 'Item marcado como não enviado' : 'Item marcado como pendente'
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
        
        // Se foi uma reconexão, mostrar mensagem de sucesso
        if (reconnectAttemptsRef.current > 0) {
          showSuccess('Conexão reestabelecida!');
        }
        
        reconnectAttemptsRef.current = 0;
        
        // Inscrever-se nas atualizações deste pedido
        wsRef.current.send(JSON.stringify({
          type: 'join_order',
          data: {
            order_id: parseInt(orderId)
          }
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
        
        // Log específico para diferentes códigos de erro
        switch (event.code) {
          case 1000:
            console.log('WebSocket closed normally');
            break;
          case 1006:
            console.error('WebSocket closed abnormally (code 1006) - likely connection issue');
            showError('Conexão perdida - tentando reconectar...');
            break;
          case 1008:
            console.error('WebSocket closed due to policy violation (code 1008) - likely auth issue');
            showError('Erro de autenticação - faça login novamente');
            break;
          case 1011:
            console.error('WebSocket closed due to server error (code 1011)');
            showError('Erro no servidor - tentando reconectar...');
            break;
          default:
            console.error(`WebSocket closed with code ${event.code}: ${event.reason}`);
            break;
        }
        
        // Tentar reconectar se não foi um fechamento intencional
        if (event.code !== 1000 && event.code !== 1008 && reconnectAttemptsRef.current < maxReconnectAttempts) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000);
          console.log(`Tentando reconectar WebSocket em ${delay}ms (tentativa ${reconnectAttemptsRef.current + 1}/${maxReconnectAttempts})`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current++;
            connectWebSocket();
          }, delay);
        } else if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
          console.error('Máximo de tentativas de reconexão WebSocket atingido');
          showError('Não foi possível reconectar - recarregue a página');
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setWsConnected(false);
        
        // Log mais detalhado do erro
        if (error.type === 'error') {
          console.error('WebSocket failed to connect or connection failed');
        }
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
          // Optimistic update para responsividade com reordenação
          setItems(prevItems => {
            const updatedItems = prevItems.map(item => 
              item.id === data.item_id 
                ? { ...item, separated: true, separated_at: new Date().toISOString() }
                : item
            );
            // Reordenar: não separados primeiro, depois separados
            return updatedItems.sort((a, b) => {
              if (a.separated !== b.separated) {
                return a.separated ? 1 : -1;
              }
              return a.product_name.localeCompare(b.product_name, 'pt-BR', { sensitivity: 'base' });
            });
          });
          setOrder(prevOrder => prevOrder ? {
            ...prevOrder,
            progress_percentage: data.progress_percentage || prevOrder.progress_percentage
          } : null);
        }
        break;

      case 'item_sent_to_purchase':
        if (data.order_id === parseInt(orderId)) {
          setItems(prevItems => {
            const updatedItems = prevItems.map(item => 
              item.id === data.item_id 
                ? { ...item, sent_to_purchase: true }
                : item
            );
            // Reordenar: não separados primeiro, depois separados/compras
            return updatedItems.sort((a, b) => {
              if (a.separated !== b.separated) {
                return a.separated ? 1 : -1;
              }
              return a.product_name.localeCompare(b.product_name, 'pt-BR', { sensitivity: 'base' });
            });
          });
        }
        break;

      case 'item_not_sent':
        if (data.order_id === parseInt(orderId)) {
          setItems(prevItems => {
            const updatedItems = prevItems.map(item => 
              item.id === data.item_id 
                ? { ...item, not_sent: true }
                : item
            );
            // Reordenar conforme prioridade: pendentes > não enviados > compras > separados
            return updatedItems.sort((a, b) => {
              const getPriority = (item) => {
                if (item.separated) return 4; // Separados por último
                if (item.sent_to_purchase) return 3; // Compras acima dos separados
                if (item.not_sent) return 2; // Não enviados acima das compras
                return 1; // Pendentes primeiro
              };
              
              const priorityA = getPriority(a);
              const priorityB = getPriority(b);
              
              if (priorityA !== priorityB) {
                return priorityA - priorityB;
              }
              
              return a.product_name.localeCompare(b.product_name, 'pt-BR', { sensitivity: 'base' });
            });
          });
          setOrder(prevOrder => prevOrder ? {
            ...prevOrder,
            progress_percentage: data.progress_percentage || prevOrder.progress_percentage
          } : null);
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
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      // Sair do pedido antes de fechar a conexão
      wsRef.current.send(JSON.stringify({
        type: 'leave_order',
        data: {
          order_id: parseInt(orderId)
        }
      }));
      wsRef.current.close(1000, 'Component unmounting');
      wsRef.current = null;
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
  }, [orderId]);

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

  // Função para completar pedido manualmente
  const completeOrder = useCallback(async () => {
    if (!order) return;

    try {
      setUpdating(true);
      console.log('🏁 useSeparation - Completando pedido:', { orderId: order.id });

      const token = localStorage.getItem('auth_token');
      if (!token) {
        throw new Error('Token de autenticação não encontrado');
      }

      const response = await fetch(`/api/v1/orders/${order.id}/complete`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.detail || errorData.message || 'Erro desconhecido';
        
        if (response.status === 404) {
          throw new Error('Pedido não encontrado');
        } else if (response.status === 400) {
          throw new Error(errorMessage);
        } else if (response.status === 403) {
          throw new Error('Sem permissão para completar pedidos');
        } else if (response.status === 401) {
          throw new Error('Acesso negado - faça login novamente');
        } else {
          throw new Error(`Erro ao completar pedido (${response.status}): ${errorMessage}`);
        }
      }

      const result = await response.json();
      console.log('✅ useSeparation - Pedido completado com sucesso:', result);

      // Atualizar estado local
      setOrder(prevOrder => ({
        ...prevOrder,
        status: 'completed',
        progress_percentage: 100,
        completed_at: result.completed_at
      }));

      showSuccess('🎉 Pedido concluído com sucesso!');
      
      return result;
    } catch (err) {
      console.error('❌ useSeparation - Erro ao completar pedido:', err);
      showError(err.message || 'Erro ao completar pedido');
      throw err;
    } finally {
      setUpdating(false);
    }
  }, [order, showSuccess, showError]);

  return {
    order,
    items,
    loading,
    error,
    updating,
    wsConnected,
    updateItem,
    completeOrder,
    refetch: fetchOrderDetails
  };
}