import React from 'react';

interface FormFieldProps {
  label: string;
  children: React.ReactNode;
  className?: string;
}

export const FormField: React.FC<FormFieldProps> = ({ label, children, className = '' }) => {
  return (
    <div className={`flex items-start gap-4 ${className}`}>
      <label className="text-sm font-medium text-gray-700 w-48 pt-2 text-left">
        {label}
      </label>
      <div className="flex-1">
        {children}
      </div>
    </div>
  );
};