import { useState, memo } from 'react';

const StatusFilter = memo(function StatusFilter({ 
  onFilterChange, 
  currentFilter = 'all',
  orderCounts = {},
  className = ''
}) {
  const [activeFilter, setActiveFilter] = useState(currentFilter);

  const filters = [
    { 
      key: 'all', 
      label: 'Todos', 
      color: 'bg-gray-100 text-gray-800 border-gray-300',
      activeColor: 'bg-gray-800 text-white border-gray-800'
    },
    { 
      key: 'pending', 
      label: 'Pendentes', 
      color: 'bg-gray-100 text-gray-800 border-gray-300',
      activeColor: 'bg-gray-800 text-white border-gray-800'
    },
    { 
      key: 'in_progress', 
      label: 'Em Separação', 
      color: 'bg-orange-100 text-orange-800 border-orange-300',
      activeColor: 'bg-orange-600 text-white border-orange-600'
    },
    { 
      key: 'completed', 
      label: 'Concluídos', 
      color: 'bg-green-100 text-green-800 border-green-300',
      activeColor: 'bg-green-600 text-white border-green-600'
    },
    { 
      key: 'paused', 
      label: 'Pausados', 
      color: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      activeColor: 'bg-yellow-600 text-white border-yellow-600'
    }
  ];

  const handleFilterClick = (filterKey) => {
    setActiveFilter(filterKey);
    if (onFilterChange) {
      onFilterChange(filterKey);
    }
  };

  const getCount = (filterKey) => {
    if (filterKey === 'all') {
      return Object.values(orderCounts).reduce((sum, count) => sum + count, 0);
    }
    return orderCounts[filterKey] || 0;
  };

  return (
    <div className={`flex flex-wrap gap-2 ${className}`}>
      {filters.map((filter) => {
        const isActive = activeFilter === filter.key;
        const count = getCount(filter.key);
        
        return (
          <button
            key={filter.key}
            onClick={() => handleFilterClick(filter.key)}
            className={`
              inline-flex items-center px-4 py-2 rounded-full text-sm font-medium border
              transition-all duration-200 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2
              ${isActive ? filter.activeColor : filter.color}
            `}
          >
            <span>{filter.label}</span>
            {count > 0 && (
              <span className={`
                ml-2 inline-flex items-center justify-center px-2 py-1 text-xs font-bold rounded-full
                ${isActive 
                  ? 'bg-white bg-opacity-25 text-current' 
                  : 'bg-gray-800 bg-opacity-10 text-current'
                }
              `}>
                {count}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
});

export default StatusFilter;