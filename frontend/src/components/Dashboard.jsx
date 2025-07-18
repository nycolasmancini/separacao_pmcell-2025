import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import Sidebar from './Sidebar';
import OrderGrid from './OrderGrid';
import StatusFilter from './StatusFilter';
import OrderAccessLogin from './OrderAccessLogin';
import { useToast } from './ToastContainer';
import { useOrders } from '../hooks/useOrders';
import { useOrderPresence } from '../hooks/useOrderPresence';
import { ComponentErrorBoundary } from './ErrorBoundary';
import { DashboardSkeleton } from './Skeleton';
import { useResponsive } from '../hooks/useResponsive';
import { dashboardAnimations, staggerContainerVariants } from '../utils/animations';
import Logo from './Logo';

function Dashboard() {
  const { user, setOrderAccess } = useAuthStore();
  const { showSuccess, showError, showInfo } = useToast();
  const navigate = useNavigate();
  const { isTabletUp, isMobile } = useResponsive();
  
  console.log('🏠 Dashboard.jsx - RENDER:', {
    timestamp: new Date().toISOString(),
    user: user?.name,
    renderCount: ++window.dashboardRenderCount || (window.dashboardRenderCount = 1)
  });
  
  // Use real API data instead of mock data
  const { orders, loading, error, refetch, hasInitiallyLoaded } = useOrders();
  
  // Initialize presence tracking
  const { 
    isConnected: presenceConnected, 
    getActiveUsersForOrder,
    fetchActiveUsers 
  } = useOrderPresence();
  
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [statusFilter, setStatusFilter] = useState('all');
  const [filteredOrders, setFilteredOrders] = useState([]);
  const [orderCounts, setOrderCounts] = useState({});
  const [activeUsers, setActiveUsers] = useState({});
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  
  // Order access modal state
  const [isOrderAccessModalOpen, setIsOrderAccessModalOpen] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState(null);

  // Show messages only once after initial load - usando useRef para controlar
  const hasShownInitialMessageRef = useRef(false);
  
  useEffect(() => {
    if (!hasInitiallyLoaded || loading || hasShownInitialMessageRef.current) return;
    
    if (!error && orders.length > 0) {
      showSuccess(`Dashboard carregado com sucesso! ${orders.length} pedidos encontrados.`);
      hasShownInitialMessageRef.current = true;
    } else if (!error && orders.length === 0) {
      showInfo('Nenhum pedido encontrado. Faça upload de um PDF para criar um novo pedido.');
      hasShownInitialMessageRef.current = true;
    }
  }, [hasInitiallyLoaded, loading, error, orders.length]);

  useEffect(() => {
    // Filtrar pedidos
    if (statusFilter === 'all') {
      setFilteredOrders(orders);
    } else {
      setFilteredOrders(orders.filter(order => order.status === statusFilter));
    }

    // Calcular contadores
    const counts = orders.reduce((acc, order) => {
      acc[order.status] = (acc[order.status] || 0) + 1;
      return acc;
    }, {});
    setOrderCounts(counts);
  }, [orders, statusFilter]);

  const handleNavigation = (page) => {
    setCurrentPage(page);
    
    // Handle actual navigation for certain pages
    if (page === 'purchases') {
      navigate('/purchase-items');
      showInfo('Navegando para tela de compras');
    } else if (page === 'admin') {
      navigate('/admin');
      showInfo('Navegando para painel administrativo');
    } else if (page === 'create-order') {
      navigate('/novo-pedido');
      showInfo('Navegando para criação de novo pedido');
    } else {
      showInfo(`Navegando para ${page}`);
    }
  };

  const handleOrderClick = (order) => {
    console.log('Dashboard - Solicitando acesso ao pedido:', {
      orderId: order.id,
      orderNumber: order.order_number,
      user: user?.name,
      userRole: user?.role
    });
    
    // Abrir modal de autenticação para acesso ao pedido
    setSelectedOrder(order);
    setIsOrderAccessModalOpen(true);
  };

  const handleOrderAccessSuccess = async (accessUser, order) => {
    console.log('Dashboard - Acesso ao pedido autorizado:', {
      orderId: order.id,
      orderNumber: order.order_number,
      accessUser: accessUser.name,
      accessUserRole: accessUser.role
    });

    // Definir acesso ao pedido no estado global
    setOrderAccess(accessUser, order.id);
    
    // Buscar usuários ativos atualizados para este pedido
    try {
      await fetchActiveUsers(order.id);
    } catch (error) {
      console.warn('Failed to fetch active users after access:', error);
    }
    
    // Navegar para a tela de separação
    navigate(`/orders/${order.id}/separation`);
    showSuccess(`Acesso autorizado! Abrindo separação do pedido #${order.order_number}`);
  };

  const handleOrderAccessClose = () => {
    setIsOrderAccessModalOpen(false);
    setSelectedOrder(null);
  };

  const handleFilterChange = (filter) => {
    setStatusFilter(filter);
  };

  const handleSidebarCollapse = (collapsed) => {
    setSidebarCollapsed(collapsed);
  };

  // Show loading skeleton only during initial load
  if (loading && !hasInitiallyLoaded) {
    return <DashboardSkeleton />;
  }

  return (
    <div className="min-h-screen bg-gray-50 safe-top safe-bottom">
      {/* Sidebar */}
      <ComponentErrorBoundary>
        <Sidebar
          currentPage={currentPage}
          onNavigate={handleNavigation}
          onCollapsedChange={handleSidebarCollapse}
        />
      </ComponentErrorBoundary>

      {/* Main Content */}
      <div className={`main-content flex flex-col min-h-screen ${
        isTabletUp ? (sidebarCollapsed ? 'ml-16' : 'ml-64') : 'ml-0'
      }`}>
        {/* Header */}
        <motion.header
          initial={{ y: -50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="bg-white shadow-sm border-b"
        >
          <div className="px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                {!isTabletUp && (
                  <Logo size="sm" />
                )}
                <div>
                  <h1 className={`font-bold text-gray-900 ${isMobile ? 'text-xl' : 'text-2xl'}`}>
                    Dashboard de Pedidos
                  </h1>
                  <p className="text-gray-600 text-sm">
                    Gerencie e acompanhe os pedidos em separação
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-600">Bem-vindo,</p>
                <p className="font-medium text-gray-900">{user?.name}</p>
                <div className="flex items-center space-x-2 mt-1">
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                    {user?.role}
                  </span>
                  <div className="flex items-center space-x-1">
                    <div className={`h-2 w-2 rounded-full ${presenceConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                    <span className="text-xs text-gray-500">
                      {presenceConnected ? 'Online' : 'Offline'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.header>

        {/* Content Area */}
        <main className="flex-1 px-4 py-2 tablet:px-4 tablet:py-4">
          <motion.div
            variants={staggerContainerVariants}
            initial="initial"
            animate="animate"
            className="space-y-6"
          >
            {/* Statistics Cards */}
            <motion.div 
              variants={dashboardAnimations.statsCard}
              className="grid grid-cols-2 tablet:grid-cols-4 gap-4 tablet:gap-6"
            >
              <div className="card card-hover touch-padding">
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
                    <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Total</p>
                    <p className={`font-bold text-gray-900 ${isMobile ? 'text-xl' : 'text-2xl'}`}>
                      {orders.length}
                    </p>
                  </div>
                </div>
              </div>

              <div className="card card-hover touch-padding">
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-yellow-100 rounded-xl flex items-center justify-center">
                    <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Pendentes</p>
                    <p className={`font-bold text-gray-900 ${isMobile ? 'text-xl' : 'text-2xl'}`}>
                      {orderCounts.pending || 0}
                    </p>
                  </div>
                </div>
              </div>

              <div className="card card-hover touch-padding">
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
                    <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                    </svg>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Em Separação</p>
                    <p className={`font-bold text-gray-900 ${isMobile ? 'text-xl' : 'text-2xl'}`}>
                      {orderCounts.in_progress || 0}
                    </p>
                  </div>
                </div>
              </div>

              <div className="card card-hover touch-padding">
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                    <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Concluídos</p>
                    <p className={`font-bold text-gray-900 ${isMobile ? 'text-xl' : 'text-2xl'}`}>
                      {orderCounts.completed || 0}
                    </p>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Filters */}
            <motion.div 
              variants={dashboardAnimations.statsCard}
              className="card touch-padding"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Filtrar Pedidos</h3>
                <button 
                  onClick={refetch}
                  disabled={loading}
                  className="btn-ghost text-sm touch-target disabled:opacity-50"
                >
                  {loading ? 'Carregando...' : 'Atualizar'}
                </button>
              </div>
              <ComponentErrorBoundary>
                <StatusFilter
                  onFilterChange={handleFilterChange}
                  currentFilter={statusFilter}
                  orderCounts={orderCounts}
                />
              </ComponentErrorBoundary>
            </motion.div>

            {/* Orders Grid */}
            <motion.div 
              variants={dashboardAnimations.statsCard}
              className="card"
            >
              <div className="touch-padding border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-900">
                    Pedidos ({filteredOrders.length})
                  </h3>
                  <div className="flex items-center space-x-2">
                    {statusFilter !== 'all' && (
                      <span className="badge badge-in-progress">
                        {statusFilter}
                      </span>
                    )}
                  </div>
                </div>
              </div>
              <ComponentErrorBoundary>
                <OrderGrid
                  orders={filteredOrders}
                  loading={loading}
                  onOrderClick={handleOrderClick}
                  activeUsers={activeUsers}
                  className="p-4"
                />
              </ComponentErrorBoundary>
            </motion.div>
          </motion.div>
        </main>
      </div>

      {/* Order Access Modal */}
      <OrderAccessLogin
        isOpen={isOrderAccessModalOpen}
        onClose={handleOrderAccessClose}
        order={selectedOrder}
        onSuccess={handleOrderAccessSuccess}
      />
    </div>
  );
}

export default Dashboard;