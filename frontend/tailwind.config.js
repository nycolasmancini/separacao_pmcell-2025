/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
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
          DEFAULT: '#f97316', // orange-500
          dark: '#ea580c',    // orange-600
          light: '#fb923c',   // orange-400
        }
      },
      
      // Breakpoints customizados
      screens: {
        'xs': '475px',
        'tablet': '768px',   // Ponto específico para tablets
        'tablet-lg': '1024px', // Tablets grandes
      },
      
      // Espaçamentos otimizados para touch
      spacing: {
        'touch': '44px',     // Tamanho mínimo de touch target
        'touch-lg': '48px',  // Touch target maior
        '18': '4.5rem',      // 72px
        '22': '5.5rem',      // 88px
      },
      
      // Tamanhos de fonte otimizados
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
        'touch-sm': ['1rem', { lineHeight: '1.5rem' }],    // Para botões touch pequenos
        'touch-base': ['1.125rem', { lineHeight: '1.75rem' }], // Para botões touch normais
        'touch-lg': ['1.25rem', { lineHeight: '1.75rem' }],    // Para botões touch grandes
      },
      
      // Grid específico para tablets
      gridTemplateColumns: {
        'tablet-orders': 'repeat(auto-fit, minmax(300px, 1fr))',
        'tablet-dashboard': '250px 1fr',
        'tablet-cards': 'repeat(auto-fit, minmax(280px, 1fr))',
      },
      
      // Heights específicos
      height: {
        'screen-safe': 'calc(100vh - env(safe-area-inset-top) - env(safe-area-inset-bottom))',
        'tablet-nav': '60px',
        'tablet-content': 'calc(100vh - 60px)',
      },
      
      // Shadows otimizados
      boxShadow: {
        'touch': '0 2px 8px 0 rgba(0, 0, 0, 0.12)',
        'touch-lg': '0 4px 12px 0 rgba(0, 0, 0, 0.15)',
        'card-hover': '0 8px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)',
      },
      
      // Border radius otimizado para touch
      borderRadius: {
        'touch': '12px',
        'touch-sm': '8px',
        'touch-lg': '16px',
      },
      
      // Animações otimizadas
      animation: {
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'fade-in': 'fadeIn 0.2s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
        'bounce-soft': 'bounceSoft 0.6s ease-out',
      },
      
      keyframes: {
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        bounceSoft: {
          '0%': { transform: 'scale(0.95)' },
          '50%': { transform: 'scale(1.02)' },
          '100%': { transform: 'scale(1)' },
        },
      },
      
      // Z-index padronizado
      zIndex: {
        'dropdown': '1000',
        'sticky': '1020',
        'fixed': '1030',
        'modal-backdrop': '1040',
        'modal': '1050',
        'popover': '1060',
        'tooltip': '1070',
        'toast': '1080',
      }
    },
  },
  plugins: [
    // Plugin personalizado para touch targets
    function({ addUtilities }) {
      const touchUtilities = {
        '.touch-target': {
          minHeight: '44px',
          minWidth: '44px',
        },
        '.touch-target-lg': {
          minHeight: '48px',
          minWidth: '48px',
        },
        '.touch-padding': {
          padding: '12px',
        },
        '.touch-margin': {
          margin: '8px',
        },
        // Safe area para dispositivos com notch
        '.safe-top': {
          paddingTop: 'env(safe-area-inset-top)',
        },
        '.safe-bottom': {
          paddingBottom: 'env(safe-area-inset-bottom)',
        },
        '.safe-left': {
          paddingLeft: 'env(safe-area-inset-left)',
        },
        '.safe-right': {
          paddingRight: 'env(safe-area-inset-right)',
        },
        // Scroll otimizado para touch
        '.scroll-touch': {
          '-webkit-overflow-scrolling': 'touch',
          'scroll-behavior': 'smooth',
        },
      };
      
      addUtilities(touchUtilities);
    }
  ],
}