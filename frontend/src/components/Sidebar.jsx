import { useState, useEffect } from 'react';
import { useAuthStore } from '../store/authStore';
import { useResponsive } from '../hooks/useResponsive';

export default function Sidebar({ 
  currentPage = 'dashboard',
  onNavigate,
  onCollapsedChange,
  className = ''
}) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const { user, logout } = useAuthStore();
  const { isTabletUp } = useResponsive();

  const navigationItems = [
    {
      key: 'dashboard',
      label: 'Dashboard',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5a2 2 0 012-2h4a2 2 0 012 2v2M8 5v2" />
        </svg>
      ),
      roles: ['admin', 'seller', 'separator', 'buyer']
    },
    {
      key: 'create-order',
      label: 'Novo Pedido',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
      ),
      roles: ['admin', 'seller']
    },
    {
      key: 'purchases',
      label: 'Compras',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
        </svg>
      ),
      roles: ['admin', 'buyer']
    },
    {
      key: 'admin',
      label: 'Administrativo',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      ),
      roles: ['admin']
    }
  ];

  const availableItems = navigationItems.filter(item => 
    item.roles.includes(user?.role)
  );

  // Notify parent when collapsed state changes
  useEffect(() => {
    if (onCollapsedChange) {
      onCollapsedChange(isCollapsed);
    }
  }, [isCollapsed, onCollapsedChange]);

  const handleNavigation = (page) => {
    if (onNavigate) {
      onNavigate(page);
    }
  };

  const handleLogout = () => {
    logout();
  };

  const getUserInitials = (name) => {
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .substring(0, 2)
      .toUpperCase();
  };

  // Don't render sidebar on mobile devices
  if (!isTabletUp) {
    return null;
  }

  return (
    <div className={`
      sidebar-layout fixed left-0 top-0 h-full z-40
      bg-white border-r border-gray-200 flex flex-col transition-all duration-300
      ${isCollapsed ? 'w-16' : 'w-64'} 
      ${className}
    `}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          {!isCollapsed && (
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 rounded-lg bg-orange-500 flex items-center justify-center">
                <span className="text-white font-bold text-sm">PM</span>
              </div>
              <div>
                <h1 className="text-lg font-bold text-gray-900">PMCELL</h1>
                <p className="text-xs text-gray-500">Separação de Pedidos</p>
              </div>
            </div>
          )}
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <svg 
              className={`w-5 h-5 text-gray-500 transition-transform ${isCollapsed ? 'rotate-180' : ''}`} 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {availableItems.map((item) => (
            <li key={item.key}>
              <button
                onClick={() => handleNavigation(item.key)}
                className={`
                  w-full flex items-center rounded-lg transition-colors hover:bg-gray-100
                  ${isCollapsed 
                    ? 'justify-center px-2 py-3' 
                    : 'justify-start space-x-3 px-3 py-2 text-left'
                  }
                  ${currentPage === item.key 
                    ? `bg-orange-100 text-orange-700 ${isCollapsed ? 'rounded-lg' : 'border-r-2 border-orange-500'}` 
                    : 'text-gray-700'
                  }
                `}
                title={isCollapsed ? item.label : ''}
              >
                <span className="flex-shrink-0">{item.icon}</span>
                {!isCollapsed && (
                  <span className="text-sm font-medium">{item.label}</span>
                )}
              </button>
            </li>
          ))}
        </ul>
      </nav>

      {/* User section */}
      <div className="p-4 border-t border-gray-200">
        <div className={`flex items-center ${isCollapsed ? 'justify-center' : 'justify-between'}`}>
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-full bg-orange-500 flex items-center justify-center text-white text-xs font-medium">
              {getUserInitials(user?.name || 'Usuario')}
            </div>
            {!isCollapsed && (
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {user?.name}
                </p>
                <p className="text-xs text-gray-500 capitalize">
                  {user?.role === 'admin' ? 'Administrador' :
                   user?.role === 'seller' ? 'Vendedor' :
                   user?.role === 'separator' ? 'Separador' :
                   user?.role === 'buyer' ? 'Comprador' : user?.role}
                </p>
              </div>
            )}
          </div>
          {!isCollapsed && (
            <button
              onClick={handleLogout}
              className="p-1 rounded-lg hover:bg-gray-100 transition-colors"
              title="Sair"
            >
              <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}