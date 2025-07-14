import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

// Adicionar logs para debug do Zustand
const debugLogger = (config) => (set, get, api) => 
  config(
    (...args) => {
      console.log('👥 OrderPresenceStore - STATE CHANGE:', {
        timestamp: new Date().toISOString(),
        previous: get(),
        action: args[0],
        stateChangeCount: ++window.presenceStoreChangeCount || (window.presenceStoreChangeCount = 1)
      });
      set(...args);
    },
    get,
    api
  );

export const useOrderPresenceStore = create(
  debugLogger(
    persist(
      (set, get) => ({
        // Estado
        // Estrutura: { orderId: [{ id, name, role, photo_url, accessed_at }, ...] }
        activeUsersByOrder: {},
        lastUpdate: null,

        // Ações
        updateOrderPresence: (orderId, users) => {
          console.log('OrderPresenceStore - Updating presence for order:', {
            orderId,
            userCount: users.length,
            users: users.map(u => ({ id: u.id, name: u.name }))
          });

          set((state) => ({
            activeUsersByOrder: {
              ...state.activeUsersByOrder,
              [orderId]: users
            },
            lastUpdate: new Date().toISOString()
          }));
        },

        addUserToOrder: (orderId, user) => {
          console.log('OrderPresenceStore - Adding user to order:', {
            orderId,
            user: { id: user.id, name: user.name }
          });

          set((state) => {
            const currentUsers = state.activeUsersByOrder[orderId] || [];
            
            // Verificar se usuário já existe
            const existingUserIndex = currentUsers.findIndex(u => u.id === user.id);
            
            let updatedUsers;
            if (existingUserIndex >= 0) {
              // Atualizar usuário existente
              updatedUsers = [...currentUsers];
              updatedUsers[existingUserIndex] = { ...user, accessed_at: new Date().toISOString() };
            } else {
              // Adicionar novo usuário
              updatedUsers = [...currentUsers, { ...user, accessed_at: new Date().toISOString() }];
            }

            return {
              activeUsersByOrder: {
                ...state.activeUsersByOrder,
                [orderId]: updatedUsers
              },
              lastUpdate: new Date().toISOString()
            };
          });
        },

        removeUserFromOrder: (orderId, userId) => {
          console.log('OrderPresenceStore - Removing user from order:', {
            orderId,
            userId
          });

          set((state) => {
            const currentUsers = state.activeUsersByOrder[orderId] || [];
            const updatedUsers = currentUsers.filter(u => u.id !== userId);

            return {
              activeUsersByOrder: {
                ...state.activeUsersByOrder,
                [orderId]: updatedUsers.length > 0 ? updatedUsers : undefined
              },
              lastUpdate: new Date().toISOString()
            };
          });
        },

        getActiveUsersForOrder: (orderId) => {
          const { activeUsersByOrder } = get();
          return activeUsersByOrder[orderId] || [];
        },

        getUserCountForOrder: (orderId) => {
          const users = get().getActiveUsersForOrder(orderId);
          return users.length;
        },

        isUserActiveInOrder: (orderId, userId) => {
          const users = get().getActiveUsersForOrder(orderId);
          return users.some(u => u.id === userId);
        },

        clearOrderPresence: (orderId) => {
          console.log('OrderPresenceStore - Clearing presence for order:', orderId);
          
          set((state) => {
            const newActiveUsersByOrder = { ...state.activeUsersByOrder };
            delete newActiveUsersByOrder[orderId];
            
            return {
              activeUsersByOrder: newActiveUsersByOrder,
              lastUpdate: new Date().toISOString()
            };
          });
        },

        clearAllPresence: () => {
          console.log('OrderPresenceStore - Clearing all presence');
          
          set({
            activeUsersByOrder: {},
            lastUpdate: new Date().toISOString()
          });
        },

        // Debug helpers
        getDebugInfo: () => {
          const state = get();
          return {
            totalOrders: Object.keys(state.activeUsersByOrder).length,
            totalUsers: Object.values(state.activeUsersByOrder).reduce((acc, users) => acc + users.length, 0),
            orderBreakdown: Object.entries(state.activeUsersByOrder).map(([orderId, users]) => ({
              orderId,
              userCount: users.length,
              users: users.map(u => ({ id: u.id, name: u.name }))
            })),
            lastUpdate: state.lastUpdate
          };
        }
      }),
      {
        name: 'order-presence-storage',
        storage: createJSONStorage(() => sessionStorage), // Usar sessionStorage para não persistir entre sessões
        partialize: (state) => ({
          // Não persistir dados de presença - sempre recarregar via WebSocket
          activeUsersByOrder: {},
          lastUpdate: null
        })
      }
    )
  )
);