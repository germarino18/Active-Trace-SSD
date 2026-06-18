import type { ReactNode } from 'react';
import { cn } from '../../utils/cn';

type BadgeVariant = 'default' | 'primary' | 'success' | 'warning' | 'error';

export interface BadgeProps {
  variant?: BadgeVariant;
  children: ReactNode;
  className?: string;
}

export function Badge({
  variant = 'default',
  children,
  className,
}: BadgeProps) {
  const variants: Record<BadgeVariant, string> = {
    default: 'bg-outline-variant text-outline',
    primary: 'bg-primary/20 text-primary border border-primary/30',
    success: 'bg-tertiary/20 text-tertiary',
    warning: 'bg-warning/20 text-warning',
    error: 'bg-error/20 text-error',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-sm py-0.5 text-label-sm font-semibold',
        variants[variant],
        className,
      )}
    >
      {children}
    </span>
  );
}
