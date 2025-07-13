import { motion } from 'framer-motion';

function Logo({ size = 'md', variant = 'default', className = '' }) {
  const sizes = {
    sm: {
      container: 'h-8',
      icon: 'w-8 h-8',
      text: 'text-lg',
      subtitle: 'text-xs',
    },
    md: {
      container: 'h-12',
      icon: 'w-12 h-12', 
      text: 'text-2xl',
      subtitle: 'text-sm',
    },
    lg: {
      container: 'h-16',
      icon: 'w-16 h-16',
      text: 'text-3xl',
      subtitle: 'text-base',
    },
  };

  const variants = {
    default: {
      iconBg: 'bg-gradient-primary',
      iconText: 'text-white',
      mainText: 'text-gray-900',
      subtitle: 'text-gray-600',
    },
    white: {
      iconBg: 'bg-white',
      iconText: 'text-primary-500',
      mainText: 'text-white',
      subtitle: 'text-gray-200',
    },
    minimal: {
      iconBg: 'bg-primary-500',
      iconText: 'text-white',
      mainText: 'text-gray-900',
      subtitle: 'text-gray-600',
    }
  };

  const currentSize = sizes[size];
  const currentVariant = variants[variant];

  return (
    <motion.div 
      className={`flex items-center space-x-3 ${currentSize.container} ${className}`}
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
    >
      {/* Ícone/Logo */}
      <motion.div 
        className={`
          ${currentSize.icon} 
          ${currentVariant.iconBg} 
          rounded-xl 
          flex items-center justify-center 
          shadow-lg
          relative overflow-hidden
        `}
        whileHover={{ scale: 1.05 }}
        transition={{ duration: 0.2 }}
      >
        {/* Background pattern */}
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-1 right-1 w-2 h-2 bg-white rounded-full"></div>
          <div className="absolute bottom-1 left-1 w-1 h-1 bg-white rounded-full"></div>
        </div>
        
        {/* Ícone principal - P estilizado */}
        <motion.span 
          className={`${currentVariant.iconText} font-bold ${currentSize.text} relative z-10`}
          initial={{ rotateY: -90 }}
          animate={{ rotateY: 0 }}
          transition={{ delay: 0.2, duration: 0.5 }}
        >
          P
        </motion.span>
      </motion.div>

      {/* Texto */}
      <div className="flex flex-col justify-center">
        <motion.h1 
          className={`${currentVariant.mainText} ${currentSize.text} font-bold leading-tight`}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3, duration: 0.4 }}
        >
          PMCELL
        </motion.h1>
        <motion.p 
          className={`${currentVariant.subtitle} ${currentSize.subtitle} font-medium leading-tight`}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4, duration: 0.4 }}
        >
          Separação de Pedidos
        </motion.p>
      </div>
    </motion.div>
  );
}

// Versão compacta apenas com ícone
export function LogoIcon({ size = 'md', variant = 'default', className = '' }) {
  const sizes = {
    sm: 'w-8 h-8 text-lg',
    md: 'w-12 h-12 text-2xl', 
    lg: 'w-16 h-16 text-3xl',
  };

  const variants = {
    default: {
      bg: 'bg-gradient-primary',
      text: 'text-white',
    },
    white: {
      bg: 'bg-white',
      text: 'text-primary-500',
    },
    minimal: {
      bg: 'bg-primary-500',
      text: 'text-white',
    }
  };

  const currentSize = sizes[size];
  const currentVariant = variants[variant];

  return (
    <motion.div 
      className={`
        ${currentSize}
        ${currentVariant.bg} 
        rounded-xl 
        flex items-center justify-center 
        shadow-lg
        relative overflow-hidden
        ${className}
      `}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      transition={{ duration: 0.2 }}
    >
      {/* Background pattern */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute top-1 right-1 w-2 h-2 bg-white rounded-full"></div>
        <div className="absolute bottom-1 left-1 w-1 h-1 bg-white rounded-full"></div>
      </div>
      
      {/* Ícone principal */}
      <span className={`${currentVariant.text} font-bold relative z-10`}>
        P
      </span>
    </motion.div>
  );
}

// Versão texto apenas (para headers simples)
export function LogoText({ size = 'md', variant = 'default', className = '' }) {
  const sizes = {
    sm: {
      main: 'text-lg',
      sub: 'text-xs',
    },
    md: {
      main: 'text-2xl',
      sub: 'text-sm',
    },
    lg: {
      main: 'text-3xl',
      sub: 'text-base',
    },
  };

  const variants = {
    default: {
      main: 'text-gray-900',
      sub: 'text-gray-600',
    },
    white: {
      main: 'text-white',
      sub: 'text-gray-200',
    },
    primary: {
      main: 'text-gradient-primary',
      sub: 'text-primary-600',
    }
  };

  const currentSize = sizes[size];
  const currentVariant = variants[variant];

  return (
    <div className={`flex flex-col ${className}`}>
      <motion.h1 
        className={`${currentVariant.main} ${currentSize.main} font-bold leading-tight`}
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        PMCELL
      </motion.h1>
      <motion.p 
        className={`${currentVariant.sub} ${currentSize.sub} font-medium leading-tight`}
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1, duration: 0.3 }}
      >
        Separação de Pedidos
      </motion.p>
    </div>
  );
}

export default Logo;