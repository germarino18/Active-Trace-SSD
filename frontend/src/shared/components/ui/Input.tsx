import type { InputHTMLAttributes } from 'react';
import { cn } from '../../utils/cn';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  icon?: string;
}

export function Input({
  label,
  error,
  helperText,
  icon,
  className,
  id,
  ...rest
}: InputProps) {
  const inputId = id ?? label?.toLowerCase().replace(/\s+/g, '-');

  return (
    <div className="w-full">
      {label && (
        <label
          htmlFor={inputId}
          className="block text-label-md font-label-md text-on-surface mb-1.5"
        >
          {label}
        </label>
      )}
      <div className="relative">
        {icon && (
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none">
            {icon}
          </span>
        )}
        <input
          id={inputId}
          className={cn(
            'w-full bg-surface-container-low border rounded-xl px-4 py-2.5 text-body-md text-on-surface placeholder:text-outline outline-none',
            'focus:ring-2 focus:ring-primary focus:border-primary',
            'transition-all duration-150',
            error ? 'border-error ring-1 ring-error' : 'border-outline-variant',
            icon ? 'pl-10' : '',
            className,
          )}
          {...rest}
        />
      </div>
      {error && <p className="mt-1.5 text-error text-label-sm">{error}</p>}
      {helperText && !error && (
        <p className="mt-1.5 text-on-surface-variant text-label-sm">{helperText}</p>
      )}
    </div>
  );
}
