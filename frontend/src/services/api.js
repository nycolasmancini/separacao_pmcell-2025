import axios from 'axios';

// Base configuration - environment dependent
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Function to get auth store dynamically (avoid circular imports)
const getAuthStore = () => {
  try {
    const authStorageStr = localStorage.getItem('auth-storage');
    if (authStorageStr) {
      const authStorage = JSON.parse(authStorageStr);
      return authStorage.state;
    }
  } catch (error) {
    console.warn('Error reading auth storage:', error);
  }
  return null;
};

// Request interceptor to add authentication token
api.interceptors.request.use(
  (config) => {
    // Try to get token from Zustand store first, fallback to direct localStorage
    const authStore = getAuthStore();
    let token = authStore?.token || localStorage.getItem('auth_token');
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Enhanced debugging with both storage sources (only in development)
    if (import.meta.env.DEV) {
      console.log('API Request:', {
        method: config.method?.toUpperCase(),
        url: config.url,
        baseURL: config.baseURL,
        fullURL: `${config.baseURL}${config.url}`,
        hasToken: !!token,
        token: token ? `${token.substring(0, 10)}...` : null,
        tokenSource: authStore?.token ? 'zustand' : (localStorage.getItem('auth_token') ? 'localStorage' : 'none'),
        authStoreAuthenticated: authStore?.isAuthenticated,
        directTokenExists: !!localStorage.getItem('auth_token'),
        headers: config.headers,
      });
    }

    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling and logging
api.interceptors.response.use(
  (response) => {
    // Log successful responses (only in development)
    if (import.meta.env.DEV) {
      console.log('API Response:', {
        status: response.status,
        statusText: response.statusText,
        url: response.config.url,
        data: response.data,
      });
    }

    return response;
  },
  (error) => {
    // Enhanced error logging (matching existing pattern)
    console.error('API Response Error:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      url: error.config?.url,
      baseURL: error.config?.baseURL,
      fullURL: error.config ? `${error.config.baseURL}${error.config.url}` : 'unknown',
      data: error.response?.data,
      message: error.message,
    });

    // Handle authentication errors (matching existing pattern)
    if (error.response?.status === 401) {
      console.log('API: Token expired or invalid, clearing auth state...');
      localStorage.removeItem('auth_token');
      
      // Clear Zustand auth state as well
      try {
        const authStorageStr = localStorage.getItem('auth-storage');
        if (authStorageStr) {
          const authStorage = JSON.parse(authStorageStr);
          authStorage.state.isAuthenticated = false;
          authStorage.state.user = null;
          authStorage.state.token = null;
          localStorage.setItem('auth-storage', JSON.stringify(authStorage));
        }
      } catch (e) {
        console.warn('Error clearing auth storage:', e);
      }
      
      // DO NOT redirect here - let React Router handle it naturally
      // The ProtectedRoute component will detect !isAuthenticated and redirect
      console.log('API: Auth cleared, React Router will handle redirect');
    }

    // Enhanced error object for consistent error handling
    const enhancedError = {
      ...error,
      isNetworkError: error.code === 'ECONNABORTED' || error.message.includes('Network Error'),
      isTimeoutError: error.code === 'ECONNABORTED' && error.message.includes('timeout'),
      status: error.response?.status,
      message: error.response?.data?.detail || error.response?.data?.message || error.message,
    };

    return Promise.reject(enhancedError);
  }
);

// Utility function to check if API is available
export const checkApiHealth = async () => {
  try {
    const response = await api.get('/health');
    return { available: true, data: response.data };
  } catch (error) {
    console.error('API Health Check Failed:', error);
    return { 
      available: false, 
      error: error.isNetworkError ? 'Network Error' : error.message 
    };
  }
};

// Export the configured axios instance
export { api };

// Export additional utilities
export const apiConfig = {
  baseURL: API_BASE_URL,
  timeout: 10000,
};

// Default export for backward compatibility
export default api;