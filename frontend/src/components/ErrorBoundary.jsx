import { Component } from 'react';
import { motion } from 'framer-motion';
import { ExclamationTriangleIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import Logo from './Logo';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false, 
      error: null, 
      errorInfo: null 
    };
  }

  static getDerivedStateFromError(error) {
    // Atualiza o state para mostrar a UI de erro
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log do erro para monitoramento
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    this.setState({
      error: error,
      errorInfo: errorInfo
    });

    // Aqui você pode enviar o erro para um serviço de monitoramento
    // como Sentry, LogRocket, etc.
    if (process.env.NODE_ENV === 'production') {
      // Sentry.captureException(error, { extra: errorInfo });
    }
  }

  handleReload = () => {
    // Recarregar a página
    window.location.reload();
  };

  handleReset = () => {
    // Resetar o state do error boundary
    this.setState({ 
      hasError: false, 
      error: null, 
      errorInfo: null 
    });
  };

  render() {
    if (this.state.hasError) {
      const { fallback: Fallback, showDetails = false } = this.props;
      
      // Se um fallback customizado foi fornecido, usar ele
      if (Fallback) {
        return (
          <Fallback
            error={this.state.error}
            errorInfo={this.state.errorInfo}
            onReset={this.handleReset}
            onReload={this.handleReload}
          />
        );
      }

      // UI de erro padrão
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
          <motion.div 
            className="max-w-md w-full"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
          >
            <div className="card card-hover p-8 text-center">
              {/* Logo */}
              <div className="flex justify-center mb-6">
                <Logo size="md" />
              </div>

              {/* Ícone de erro */}
              <motion.div
                className="flex justify-center mb-6"
                initial={{ rotate: -10 }}
                animate={{ rotate: 0 }}
                transition={{ delay: 0.2, duration: 0.3 }}
              >
                <div className="p-4 bg-red-100 rounded-full">
                  <ExclamationTriangleIcon className="w-12 h-12 text-red-600" />
                </div>
              </motion.div>

              {/* Título e descrição */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3, duration: 0.4 }}
              >
                <h1 className="text-2xl font-bold text-gray-900 mb-2">
                  Ops! Algo deu errado
                </h1>
                <p className="text-gray-600 mb-6">
                  Ocorreu um erro inesperado. Nossa equipe foi notificada e está trabalhando para resolver.
                </p>
              </motion.div>

              {/* Botões de ação */}
              <motion.div
                className="space-y-3"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4, duration: 0.4 }}
              >
                <button
                  onClick={this.handleReset}
                  className="btn-primary w-full"
                >
                  <ArrowPathIcon className="w-5 h-5 mr-2" />
                  Tentar Novamente
                </button>
                
                <button
                  onClick={this.handleReload}
                  className="btn-secondary w-full"
                >
                  Recarregar Página
                </button>
              </motion.div>

              {/* Detalhes do erro (apenas em desenvolvimento) */}
              {(process.env.NODE_ENV === 'development' || showDetails) && this.state.error && (
                <motion.details
                  className="mt-6 text-left"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.5, duration: 0.3 }}
                >
                  <summary className="cursor-pointer text-sm text-gray-500 hover:text-gray-700 transition-colors">
                    Detalhes técnicos
                  </summary>
                  <div className="mt-2 p-4 bg-gray-100 rounded-lg text-xs font-mono overflow-auto max-h-40 scrollbar-thin">
                    <div className="text-red-600 font-semibold mb-2">
                      {this.state.error.toString()}
                    </div>
                    <div className="text-gray-700 whitespace-pre-wrap">
                      {this.state.errorInfo.componentStack}
                    </div>
                  </div>
                </motion.details>
              )}

              {/* Info adicional */}
              <motion.div
                className="mt-6 pt-6 border-t border-gray-200"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.6, duration: 0.3 }}
              >
                <p className="text-xs text-gray-500">
                  Se o problema persistir, entre em contato com o suporte técnico.
                </p>
              </motion.div>
            </div>
          </motion.div>
        </div>
      );
    }

    // Se não há erro, renderizar os children normalmente
    return this.props.children;
  }
}

// Hook para usar com functional components
export function useErrorHandler() {
  const handleError = (error, errorInfo) => {
    // Log do erro
    console.error('Error caught by useErrorHandler:', error, errorInfo);
    
    // Em produção, enviar para serviço de monitoramento
    if (process.env.NODE_ENV === 'production') {
      // Sentry.captureException(error, { extra: errorInfo });
    }
  };

  return handleError;
}

// Componente de fallback simples para erros menores
export function ErrorFallback({ error, onReset, title = "Erro", message }) {
  return (
    <motion.div
      className="bg-red-50 border border-red-200 rounded-lg p-4"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.2 }}
    >
      <div className="flex items-start">
        <ExclamationTriangleIcon className="w-5 h-5 text-red-600 mt-0.5 mr-3 flex-shrink-0" />
        <div className="flex-1">
          <h3 className="text-sm font-medium text-red-800 mb-1">
            {title}
          </h3>
          <p className="text-sm text-red-700 mb-3">
            {message || 'Ocorreu um erro ao carregar este componente.'}
          </p>
          {onReset && (
            <button
              onClick={onReset}
              className="text-sm text-red-800 hover:text-red-900 underline transition-colors"
            >
              Tentar novamente
            </button>
          )}
        </div>
      </div>
      
      {/* Detalhes em desenvolvimento */}
      {process.env.NODE_ENV === 'development' && error && (
        <details className="mt-3">
          <summary className="cursor-pointer text-xs text-red-600 hover:text-red-700">
            Detalhes do erro
          </summary>
          <pre className="mt-2 text-xs text-red-800 bg-red-100 p-2 rounded overflow-auto max-h-32 scrollbar-thin">
            {error.toString()}
          </pre>
        </details>
      )}
    </motion.div>
  );
}

// Wrapper para páginas
export function PageErrorBoundary({ children }) {
  return (
    <ErrorBoundary>
      {children}
    </ErrorBoundary>
  );
}

// Wrapper para componentes específicos
export function ComponentErrorBoundary({ children, fallback }) {
  return (
    <ErrorBoundary fallback={fallback}>
      {children}
    </ErrorBoundary>
  );
}

export default ErrorBoundary;