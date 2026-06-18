import type { ReactNode, HTMLAttributes } from 'react';
import { cn } from '../../utils/cn';

type CardPadding = 'sm' | 'md' | 'lg';

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  hover?: boolean;
  padding?: CardPadding;
  children: ReactNode;
}

export function Card({
  hover = false,
  padding = 'md',
  children,
  className,
  ...rest
}: CardProps) {
  const paddings: Record<CardPadding, string> = {
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6',
  };

  return (
    <div
      className={cn(
        'bg-surface-container-lowest rounded-xl border border-outline-variant',
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
