import { useEffect, useState } from 'react';
import { CheckCircleIcon, ClockIcon } from '@heroicons/react/24/outline';

export default function SeparationProgress({ 
  progress = 0, 
  totalItems = 0, 
  separatedItems = 0,
  animated = true 
}) {
  const [displayProgress, setDisplayProgress] = useState(0);

  // Animação suave do progresso
  useEffect(() => {
    if (!animated) {
      setDisplayProgress(progress);
      return;
    }

    const duration = 500; // 500ms
    const steps = 30;
    const stepValue = (progress - displayProgress) / steps;
    
    if (Math.abs(stepValue) < 0.1) {
      setDisplayProgress(progress);
      return;
    }

    const interval = setInterval(() => {
      setDisplayProgress(prev => {
        const next = prev + stepValue;
        if (Math.abs(next - progress) < Math.abs(stepValue)) {
          clearInterval(interval);
          return progress;
        }
        return next;
      });
    }, duration / steps);

    return () => clearInterval(interval);
  }, [progress, animated]);

  const getProgressColor = () => {
    if (displayProgress >= 100) return 'bg-green-500';
    if (displayProgress >= 75) return 'bg-orange-400';
    if (displayProgress >= 50) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getProgressTextColor = () => {
    if (displayProgress >= 100) return 'text-green-600';
    if (displayProgress >= 75) return 'text-orange-500';
    if (displayProgress >= 50) return 'text-orange-600';
    return 'text-red-600';
  };

  const isCompleted = displayProgress >= 100;
  const pendingItems = totalItems - separatedItems;

  return (
    <div className="space-y-4">
      {/* Cabeçalho com estatísticas */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-6">
          {/* Progresso principal */}
          <div className="flex items-center space-x-2">
            {isCompleted ? (
              <CheckCircleIcon className="h-6 w-6 text-green-500" />
            ) : (
              <ClockIcon className="h-6 w-6 text-orange-500" />
            )}
            <span className={`text-2xl font-bold ${getProgressTextColor()}`}>
              {Math.round(displayProgress)}%
            </span>
            <span className="text-sm text-gray-500">concluído</span>
          </div>
        </div>

        {/* Estatísticas de itens */}
        <div className="flex items-center space-x-6 text-sm">
          <div className="text-center">
            <div className="font-semibold text-gray-900">{separatedItems}</div>
            <div className="text-gray-500">Separados</div>
          </div>
          <div className="text-center">
            <div className="font-semibold text-gray-900">{pendingItems}</div>
            <div className="text-gray-500">Pendentes</div>
          </div>
          <div className="text-center">
            <div className="font-semibold text-gray-900">{totalItems}</div>
            <div className="text-gray-500">Total</div>
          </div>
        </div>
      </div>

      {/* Barra de progresso */}
      <div className="relative">
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div
            className={`h-full transition-all duration-500 ease-out ${getProgressColor()}`}
            style={{ width: `${Math.min(displayProgress, 100)}%` }}
          />
        </div>
        
        {/* Indicadores de marco */}
        <div className="absolute top-0 left-0 w-full h-3 flex items-center justify-between px-1">
          {[25, 50, 75].map(milestone => (
            <div
              key={milestone}
              className={`w-0.5 h-2 transition-colors duration-300 ${
                displayProgress >= milestone ? 'bg-white opacity-60' : 'bg-gray-400 opacity-40'
              }`}
              style={{ marginLeft: `${milestone - 0.25}%` }}
            />
          ))}
        </div>
      </div>

      {/* Mensagens motivacionais */}
      <div className="text-center">
        {isCompleted ? (
          <div className="flex items-center justify-center space-x-2 text-green-600">
            <CheckCircleIcon className="h-5 w-5" />
            <span className="font-medium">Pedido concluído! 🎉</span>
          </div>
        ) : displayProgress >= 75 ? (
          <p className="text-orange-600 font-medium">Quase lá! Faltam poucos itens 💪</p>
        ) : displayProgress >= 50 ? (
          <p className="text-orange-600 font-medium">Ótimo progresso! Continue assim 👍</p>
        ) : displayProgress > 0 ? (
          <p className="text-gray-600 font-medium">Separação em andamento... 🚀</p>
        ) : (
          <p className="text-gray-500">Clique nos itens para marcar como separados</p>
        )}
      </div>

      {/* Barra adicional para itens em compras (se houver) */}
      {/* Esta funcionalidade pode ser adicionada futuramente se necessário */}
    </div>
  );
}