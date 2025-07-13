import { motion } from 'framer-motion';

// Skeleton básico
export function Skeleton({ 
  width = 'w-full', 
  height = 'h-4', 
  className = '',
  animated = true 
}) {
  const baseClasses = `bg-gray-200 rounded ${width} ${height} ${className}`;
  
  if (!animated) {
    return <div className={baseClasses} />;
  }

  return (
    <motion.div
      className={baseClasses}
      animate={{
        opacity: [0.5, 1, 0.5],
      }}
      transition={{
        duration: 1.5,
        repeat: Infinity,
        ease: "easeInOut"
      }}
    />
  );
}

// Skeleton com shimmer effect
export function ShimmerSkeleton({ 
  width = 'w-full', 
  height = 'h-4', 
  className = '' 
}) {
  return (
    <div className={`relative overflow-hidden bg-gray-200 rounded ${width} ${height} ${className}`}>
      <motion.div
        className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white to-transparent opacity-60"
        animate={{
          x: ['100%', '-100%'],
        }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          ease: "linear"
        }}
      />
    </div>
  );
}

// Skeleton para cards de pedidos
export function OrderCardSkeleton({ className = '' }) {
  return (
    <div className={`card p-6 ${className}`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <Skeleton width="w-24" height="h-5" className="mb-2" />
          <Skeleton width="w-32" height="h-4" />
        </div>
        <Skeleton width="w-16" height="h-6" />
      </div>

      {/* Cliente e Vendedor */}
      <div className="space-y-3 mb-4">
        <div>
          <Skeleton width="w-16" height="h-3" className="mb-1" />
          <Skeleton width="w-40" height="h-4" />
        </div>
        <div>
          <Skeleton width="w-20" height="h-3" className="mb-1" />
          <Skeleton width="w-32" height="h-4" />
        </div>
      </div>

      {/* Valor e Progresso */}
      <div className="space-y-3 mb-4">
        <div className="flex justify-between items-center">
          <Skeleton width="w-12" height="h-3" />
          <Skeleton width="w-20" height="h-4" />
        </div>
        <div>
          <Skeleton width="w-full" height="h-2" className="mb-1" />
          <div className="flex justify-between">
            <Skeleton width="w-16" height="h-3" />
            <Skeleton width="w-12" height="h-3" />
          </div>
        </div>
      </div>

      {/* Footer com avatares */}
      <div className="flex items-center justify-between pt-4 border-t border-gray-100">
        <div className="flex -space-x-2">
          <Skeleton width="w-8" height="h-8" className="rounded-full" />
          <Skeleton width="w-8" height="h-8" className="rounded-full" />
        </div>
        <Skeleton width="w-16" height="h-3" />
      </div>
    </div>
  );
}

// Skeleton para lista de itens
export function ItemListSkeleton({ items = 5, className = '' }) {
  return (
    <div className={`space-y-2 ${className}`}>
      {Array.from({ length: items }).map((_, i) => (
        <div key={i} className="flex items-center p-3 bg-white rounded-lg">
          <Skeleton width="w-6" height="h-6" className="mr-3" />
          <div className="flex-1">
            <Skeleton width="w-48" height="h-4" className="mb-1" />
            <Skeleton width="w-24" height="h-3" />
          </div>
          <Skeleton width="w-8" height="h-8" className="rounded-full" />
        </div>
      ))}
    </div>
  );
}

// Skeleton para cabeçalho
export function HeaderSkeleton({ className = '' }) {
  return (
    <div className={`flex items-center justify-between p-4 bg-white ${className}`}>
      <div className="flex items-center space-x-3">
        <Skeleton width="w-10" height="h-10" className="rounded-full" />
        <div>
          <Skeleton width="w-32" height="h-5" className="mb-1" />
          <Skeleton width="w-24" height="h-3" />
        </div>
      </div>
      <div className="flex items-center space-x-2">
        <Skeleton width="w-8" height="h-8" className="rounded-lg" />
        <Skeleton width="w-8" height="h-8" className="rounded-lg" />
      </div>
    </div>
  );
}

// Skeleton para dashboard
export function DashboardSkeleton({ className = '' }) {
  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <HeaderSkeleton />
      
      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[1, 2, 3].map((i) => (
          <div key={i} className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <Skeleton width="w-16" height="h-4" className="mb-2" />
                <Skeleton width="w-12" height="h-8" />
              </div>
              <Skeleton width="w-12" height="h-12" className="rounded-xl" />
            </div>
          </div>
        ))}
      </div>

      {/* Orders grid */}
      <div className="grid-responsive">
        {Array.from({ length: 6 }).map((_, i) => (
          <OrderCardSkeleton key={i} />
        ))}
      </div>
    </div>
  );
}

// Skeleton para tabela
export function TableSkeleton({ 
  rows = 5, 
  columns = 4, 
  className = '' 
}) {
  return (
    <div className={`bg-white rounded-lg overflow-hidden ${className}`}>
      {/* Header */}
      <div className="px-6 py-3 border-b border-gray-200">
        <div className="grid grid-cols-4 gap-4">
          {Array.from({ length: columns }).map((_, i) => (
            <Skeleton key={i} width="w-20" height="h-4" />
          ))}
        </div>
      </div>

      {/* Rows */}
      <div className="divide-y divide-gray-200">
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="px-6 py-4">
            <div className="grid grid-cols-4 gap-4 items-center">
              {Array.from({ length: columns }).map((_, j) => (
                <Skeleton 
                  key={j} 
                  width={j === 0 ? "w-32" : j === columns - 1 ? "w-16" : "w-24"} 
                  height="h-4" 
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Skeleton para formulário
export function FormSkeleton({ fields = 4, className = '' }) {
  return (
    <div className={`space-y-4 ${className}`}>
      {Array.from({ length: fields }).map((_, i) => (
        <div key={i}>
          <Skeleton width="w-24" height="h-4" className="mb-2" />
          <Skeleton width="w-full" height="h-10" className="rounded-lg" />
        </div>
      ))}
      <div className="flex space-x-3 pt-4">
        <Skeleton width="w-24" height="h-10" className="rounded-lg" />
        <Skeleton width="w-20" height="h-10" className="rounded-lg" />
      </div>
    </div>
  );
}

// Skeleton com texto personalizado
export function TextSkeleton({ 
  lines = 3, 
  widths = ['w-full', 'w-4/5', 'w-3/5'],
  className = '' 
}) {
  return (
    <div className={`space-y-2 ${className}`}>
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton 
          key={i} 
          width={widths[i] || 'w-full'} 
          height="h-4" 
        />
      ))}
    </div>
  );
}

// Skeleton para gráficos
export function ChartSkeleton({ className = '' }) {
  return (
    <div className={`card p-6 ${className}`}>
      {/* Título */}
      <div className="flex items-center justify-between mb-6">
        <Skeleton width="w-32" height="h-6" />
        <Skeleton width="w-20" height="h-4" />
      </div>

      {/* Gráfico */}
      <div className="h-64 flex items-end justify-center space-x-2">
        {Array.from({ length: 7 }).map((_, i) => (
          <Skeleton 
            key={i} 
            width="w-8" 
            height={`h-${Math.floor(Math.random() * 48) + 16}`}
            className="rounded-t" 
          />
        ))}
      </div>

      {/* Legenda */}
      <div className="flex justify-center space-x-4 mt-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="flex items-center space-x-2">
            <Skeleton width="w-4" height="h-4" className="rounded-full" />
            <Skeleton width="w-16" height="h-3" />
          </div>
        ))}
      </div>
    </div>
  );
}

export default Skeleton;