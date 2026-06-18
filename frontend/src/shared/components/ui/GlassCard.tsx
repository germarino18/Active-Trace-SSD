import type { ReactNode, HTMLAttributes } from 'react';
import { cn } from '../../utils/cn';

type GlassPadding = 'sm' | 'md' | 'lg';

export interface GlassCardProps extends HTMLAttributes<HTMLDivElement> {
  padding?: GlassPadding;
  children: ReactNode;
  hover?: boolean;
}

export function GlassCard({
  padding = 'md',
  children,
  className,
  hover = false,
  ...rest
}: GlassCardProps) {
  const paddings: Record<GlassPadding, string> = {
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6',
  };

  return (
    <div
      className={cn(
        'glass-card rounded-xl',
        hover ? 'hover:-translate-y-0.5 transition-transform duration-200' : '',
        paddings[padding],
        rest.onClick ? 'cursor-pointer' : '',
        className,
      )}
      {...rest}
    >
      {children}
    </div>
  );
}
