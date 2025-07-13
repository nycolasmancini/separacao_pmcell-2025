// Design System - PMCELL Separação de Pedidos
// Baseado nas especificações do CLAUDE.md

export const colors = {
  // Cores principais em tons de laranja
  primary: {
    50: '#fff7ed',
    100: '#ffedd5', 
    200: '#fed7aa',
    300: '#fdba74',
    400: '#fb923c',  // primary-light
    500: '#f97316',  // primary (DEFAULT)
    600: '#ea580c',  // primary-dark
    700: '#c2410c',
    800: '#9a3412',
    900: '#7c2d12',
  },
  
  // Cores de apoio
  gray: {
    50: '#f9fafb',   // background
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',
    600: '#4b5563',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',  // text principal
  },
  
  // Estados
  success: {
    50: '#f0fdf4',
    500: '#22c55e',
    600: '#16a34a',
  },
  
  error: {
    50: '#fef2f2',
    500: '#ef4444',
    600: '#dc2626',
  },
  
  warning: {
    50: '#fffbeb',
    500: '#f59e0b',
    600: '#d97706',
  },
  
  info: {
    50: '#eff6ff',
    500: '#3b82f6',
    600: '#2563eb',
  }
};

export const spacing = {
  xs: '0.5rem',   // 8px
  sm: '0.75rem',  // 12px
  md: '1rem',     // 16px
  lg: '1.5rem',   // 24px
  xl: '2rem',     // 32px
  '2xl': '3rem',  // 48px
  '3xl': '4rem',  // 64px
};

export const borderRadius = {
  sm: '0.25rem',   // 4px
  md: '0.375rem',  // 6px
  lg: '0.5rem',    // 8px
  xl: '0.75rem',   // 12px
  '2xl': '1rem',   // 16px
  full: '9999px',
};

export const fontSize = {
  xs: '0.75rem',    // 12px
  sm: '0.875rem',   // 14px
  base: '1rem',     // 16px
  lg: '1.125rem',   // 18px
  xl: '1.25rem',    // 20px
  '2xl': '1.5rem',  // 24px
  '3xl': '1.875rem', // 30px
  '4xl': '2.25rem',  // 36px
};

export const shadows = {
  sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
  base: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
  md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
  lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
  xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
};

// Transições e animações
export const animations = {
  transition: {
    fast: '150ms ease-in-out',
    normal: '200ms ease-in-out',
    slow: '300ms ease-in-out',
  },
  
  // Variantes para Framer Motion
  variants: {
    fadeIn: {
      initial: { opacity: 0 },
      animate: { opacity: 1 },
      exit: { opacity: 0 },
    },
    
    slideUp: {
      initial: { opacity: 0, y: 20 },
      animate: { opacity: 1, y: 0 },
      exit: { opacity: 0, y: -20 },
    },
    
    slideDown: {
      initial: { opacity: 0, y: -20 },
      animate: { opacity: 1, y: 0 },
      exit: { opacity: 0, y: 20 },
    },
    
    scaleIn: {
      initial: { opacity: 0, scale: 0.95 },
      animate: { opacity: 1, scale: 1 },
      exit: { opacity: 0, scale: 0.95 },
    },
    
    slideInRight: {
      initial: { opacity: 0, x: 100 },
      animate: { opacity: 1, x: 0 },
      exit: { opacity: 0, x: -100 },
    },
  },
  
  // Configurações de transição
  transition: {
    fast: { duration: 0.15 },
    normal: { duration: 0.2 },
    slow: { duration: 0.3 },
    spring: { type: "spring", stiffness: 300, damping: 30 },
  }
};

// Classes CSS utilitárias personalizadas
export const cssClasses = {
  // Botões
  button: {
    base: 'inline-flex items-center justify-center rounded-lg font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2',
    primary: 'bg-primary-500 hover:bg-primary-600 text-white focus:ring-primary-500',
    secondary: 'bg-gray-200 hover:bg-gray-300 text-gray-900 focus:ring-gray-500',
    danger: 'bg-red-500 hover:bg-red-600 text-white focus:ring-red-500',
    ghost: 'hover:bg-gray-100 text-gray-700 focus:ring-gray-500',
    sizes: {
      sm: 'px-3 py-1.5 text-sm',
      md: 'px-4 py-2 text-base',
      lg: 'px-6 py-3 text-lg',
    }
  },
  
  // Cards
  card: {
    base: 'bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden',
    hover: 'hover:shadow-lg hover:border-primary-200 transition-all duration-200',
    padding: {
      sm: 'p-4',
      md: 'p-6',
      lg: 'p-8',
    }
  },
  
  // Inputs
  input: {
    base: 'block w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-500 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500',
    error: 'border-red-500 focus:border-red-500 focus:ring-red-500',
  },
  
  // Status badges
  badge: {
    base: 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
    variants: {
      pending: 'bg-yellow-100 text-yellow-800',
      in_progress: 'bg-blue-100 text-blue-800', 
      completed: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800',
    }
  },
  
  // Layout
  container: 'mx-auto max-w-7xl px-4 sm:px-6 lg:px-8',
  section: 'py-8 sm:py-12',
};

// Breakpoints para responsividade
export const breakpoints = {
  sm: '640px',
  md: '768px',  // tablet
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
};

// Configurações específicas para tablet
export const tablet = {
  // Touch targets mínimos recomendados
  minTouchTarget: '44px',
  
  // Espaçamentos otimizados para touch
  spacing: {
    touchPadding: '12px',
    elementGap: '16px',
    sectionGap: '24px',
  },
  
  // Grid layouts
  grid: {
    orders: {
      columns: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
      gap: 'gap-6',
    },
    dashboard: {
      sidebar: 'md:w-64',
      content: 'md:ml-64',
    }
  }
};

export default {
  colors,
  spacing,
  borderRadius,
  fontSize,
  shadows,
  animations,
  cssClasses,
  breakpoints,
  tablet,
};