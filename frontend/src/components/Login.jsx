import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuthStore } from '../store/authStore';
import Logo from './Logo';
import { ButtonSpinner } from './LoadingSpinner';
import { useResponsive } from '../hooks/useResponsive';
import { loginAnimations } from '../utils/animations';

const PIN_LENGTH = 4;

function Login() {
  const [pin, setPin] = useState('');
  const [isShaking, setIsShaking] = useState(false);
  
  const { login, isLoading, error, clearError } = useAuthStore();
  const { isTabletUp, isTouchDevice } = useResponsive();

  useEffect(() => {
    if (error) {
      setIsShaking(true);
      setPin('');
      const timer = setTimeout(() => {
        setIsShaking(false);
        clearError();
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [error, clearError]);

  const handleNumberClick = (number) => {
    if (pin.length < PIN_LENGTH) {
      setPin(prev => prev + number);
    }
  };

  const handleDelete = () => {
    setPin(prev => prev.slice(0, -1));
  };

  const handleSubmit = async () => {
    if (pin.length === PIN_LENGTH) {
      await login(pin);
    }
  };

  // Auto-submit quando PIN estiver completo
  useEffect(() => {
    if (pin.length === PIN_LENGTH && !isLoading && !error) {
      handleSubmit();
    }
  }, [pin, isLoading, error]);

  const renderPinDisplay = () => {
    return (
      <div className="flex justify-center space-x-3 mb-8">
        {[...Array(PIN_LENGTH)].map((_, index) => (
          <motion.div
            key={index}
            className={`
              ${isTouchDevice ? 'w-5 h-5' : 'w-4 h-4'} 
              rounded-full border-2 transition-colors ${
              index < pin.length 
                ? 'bg-primary-500 border-primary-500' 
                : 'border-gray-300'
            }`}
            animate={isShaking ? { x: [-10, 10, -10, 10, 0] } : {}}
            transition={{ duration: 0.5 }}
          />
        ))}
      </div>
    );
  };

  const NumberButton = ({ number, onClick }) => (
    <motion.button
      onClick={() => onClick(number)}
      className={`
        ${isTouchDevice ? 'touch-target-lg' : 'w-16 h-16'} 
        rounded-touch bg-white border-2 border-gray-200 
        ${isTouchDevice ? 'text-touch-lg' : 'text-2xl'} 
        font-semibold text-gray-800 
        hover:bg-primary-50 hover:border-primary-300 
        active:bg-primary-100
        transition-all duration-200
        shadow-touch hover:shadow-touch-lg
      `}
      variants={loginAnimations.keyButton}
      whileTap="tap"
      whileHover="hover"
      disabled={isLoading}
    >
      {number}
    </motion.button>
  );

  const DeleteButton = () => (
    <motion.button
      onClick={handleDelete}
      className={`
        ${isTouchDevice ? 'touch-target-lg' : 'w-16 h-16'} 
        rounded-touch bg-gray-100 border-2 border-gray-200 
        flex items-center justify-center 
        hover:bg-gray-200 active:bg-gray-300
        transition-all duration-200
        shadow-touch hover:shadow-touch-lg
      `}
      variants={loginAnimations.keyButton}
      whileTap="tap"
      whileHover="hover"
      disabled={isLoading || pin.length === 0}
    >
      <svg 
        className={`${isTouchDevice ? 'w-7 h-7' : 'w-6 h-6'} text-gray-600`}
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
      >
        <path 
          strokeLinecap="round" 
          strokeLinejoin="round" 
          strokeWidth={2} 
          d="M12 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2M3 12l6.414 6.414a2 2 0 001.414.586H19a2 2 0 002-2V7a2 2 0 00-2-2h-8.172a2 2 0 00-1.414.586L3 12z" 
        />
      </svg>
    </motion.button>
  );

  return (
    <div className="min-h-screen bg-gradient-primary flex items-center justify-center p-4 safe-top safe-bottom">
      <motion.div
        variants={loginAnimations.container}
        initial="initial"
        animate="animate"
        className={`
          bg-white rounded-touch-lg shadow-xl 
          ${isTabletUp ? 'p-8 w-full max-w-md' : 'p-6 w-full max-w-sm'}
        `}
      >
        {/* Logo */}
        <motion.div
          variants={loginAnimations.logo}
          initial="initial"
          animate="animate"
          className="flex justify-center mb-8"
        >
          <Logo size={isTabletUp ? "lg" : "md"} />
        </motion.div>

        {/* PIN Display */}
        <div className="mb-6">
          <p className={`text-center text-gray-600 mb-4 ${isTouchDevice ? 'text-lg' : 'text-base'}`}>
            Digite seu PIN de acesso
          </p>
          {renderPinDisplay()}
        </div>

        {/* Error Message */}
        {error && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-red-50 border border-red-200 rounded-lg p-3 mb-6"
          >
            <p className="text-red-600 text-center text-sm">
              {error}
            </p>
          </motion.div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="text-center mb-6">
            <ButtonSpinner size="lg" className="mx-auto text-primary-500" />
            <p className="text-gray-600 text-sm mt-2">Verificando...</p>
          </div>
        )}

        {/* Numeric Keypad */}
        <motion.div
          variants={loginAnimations.keypad}
          initial="initial"
          animate="animate"
          className={`grid grid-cols-3 ${isTouchDevice ? 'gap-6' : 'gap-4'} mb-6`}
        >
          {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((number) => (
            <NumberButton
              key={number}
              number={number}
              onClick={handleNumberClick}
            />
          ))}
          
          {/* Empty space */}
          <div></div>
          
          {/* Zero */}
          <NumberButton number={0} onClick={handleNumberClick} />
          
          {/* Delete button */}
          <DeleteButton />
        </motion.div>

        {/* PIN Hints for Testing */}
        {process.env.NODE_ENV === 'development' && (
          <div className="text-center">
            <p className="text-xs text-gray-400 mb-2">Usuários de teste:</p>
            <div className="grid grid-cols-2 gap-2 text-xs text-gray-500">
              <div>João (1234) - Vendedor</div>
              <div>Maria (5678) - Separador</div>
              <div>Pedro (9012) - Separador</div>
              <div>Ana (3456) - Comprador</div>
              <div>Admin (0000) - Admin</div>
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
}

export default Login;