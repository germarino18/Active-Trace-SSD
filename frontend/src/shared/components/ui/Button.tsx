import type { ButtonHTMLAttributes, ReactNode } from 'react';
import { Spinner } from '../Spinner';
import { cn } from '../../utils/cn';

type ButtonVariant = 'primary' | 'secondary' | 'ghost';
type ButtonSize = 'sm' | 'md' | 'lg';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  icon?: string;
  children?: ReactNode;
}

export function Button({
  variant = 'primary',
  size = 'md',
  disabled,
  loading,
  icon,
  children,
  className,
  ...rest
}: ButtonProps) {
  const base =
    'inline-flex items-center justify-center gap-2 rounded-xl font-label-md transition-all duration-150 active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none';

  const variants: Record<ButtonVariant, string> = {
    primary: 'bg-primary text-on-primary hover:bg-primary-container',
    secondary: 'border border-outline-variant text-on-surface hover:bg-surface-container-high',
    ghost: 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container',
  };

  const sizes: Record<ButtonSize, string> = {
    sm: 'px-3 py-1.5 text-label-sm',
    md: 'px-4 py-2 text-label-md',
    lg: 'px-6 py-3 text-body-md',
  };

  return (
    <button
      className={cn(base, variants[variant], sizes[size], className)}
      disabled={disabled ?? loading}
      {...rest}
    >
      {loading ? (
        <Spinner size="sm" />
      ) : icon ? (
        <span className="material-symbols-outlined text-[1.2em]">{icon}</span>
      ) : null}
      {children}
    </button>
  );
}
