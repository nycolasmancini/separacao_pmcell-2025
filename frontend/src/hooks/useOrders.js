import { useState, useEffect, useCallback, useRef } from 'react';
import { useToast } from '../components/ToastContainer';
import { api } from '../services/api';
import { useAuthStore } from '../store/authStore';

export function useOrders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const hasInitializedRef = useRef(false);
  const isRequestingRef = useRef(false);
  
  console.log('📦 useOrders.js - HOOK CALL:', {
    timestamp: new Date().toISOString(),
    hasInitialized: hasInitializedRef.current,
    isRequesting: isRequestingRef.current,
    ordersLength: orders.length,
    loading,
    error: !!error,
    hookCallCount: ++window.useOrdersCallCount || (window.useOrdersCallCount = 1)
  });
  
  const { showError } = useToast();
  const { isAuthenticated } = useAuthStore();

  const fetchOrders = useCallback(async (forceRefresh = false) => {
    // Evitar múltiplas requisições simultâneas
    if (isRequestingRef.current && !forceRefresh) {
      return;
    }

    try {
      isRequestingRef.current = true;
      setLoading(true);
      setError(null);
      
      const response = await api.get('/orders');
      const data = response.data;
      
      // Mapear dados da API para formato esperado pelo frontend
      const mappedOrders = data.map(order => ({
        id: order.id,
        order_number: order.order_number,
        client: order.client_name,
        seller: order.seller_name,
        value: order.total_value,
        status: order.progress_percentage === 0 ? 'pending' : 
                order.progress_percentage === 100 ? 'completed' : 'in_progress',
        items_count: order.items_count,
        progress: order.progress_percentage,
        created_at: order.created_at
      }));
      
      setOrders(mappedOrders);
      hasInitializedRef.current = true;
      
    } catch (err) {
      console.error('Error fetching orders:', err);
      
      // Usar o sistema de erro do api.js que já trata AxiosError
      const errorMessage = err.message || 'Erro ao carregar pedidos';
      
      setError(errorMessage);
      hasInitializedRef.current = true;
      showError(errorMessage);
    } finally {
      setLoading(false);
      isRequestingRef.current = false;
    }
  }, [showError]);

  // Carregar pedidos na inicialização apenas uma vez usando useRef
  useEffect(() => {
    console.log('📦 useOrders.js - useEffect TRIGGERED:', {
      timestamp: new Date().toISOString(),
      isAuthenticated,
      hasInitialized: hasInitializedRef.current,
      effectTriggerCount: ++window.useOrdersEffectCount || (window.useOrdersEffectCount = 1)
    });
    
    if (!isAuthenticated) {
      hasInitializedRef.current = true;
      return;
    }
    
    if (hasInitializedRef.current) {
      return;
    }
    
    const timer = setTimeout(() => {
      console.log('📦 useOrders.js - CALLING fetchOrders via setTimeout');
      fetchOrders();
    }, 100);
    
    return () => clearTimeout(timer);
  }, [isAuthenticated]); // Removido fetchOrders das dependências para evitar loop

  // Função para recarregar manualmente
  const refetch = useCallback(() => {
    fetchOrders(true); // Force refresh
  }, [fetchOrders]);

  return {
    orders,
    loading,
    error,
    refetch,
    hasInitiallyLoaded: hasInitializedRef.current
  };
}