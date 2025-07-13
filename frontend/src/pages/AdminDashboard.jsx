import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import AdminLogin from '../components/AdminLogin';
import UserManagement from '../components/UserManagement';
import { api } from '../services/api';
import { useToast } from '../components/ToastContainer';

export default function AdminDashboard() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showLogin, setShowLogin] = useState(true);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [currentTab, setCurrentTab] = useState('dashboard');
  const navigate = useNavigate();
  const { showSuccess, showError } = useToast();

  useEffect(() => {
    if (isAuthenticated) {
      fetchStats();
    }
  }, [isAuthenticated]);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const response = await api.get('/orders/stats');
      setStats(response.data);
    } catch (err) {
      console.error('Error fetching stats:', err);
      showError('Erro ao carregar estatísticas');
    } finally {
      setLoading(false);
    }
  };

  const handleAdminLogin = () => {
    setIsAuthenticated(true);
    setShowLogin(false);
    showSuccess('Acesso administrativo autorizado');
  };

  const handleLoginCancel = () => {
    navigate('/');
  };

  const StatCard = ({ title, value, subtitle, icon, color = 'orange' }) => (
    <motion.div
      initial={{ scale: 0.95, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      whileHover={{ scale: 1.02 }}
      className="bg-white rounded-lg shadow-md p-6 border border-gray-200"
    >
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-medium text-gray-600 mb-2">{title}</h3>
          <p className={`text-3xl font-bold text-${color}-600`}>
            {value !== null && value !== undefined ? value : '--'}
          </p>
          {subtitle && (
            <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
          )}
        </div>
        <div className={`w-12 h-12 bg-${color}-100 rounded-lg flex items-center justify-center`}>
          {icon}
        </div>
      </div>
    </motion.div>
  );

  if (showLogin) {
    return (
      <AdminLogin
        onSuccess={handleAdminLogin}
        onCancel={handleLoginCancel}
      />
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="flex items-center justify-between mb-8"
        >
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Painel Administrativo</h1>
            <p className="text-gray-600 mt-1">Relatórios, estatísticas e gerenciamento do sistema</p>
          </div>
          <button
            onClick={() => navigate('/')}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            Voltar ao Dashboard
          </button>
        </motion.div>

        {/* Tab Navigation */}
        <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg mb-6">
          <button
            onClick={() => setCurrentTab('dashboard')}
            className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              currentTab === 'dashboard'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Dashboard
          </button>
          <button
            onClick={() => setCurrentTab('users')}
            className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              currentTab === 'users'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Usuários
          </button>
        </div>

        {/* Content */}
        {currentTab === 'users' ? (
          <UserManagement />
        ) : loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600"></div>
          </div>
        ) : (
          <>
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <StatCard
                title="Total de Pedidos"
                value={stats?.total_orders}
                icon={
                  <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14-7H5a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2V5a2 2 0 00-2-2z" />
                  </svg>
                }
              />
              
              <StatCard
                title="Em Andamento"
                value={stats?.orders_in_progress}
                subtitle={`${stats?.orders_pending || 0} pendentes`}
                color="blue"
                icon={
                  <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                }
              />
              
              <StatCard
                title="Concluídos"
                value={stats?.orders_completed}
                color="green"
                icon={
                  <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                }
              />
              
              <StatCard
                title="Tempo Médio"
                value={stats?.average_separation_time ? `${stats.average_separation_time.toFixed(1)}h` : '--'}
                subtitle="de separação"
                color="purple"
                icon={
                  <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                }
              />
            </div>

            {/* Items Stats */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
              <StatCard
                title="Total de Itens"
                value={stats?.total_items}
                icon={
                  <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                  </svg>
                }
              />
              
              <StatCard
                title="Itens Separados"
                value={stats?.items_separated}
                subtitle={stats?.total_items ? `${((stats.items_separated / stats.total_items) * 100).toFixed(1)}% do total` : ''}
                color="green"
                icon={
                  <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                }
              />
              
              <StatCard
                title="Em Compras"
                value={stats?.items_in_purchase}
                color="yellow"
                icon={
                  <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                  </svg>
                }
              />
            </div>

            {/* Action Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <motion.div
                whileHover={{ scale: 1.02 }}
                className="bg-white rounded-lg shadow-md p-6 border border-gray-200 cursor-pointer"
                onClick={() => setCurrentTab('users')}
              >
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-4.5a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">Gerenciar Usuários</h3>
                    <p className="text-gray-600 text-sm">Criar, editar e remover usuários</p>
                  </div>
                </div>
              </motion.div>

              <motion.div
                whileHover={{ scale: 1.02 }}
                className="bg-white rounded-lg shadow-md p-6 border border-gray-200 cursor-pointer"
                onClick={() => showError('Funcionalidade em desenvolvimento')}
              >
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                    <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">Relatórios</h3>
                    <p className="text-gray-600 text-sm">Gráficos e análises detalhadas</p>
                  </div>
                </div>
              </motion.div>

              <motion.div
                whileHover={{ scale: 1.02 }}
                className="bg-white rounded-lg shadow-md p-6 border border-gray-200 cursor-pointer"
                onClick={() => navigate('/purchase-items')}
              >
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                    <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">Tela de Compras</h3>
                    <p className="text-gray-600 text-sm">Gerenciar itens em compras</p>
                  </div>
                </div>
              </motion.div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}