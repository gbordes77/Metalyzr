import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  subtitle?: string;
  onClick?: () => void;
}

export const Card: React.FC<CardProps> = ({ 
  children, 
  className = '', 
  title, 
  subtitle,
  onClick
}) => {
  return (
    <div 
      className={`bg-white rounded-lg shadow-md border border-gray-200 ${className} ${
        onClick ? 'cursor-pointer hover:shadow-lg transition-shadow' : ''
      }`}
      onClick={onClick}
    >
      {(title || subtitle) && (
        <div className="px-6 py-4 border-b border-gray-200">
          {title && (
            <h3 className="text-lg font-semibold text-gray-900">
              {title}
            </h3>
          )}
          {subtitle && (
            <p className="text-sm text-gray-600 mt-1">
              {subtitle}
            </p>
          )}
        </div>
      )}
      <div className="p-6">
        {children}
      </div>
    </div>
  );
}; 