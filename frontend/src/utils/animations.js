// Utilitários de animação com Framer Motion
// Baseado no design system em src/styles/theme.js

// Variantes de entrada e saída
export const fadeVariants = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
};

export const slideUpVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
};

export const slideDownVariants = {
  initial: { opacity: 0, y: -20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: 20 },
};

export const slideInRightVariants = {
  initial: { opacity: 0, x: 100 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -100 },
};

export const slideInLeftVariants = {
  initial: { opacity: 0, x: -100 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: 100 },
};

export const scaleVariants = {
  initial: { opacity: 0, scale: 0.95 },
  animate: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.95 },
};

export const scaleInVariants = {
  initial: { opacity: 0, scale: 0.8 },
  animate: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.8 },
};

// Variantes para listas (stagger)
export const staggerContainerVariants = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.1,
    },
  },
  exit: {
    transition: {
      staggerChildren: 0.05,
      staggerDirection: -1,
    },
  },
};

export const staggerItemVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
};

// Variantes para cards
export const cardVariants = {
  initial: { opacity: 0, y: 20, scale: 0.95 },
  animate: { 
    opacity: 1, 
    y: 0, 
    scale: 1,
    transition: {
      duration: 0.3,
      ease: "easeOut"
    }
  },
  exit: { 
    opacity: 0, 
    y: -20, 
    scale: 0.95,
    transition: {
      duration: 0.2,
      ease: "easeIn"
    }
  },
  hover: {
    y: -5,
    scale: 1.02,
    transition: {
      duration: 0.2,
      ease: "easeOut"
    }
  },
  tap: {
    scale: 0.98,
    transition: {
      duration: 0.1,
      ease: "easeInOut"
    }
  }
};

// Variantes para botões
export const buttonVariants = {
  initial: { scale: 1 },
  hover: { 
    scale: 1.05,
    transition: { duration: 0.2, ease: "easeOut" }
  },
  tap: { 
    scale: 0.95,
    transition: { duration: 0.1, ease: "easeInOut" }
  },
  disabled: {
    scale: 1,
    opacity: 0.6,
    transition: { duration: 0.2 }
  }
};

// Variantes para modais
export const modalVariants = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
};

export const modalContentVariants = {
  initial: { opacity: 0, scale: 0.9, y: 20 },
  animate: { 
    opacity: 1, 
    scale: 1, 
    y: 0,
    transition: {
      duration: 0.3,
      ease: "easeOut"
    }
  },
  exit: { 
    opacity: 0, 
    scale: 0.9, 
    y: 20,
    transition: {
      duration: 0.2,
      ease: "easeIn"
    }
  },
};

// Variantes para sidebar
export const sidebarVariants = {
  open: {
    x: 0,
    transition: {
      duration: 0.3,
      ease: "easeOut"
    }
  },
  closed: {
    x: "-100%",
    transition: {
      duration: 0.3,
      ease: "easeIn"
    }
  }
};

// Variantes para progress bars
export const progressVariants = {
  initial: { width: 0 },
  animate: (progress) => ({
    width: `${progress}%`,
    transition: {
      duration: 0.5,
      ease: "easeOut"
    }
  })
};

// Variantes para notificações/toasts
export const toastVariants = {
  initial: { opacity: 0, x: 100, scale: 0.95 },
  animate: { 
    opacity: 1, 
    x: 0, 
    scale: 1,
    transition: {
      duration: 0.3,
      ease: "easeOut"
    }
  },
  exit: { 
    opacity: 0, 
    x: 100, 
    scale: 0.95,
    transition: {
      duration: 0.2,
      ease: "easeIn"
    }
  },
};

// Configurações de transição
export const transitions = {
  fast: { duration: 0.15, ease: "easeInOut" },
  normal: { duration: 0.2, ease: "easeInOut" },
  slow: { duration: 0.3, ease: "easeInOut" },
  spring: { type: "spring", stiffness: 300, damping: 30 },
  springBouncy: { type: "spring", stiffness: 400, damping: 25 },
  springSoft: { type: "spring", stiffness: 200, damping: 35 },
};

// Easing customizado
export const easings = {
  easeOutCubic: [0.33, 1, 0.68, 1],
  easeInCubic: [0.32, 0, 0.67, 0],
  easeInOutCubic: [0.65, 0, 0.35, 1],
  easeOutQuart: [0.25, 1, 0.5, 1],
  easeInOutQuart: [0.76, 0, 0.24, 1],
};

// Funções utilitárias para animações
export const createStaggerAnimation = (children, staggerDelay = 0.1) => ({
  animate: {
    transition: {
      staggerChildren: staggerDelay,
      delayChildren: 0.1,
    },
  },
});

export const createHoverAnimation = (scale = 1.05, duration = 0.2) => ({
  hover: {
    scale,
    transition: { duration, ease: "easeOut" }
  }
});

export const createTapAnimation = (scale = 0.95, duration = 0.1) => ({
  tap: {
    scale,
    transition: { duration, ease: "easeInOut" }
  }
});

// Animações específicas para componentes
export const orderCardAnimations = {
  container: {
    ...cardVariants,
    hover: {
      ...cardVariants.hover,
      boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
    }
  },
  progressBar: {
    initial: { width: 0 },
    animate: (progress) => ({
      width: `${progress}%`,
      transition: {
        duration: 0.8,
        ease: "easeOut",
        delay: 0.3
      }
    })
  },
  badge: {
    initial: { scale: 0, opacity: 0 },
    animate: { 
      scale: 1, 
      opacity: 1,
      transition: {
        duration: 0.2,
        ease: "easeOut",
        delay: 0.5
      }
    }
  }
};

export const dashboardAnimations = {
  container: staggerContainerVariants,
  statsCard: {
    initial: { opacity: 0, y: 20 },
    animate: { 
      opacity: 1, 
      y: 0,
      transition: {
        duration: 0.4,
        ease: "easeOut"
      }
    },
    hover: {
      y: -2,
      transition: { duration: 0.2 }
    }
  },
  filterButton: {
    initial: { scale: 1 },
    animate: { scale: 1 },
    hover: { scale: 1.03 },
    tap: { scale: 0.97 },
    active: { 
      backgroundColor: "#f97316",
      color: "#ffffff",
      transition: { duration: 0.2 }
    }
  }
};

export const separationAnimations = {
  itemRow: {
    initial: { opacity: 0, x: -20 },
    animate: { 
      opacity: 1, 
      x: 0,
      transition: {
        duration: 0.3,
        ease: "easeOut"
      }
    },
    hover: {
      backgroundColor: "#f9fafb",
      transition: { duration: 0.15 }
    },
    separated: {
      backgroundColor: "#f0fdf4",
      transition: { duration: 0.3 }
    }
  },
  checkbox: {
    initial: { scale: 1 },
    tap: { scale: 0.9 },
    checked: {
      scale: [1, 1.2, 1],
      transition: { duration: 0.3 }
    }
  },
  progressUpdate: {
    initial: { scale: 1 },
    animate: {
      scale: [1, 1.05, 1],
      transition: { duration: 0.4 }
    }
  }
};

// Animações para página de login
export const loginAnimations = {
  container: {
    initial: { opacity: 0, scale: 0.9 },
    animate: { 
      opacity: 1, 
      scale: 1,
      transition: {
        duration: 0.4,
        ease: "easeOut"
      }
    }
  },
  logo: {
    initial: { opacity: 0, y: -30 },
    animate: { 
      opacity: 1, 
      y: 0,
      transition: {
        duration: 0.5,
        ease: "easeOut",
        delay: 0.2
      }
    }
  },
  keypad: {
    initial: { opacity: 0, y: 20 },
    animate: { 
      opacity: 1, 
      y: 0,
      transition: {
        duration: 0.4,
        ease: "easeOut",
        delay: 0.4
      }
    }
  },
  keyButton: {
    initial: { scale: 1 },
    hover: { 
      scale: 1.05,
      backgroundColor: "#f97316",
      color: "#ffffff",
      transition: { duration: 0.15 }
    },
    tap: { 
      scale: 0.95,
      transition: { duration: 0.1 }
    }
  }
};

export default {
  // Variantes
  fadeVariants,
  slideUpVariants,
  slideDownVariants,
  slideInRightVariants,
  slideInLeftVariants,
  scaleVariants,
  scaleInVariants,
  staggerContainerVariants,
  staggerItemVariants,
  cardVariants,
  buttonVariants,
  modalVariants,
  modalContentVariants,
  sidebarVariants,
  progressVariants,
  toastVariants,
  
  // Transições
  transitions,
  easings,
  
  // Funções utilitárias
  createStaggerAnimation,
  createHoverAnimation,
  createTapAnimation,
  
  // Animações específicas
  orderCardAnimations,
  dashboardAnimations,
  separationAnimations,
  loginAnimations,
};