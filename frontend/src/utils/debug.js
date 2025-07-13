// Utilitário central para debug
export const DEBUG_CONFIG = {
  enabled: true, // Mudar para false para desativar todos os logs
  components: {
    app: true,
    dashboard: true,
    useOrders: true,
    authStore: true,
    toastProvider: true,
    api: true
  }
};

export const debugLog = (component, message, data = {}) => {
  if (!DEBUG_CONFIG.enabled || !DEBUG_CONFIG.components[component]) {
    return;
  }
  
  const emoji = {
    app: '🔄',
    dashboard: '🏠',
    useOrders: '📦',
    authStore: '🔐',
    toastProvider: '🍞',
    api: '🌐'
  };
  
  console.log(`${emoji[component] || '🔍'} ${component.toUpperCase()} - ${message}:`, {
    timestamp: new Date().toISOString(),
    ...data
  });
};

// Contadores globais para tracking
export const initCounters = () => {
  if (typeof window !== 'undefined') {
    window.debugCounters = {
      appRender: 0,
      dashboardRender: 0,
      useOrdersCall: 0,
      useOrdersEffect: 0,
      authStoreChange: 0,
      toastProviderRender: 0,
      apiRequest: 0
    };
  }
};

export const incrementCounter = (name) => {
  if (typeof window !== 'undefined' && window.debugCounters) {
    window.debugCounters[name] = (window.debugCounters[name] || 0) + 1;
    return window.debugCounters[name];
  }
  return 0;
};

// Reset de contadores
export const resetCounters = () => {
  if (typeof window !== 'undefined') {
    window.debugCounters = {
      appRender: 0,
      dashboardRender: 0,
      useOrdersCall: 0,
      useOrdersEffect: 0,
      authStoreChange: 0,
      toastProviderRender: 0,
      apiRequest: 0
    };
  }
};

// Inicializar na primeira carga
initCounters();