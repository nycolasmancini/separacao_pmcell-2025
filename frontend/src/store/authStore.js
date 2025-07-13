import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

// Note: axios interceptors are now handled in api.js service
// This avoids conflicts and ensures consistent authentication

// Adicionar logs para debug do Zustand
const debugLogger = (config) => (set, get, api) => 
  config(
    (...args) => {
      console.log('🔐 AuthStore - STATE CHANGE:', {
        timestamp: new Date().toISOString(),
        previous: get(),
        action: args[0],
        stateChangeCount: ++window.authStoreChangeCount || (window.authStoreChangeCount = 1)
      });
      set(...args);
    },
    get,
    api
  );

export const useAuthStore = create(
  debugLogger(
    persist(
      (set, get) => {
        const store = {
        // Estado
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,

        // Ações
      login: async (pin) => {
        console.log('AuthStore - Tentativa de login com PIN:', pin);
        set({ isLoading: true, error: null });
        
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/login`, {
            pin: pin
          });
          
          const { access_token, user } = response.data;
          console.log('AuthStore - Login bem-sucedido:', {
            user: user,
            hasToken: !!access_token
          });
          
          // Salvar token no localStorage PRIMEIRO para garantir disponibilidade imediata
          localStorage.setItem('auth_token', access_token);
          console.log('AuthStore - Token salvo no localStorage:', {
            tokenInStorage: localStorage.getItem('auth_token')?.substring(0, 10) + '...',
            storageLength: localStorage.getItem('auth_token')?.length
          });
          
          set({
            user,
            token: access_token,
            isAuthenticated: true,
            isLoading: false,
            error: null
          });
          
          console.log('AuthStore - Estado atualizado:', {
            isAuthenticated: true,
            hasUser: !!user,
            hasToken: !!access_token
          });
          
          return { success: true };
        } catch (error) {
          console.error('AuthStore - Erro no login:', {
            status: error.response?.status,
            data: error.response?.data,
            message: error.message,
            code: error.code
          });
          
          let errorMessage = 'Erro no login';
          
          if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
            errorMessage = 'Timeout - verifique sua conexão';
          } else if (error.code === 'ERR_NETWORK' || !error.response) {
            errorMessage = 'Erro de conexão - servidor não responde';
          } else if (error.response?.status === 401) {
            errorMessage = 'PIN incorreto';
          } else if (error.response?.status === 400) {
            errorMessage = error.response?.data?.detail || 'PIN inválido';
          } else if (error.response?.status >= 500) {
            errorMessage = 'Erro no servidor - tente novamente';
          } else {
            errorMessage = error.response?.data?.detail || 'Erro no login';
          }
          
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            error: errorMessage
          });
          return { success: false, error: errorMessage };
        }
      },

      logout: () => {
        // Limpar localStorage primeiro
        localStorage.removeItem('auth_token');
        
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
          error: null
        });
        
        console.log('AuthStore - Logout realizado, token removido');
      },

      clearError: () => {
        set({ error: null });
      },

      // Verificar se o usuário tem determinado role
      hasRole: (role) => {
        const { user } = get();
        return user?.role === role;
      },

      // Verificar se é admin
      isAdmin: () => {
        const { user } = get();
        return user?.role === 'admin';
      }
      };
      
      return store;
    },
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated
      })
    }
    )
  )
);