import { motion } from 'framer-motion';
import { LogoIcon } from './Logo';

// Spinner básico
export function Spinner({ size = 'md', color = 'primary', className = '' }) {
  const sizes = {
    xs: 'w-3 h-3',
    sm: 'w-4 h-4', 
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12',
  };

  const colors = {
    primary: 'text-primary-500',
    white: 'text-white',
    gray: 'text-gray-500',
    current: 'text-current',
  };

  return (
    <motion.div
      className={`${sizes[size]} ${colors[color]} ${className}`}
      animate={{ rotate: 360 }}
      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
    >
      <svg
        className="w-full h-full"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
      >
        <path 
          strokeLinecap="round" 
          strokeLinejoin="round" 
          d="M12 2v4m0 12v4M4.93 4.93l2.83 2.83m8.49 8.49l2.83 2.83M2 12h4m12 0h4M4.93 19.07l2.83-2.83m8.49-8.49l2.83-2.83"
          className="opacity-25"
        />
        <path 
          strokeLinecap="round" 
          strokeLinejoin="round" 
          d="M12 2v4"
          className="opacity-75"
        />
      </svg>
    </motion.div>
  );
}

// Loading com logo PMCELL animado
export function LogoSpinner({ size = 'md', message, className = '' }) {
  const sizes = {
    sm: {
      logo: 'sm',
      container: 'py-8',
      text: 'text-sm',
    },
    md: {
      logo: 'md',
      container: 'py-12',
      text: 'text-base',
    },
    lg: {
      logo: 'lg', 
      container: 'py-16',
      text: 'text-lg',
    },
  };

  const currentSize = sizes[size];

  return (
    <motion.div
      className={`flex flex-col items-center justify-center ${currentSize.container} ${className}`}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      {/* Logo animado */}
      <motion.div
        animate={{ 
          rotate: [0, 360],
          scale: [1, 1.1, 1],
        }}
        transition={{ 
          rotate: { duration: 2, repeat: Infinity, ease: "linear" },
          scale: { duration: 1, repeat: Infinity, ease: "easeInOut" }
        }}
      >
        <LogoIcon size={currentSize.logo} />
      </motion.div>

      {/* Mensagem opcional */}
      {message && (
        <motion.p
          className={`${currentSize.text} text-gray-600 mt-4 font-medium`}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.3 }}
        >
          {message}
        </motion.p>
      )}

      {/* Dots animados */}
      <motion.div 
        className="flex space-x-1 mt-3"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4, duration: 0.3 }}
      >
        {[0, 1, 2].map((i) => (
          <motion.div
            key={i}
            className="w-2 h-2 bg-primary-500 rounded-full"
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.7, 1, 0.7],
            }}
            transition={{
              duration: 0.6,
              repeat: Infinity,
              delay: i * 0.2,
              ease: "easeInOut"
            }}
          />
        ))}
      </motion.div>
    </motion.div>
  );
}

// Loading de tela cheia
export function FullPageLoader({ message = "Carregando..." }) {
  return (
    <div className="fixed inset-0 bg-white bg-opacity-90 backdrop-blur-sm z-50 flex items-center justify-center">
      <LogoSpinner size="lg" message={message} />
    </div>
  );
}

// Loading inline para botões
export function ButtonSpinner({ size = 'sm', className = '' }) {
  return (
    <Spinner 
      size={size} 
      color="current"
      className={`animate-spin ${className}`}
    />
  );
}

// Loading com progresso circular
export function CircularProgress({ 
  progress = 0, 
  size = 'md', 
  showPercentage = true,
  className = '' 
}) {
  const sizes = {
    sm: { width: 40, height: 40, strokeWidth: 3, fontSize: 'text-xs' },
    md: { width: 60, height: 60, strokeWidth: 4, fontSize: 'text-sm' },
    lg: { width: 80, height: 80, strokeWidth: 5, fontSize: 'text-base' },
  };

  const currentSize = sizes[size];
  const radius = (currentSize.width - currentSize.strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const strokeDashoffset = circumference - (progress / 100) * circumference;

  return (
    <div className={`relative ${className}`}>
      <svg
        width={currentSize.width}
        height={currentSize.height}
        className="transform -rotate-90"
      >
        {/* Background circle */}
        <circle
          cx={currentSize.width / 2}
          cy={currentSize.height / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth={currentSize.strokeWidth}
          fill="none"
          className="text-gray-200"
        />
        
        {/* Progress circle */}
        <motion.circle
          cx={currentSize.width / 2}
          cy={currentSize.height / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth={currentSize.strokeWidth}
          fill="none"
          strokeLinecap="round"
          className="text-primary-500"
          style={{
            strokeDasharray: circumference,
          }}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset }}
          transition={{ duration: 0.5, ease: "easeInOut" }}
        />
      </svg>
      
      {/* Percentage text */}
      {showPercentage && (
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={`font-semibold text-gray-700 ${currentSize.fontSize}`}>
            {Math.round(progress)}%
          </span>
        </div>
      )}
    </div>
  );
}

// Loading overlay para cards/componentes
export function LoadingOverlay({ 
  show = true, 
  message,
  blur = true,
  className = '' 
}) {
  if (!show) return null;

  return (
    <motion.div
      className={`
        absolute inset-0 
        ${blur ? 'backdrop-blur-sm' : ''} 
        bg-white bg-opacity-80 
        flex items-center justify-center 
        z-10 
        ${className}
      `}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.2 }}
    >
      <div className="text-center">
        <Spinner size="lg" />
        {message && (
          <p className="mt-3 text-sm text-gray-600 font-medium">
            {message}
          </p>
        )}
      </div>
    </motion.div>
  );
}

// Loading com wave animation
export function WaveLoader({ className = '' }) {
  return (
    <div className={`flex items-center justify-center space-x-1 ${className}`}>
      {[0, 1, 2, 3, 4].map((i) => (
        <motion.div
          key={i}
          className="w-2 h-8 bg-primary-500 rounded-full"
          animate={{
            scaleY: [1, 0.5, 1],
            opacity: [0.7, 1, 0.7],
          }}
          transition={{
            duration: 0.8,
            repeat: Infinity,
            delay: i * 0.1,
            ease: "easeInOut"
          }}
        />
      ))}
    </div>
  );
}

export default Spinner;