import { memo } from 'react';
import { motion } from 'framer-motion';

const UserAvatar = memo(function UserAvatar({ 
  user, 
  size = 'md', 
  showTooltip = true,
  className = '' 
}) {
  const getUserInitials = (name) => {
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .substring(0, 2)
      .toUpperCase();
  };

  const sizeClasses = {
    xs: 'w-6 h-6 text-xs',
    sm: 'w-8 h-8 text-xs',
    md: 'w-10 h-10 text-sm',
    lg: 'w-12 h-12 text-base',
    xl: 'w-16 h-16 text-lg'
  };

  const avatarContent = user.photo_url ? (
    <img
      src={user.photo_url}
      alt={user.name}
      className="w-full h-full object-cover"
    />
  ) : (
    <span className="font-medium text-white">
      {getUserInitials(user.name)}
    </span>
  );

  const avatarElement = (
    <motion.div
      className={`
        ${sizeClasses[size]} 
        rounded-full bg-primary-500 border-2 border-white 
        flex items-center justify-center
        shadow-md hover:shadow-lg transition-shadow
        ${className}
      `}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      {avatarContent}
    </motion.div>
  );

  if (showTooltip && user.name) {
    return (
      <div className="relative group">
        {avatarElement}
        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 text-xs text-white bg-gray-800 rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-10">
          {user.name}
        </div>
      </div>
    );
  }

  return avatarElement;
});

export default UserAvatar;