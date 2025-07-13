import { useState } from 'react';
import { motion } from 'framer-motion';

export default function AdminLogin({ onSuccess, onCancel }) {
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    // Admin password check
    if (password === 'thmpv321') {
      setTimeout(() => {
        setIsLoading(false);
        onSuccess();
      }, 1000);
    } else {
      setTimeout(() => {
        setIsLoading(false);
        setError('Senha incorreta');
        setPassword('');
      }, 1000);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md mx-4"
      >
        <div className="text-center mb-6">
          <div className="w-16 h-16 bg-orange-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m0 0v2m0-2h2m-2 0H10m6-4h.01M8 11h.01M12 7h.01M8 15h.01M16 15h.01M21 12c0 4.97-4.03 9-9 9s-9-4.03-9-9 4.03-9 9-9 9 4.03 9 9z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Acesso Administrativo</h2>
          <p className="text-gray-600">Digite a senha de administrador para continuar</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
              Senha do Administrador
            </label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={`
                w-full px-4 py-3 border rounded-lg text-center text-lg font-mono
                focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500
                ${error ? 'border-red-300 bg-red-50' : 'border-gray-300'}
              `}
              placeholder="Digite a senha"
              autoFocus
              disabled={isLoading}
            />
            {error && (
              <motion.p
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-red-600 text-sm mt-2 text-center"
              >
                {error}
              </motion.p>
            )}
          </div>

          <div className="flex space-x-3">
            <button
              type="button"
              onClick={onCancel}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              disabled={isLoading}
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={!password || isLoading}
              className={`
                flex-1 px-4 py-3 rounded-lg text-white font-medium transition-colors
                ${password && !isLoading
                  ? 'bg-orange-600 hover:bg-orange-700'
                  : 'bg-gray-300 cursor-not-allowed'
                }
              `}
            >
              {isLoading ? (
                <div className="flex items-center justify-center">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                  Verificando...
                </div>
              ) : (
                'Acessar'
              )}
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  );
}