import { useState, useEffect } from 'react';

// Breakpoints padrão (sincronizado com Tailwind)
const breakpoints = {
  xs: 475,
  sm: 640,
  md: 768,
  tablet: 768,
  lg: 1024,
  'tablet-lg': 1024,
  xl: 1280,
  '2xl': 1536,
};

export function useResponsive() {
  const [windowSize, setWindowSize] = useState({
    width: typeof window !== 'undefined' ? window.innerWidth : 0,
    height: typeof window !== 'undefined' ? window.innerHeight : 0,
  });

  const [orientation, setOrientation] = useState('portrait');

  useEffect(() => {
    function handleResize() {
      const width = window.innerWidth;
      const height = window.innerHeight;
      
      setWindowSize({ width, height });
      setOrientation(width > height ? 'landscape' : 'portrait');
    }

    // Event listener para mudanças de tamanho
    window.addEventListener('resize', handleResize);
    
    // Event listener para mudanças de orientação
    window.addEventListener('orientationchange', () => {
      // Delay para aguardar mudança de orientação completar
      setTimeout(handleResize, 100);
    });

    // Chamar uma vez para definir estado inicial
    handleResize();

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('orientationchange', handleResize);
    };
  }, []);

  // Função para verificar se está acima de um breakpoint
  const isAbove = (breakpoint) => {
    const minWidth = breakpoints[breakpoint];
    return windowSize.width >= minWidth;
  };

  // Função para verificar se está abaixo de um breakpoint
  const isBelow = (breakpoint) => {
    const maxWidth = breakpoints[breakpoint];
    return windowSize.width < maxWidth;
  };

  // Função para verificar se está entre dois breakpoints
  const isBetween = (minBreakpoint, maxBreakpoint) => {
    const minWidth = breakpoints[minBreakpoint];
    const maxWidth = breakpoints[maxBreakpoint];
    return windowSize.width >= minWidth && windowSize.width < maxWidth;
  };

  // Estados específicos para diferentes dispositivos
  const isMobile = windowSize.width < breakpoints.md;
  const isTablet = windowSize.width >= breakpoints.tablet && windowSize.width < breakpoints['tablet-lg'];
  const isTabletUp = windowSize.width >= breakpoints.tablet;
  const isDesktop = windowSize.width >= breakpoints['tablet-lg'];
  const isLargeScreen = windowSize.width >= breakpoints.xl;

  // Detecção de dispositivos touch
  const [isTouchDevice, setIsTouchDevice] = useState(false);

  useEffect(() => {
    const checkTouchDevice = () => {
      return (
        'ontouchstart' in window ||
        navigator.maxTouchPoints > 0 ||
        navigator.msMaxTouchPoints > 0
      );
    };

    setIsTouchDevice(checkTouchDevice());
  }, []);

  // Detecção de user agent para tablets específicos
  const isIPad = /iPad|Macintosh/i.test(navigator.userAgent) && isTouchDevice;
  const isAndroidTablet = /Android/i.test(navigator.userAgent) && !/Mobile/i.test(navigator.userAgent);
  const isActualTablet = isIPad || isAndroidTablet || (isTablet && isTouchDevice);

  // Grid layouts baseados no tamanho da tela
  const getGridCols = (sizes = {}) => {
    const defaults = {
      mobile: 1,
      tablet: 2,
      desktop: 3,
      large: 4,
    };

    const config = { ...defaults, ...sizes };

    if (isMobile) return config.mobile;
    if (isTablet) return config.tablet;
    if (isDesktop && !isLargeScreen) return config.desktop;
    return config.large;
  };

  // Classe CSS responsiva para grid
  const getGridClass = (sizes = {}) => {
    const cols = getGridCols(sizes);
    return `grid-cols-${cols}`;
  };

  // Configurações específicas para componentes
  const getComponentConfig = (component) => {
    const configs = {
      sidebar: {
        mobile: { position: 'overlay', width: '80%' },
        tablet: { position: 'overlay', width: '320px' },
        desktop: { position: 'fixed', width: '256px' },
      },
      
      orderCard: {
        mobile: { size: 'full', padding: '4' },
        tablet: { size: 'auto', padding: '6' },
        desktop: { size: 'auto', padding: '6' },
      },
      
      pagination: {
        mobile: { showLabels: false, itemsPerPage: 10 },
        tablet: { showLabels: true, itemsPerPage: 15 },
        desktop: { showLabels: true, itemsPerPage: 20 },
      },
      
      modal: {
        mobile: { fullScreen: true, padding: '4' },
        tablet: { fullScreen: false, padding: '6', maxWidth: '2xl' },
        desktop: { fullScreen: false, padding: '8', maxWidth: '4xl' },
      },
    };

    const config = configs[component] || {};
    
    if (isMobile) return config.mobile || {};
    if (isTablet || isActualTablet) return config.tablet || {};
    return config.desktop || {};
  };

  // Função para obter classes CSS responsivas
  const getResponsiveClasses = (classes = {}) => {
    const defaults = {
      mobile: '',
      tablet: '',
      desktop: '',
    };

    const config = { ...defaults, ...classes };
    
    let result = config.mobile || '';
    
    if (isTabletUp && config.tablet) {
      result += ` tablet:${config.tablet}`;
    }
    
    if (isDesktop && config.desktop) {
      result += ` lg:${config.desktop}`;
    }
    
    return result.trim();
  };

  return {
    // Dimensões da tela
    windowSize,
    orientation,
    
    // Estados de dispositivos
    isMobile,
    isTablet,
    isTabletUp,
    isActualTablet,
    isDesktop,
    isLargeScreen,
    isTouchDevice,
    isIPad,
    isAndroidTablet,
    
    // Funções de breakpoint
    isAbove,
    isBelow,
    isBetween,
    
    // Utilitários para grid
    getGridCols,
    getGridClass,
    
    // Configurações de componentes
    getComponentConfig,
    getResponsiveClasses,
    
    // Breakpoints disponíveis
    breakpoints,
  };
}

// Hook para media queries específicas
export function useMediaQuery(query) {
  const [matches, setMatches] = useState(false);

  useEffect(() => {
    const media = window.matchMedia(query);
    
    if (media.matches !== matches) {
      setMatches(media.matches);
    }
    
    const listener = (event) => setMatches(event.matches);
    
    // Usar addListener para compatibilidade com navegadores mais antigos
    if (media.addListener) {
      media.addListener(listener);
    } else {
      media.addEventListener('change', listener);
    }
    
    return () => {
      if (media.removeListener) {
        media.removeListener(listener);
      } else {
        media.removeEventListener('change', listener);
      }
    };
  }, [matches, query]);

  return matches;
}

// Hook para orientação específica
export function useOrientation() {
  const [orientation, setOrientation] = useState(
    window.innerWidth > window.innerHeight ? 'landscape' : 'portrait'
  );

  useEffect(() => {
    const handleOrientationChange = () => {
      // Pequeno delay para aguardar a mudança completar
      setTimeout(() => {
        setOrientation(
          window.innerWidth > window.innerHeight ? 'landscape' : 'portrait'
        );
      }, 100);
    };

    window.addEventListener('orientationchange', handleOrientationChange);
    window.addEventListener('resize', handleOrientationChange);

    return () => {
      window.removeEventListener('orientationchange', handleOrientationChange);
      window.removeEventListener('resize', handleOrientationChange);
    };
  }, []);

  return orientation;
}

// Hook específico para detectar tablets
export function useIsTablet() {
  const { isActualTablet, isTablet, isTouchDevice } = useResponsive();
  
  // Lógica mais refinada para detectar tablets
  const isTabletDevice = () => {
    // iPad
    if (/iPad|Macintosh/i.test(navigator.userAgent) && isTouchDevice) {
      return true;
    }
    
    // Android tablets
    if (/Android/i.test(navigator.userAgent) && !/Mobile/i.test(navigator.userAgent)) {
      return true;
    }
    
    // Tablets Windows/Surface
    if (/Windows/i.test(navigator.userAgent) && isTouchDevice && isTablet) {
      return true;
    }
    
    // Fallback para telas entre 768px e 1024px com touch
    return isTablet && isTouchDevice;
  };

  return isTabletDevice();
}

export default useResponsive;