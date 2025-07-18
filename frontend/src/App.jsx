import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import { ToastProvider } from './components/ToastContainer';
import ErrorBoundary, { PageErrorBoundary } from './components/ErrorBoundary';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import NewOrder from './components/NewOrder';
import OrderSeparation from './components/OrderSeparation';
import PurchaseItems from './pages/PurchaseItems';
import AdminDashboard from './pages/AdminDashboard';
import ProtectedRoute from './components/ProtectedRoute';
import { debugLog, incrementCounter } from './utils/debug';

function App() {
  const { isAuthenticated } = useAuthStore();

  debugLog('app', 'RENDER', {
    isAuthenticated,
    renderCount: incrementCounter('appRender')
  });

  return (
    <ErrorBoundary>
      <ToastProvider>
        <BrowserRouter basename="/separacao_pmcell-2025">
          <div className="min-h-screen bg-gray-50 safe-top safe-bottom">
            <Routes>
              <Route 
                path="/login" 
                element={
                  isAuthenticated ? <Navigate to="/" replace /> : (
                    <PageErrorBoundary>
                      <Login />
                    </PageErrorBoundary>
                  )
                } 
              />
              <Route 
                path="/" 
                element={
                  <ProtectedRoute>
                    <PageErrorBoundary>
                      <Dashboard />
                    </PageErrorBoundary>
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/novo-pedido" 
                element={
                  <ProtectedRoute>
                    <PageErrorBoundary>
                      <NewOrder />
                    </PageErrorBoundary>
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/orders/:orderId/separation" 
                element={
                  <ProtectedRoute>
                    <PageErrorBoundary>
                      <OrderSeparation />
                    </PageErrorBoundary>
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/purchase-items" 
                element={
                  <ProtectedRoute>
                    <PageErrorBoundary>
                      <PurchaseItems />
                    </PageErrorBoundary>
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/admin" 
                element={
                  <ProtectedRoute>
                    <PageErrorBoundary>
                      <AdminDashboard />
                    </PageErrorBoundary>
                  </ProtectedRoute>
                } 
              />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </div>
        </BrowserRouter>
      </ToastProvider>
    </ErrorBoundary>
  );
}

export default App;
