import { cn } from '../../utils/cn';

type StatVariant = 'primary' | 'tertiary' | 'default';
type TrendDirection = 'up' | 'down' | 'neutral';

export interface StatCardProps {
  icon?: string;
  label: string;
  value: string | number;
  trend?: TrendDirection;
  trendValue?: string;
  variant?: StatVariant;
  className?: string;
}

export function StatCard({
  icon,
  label,
  value,
  trend,
  trendValue,
  variant = 'default',
  className,
}: StatCardProps) {
  const iconBg: Record<StatVariant, string> = {
    primary: 'bg-primary/20 text-primary',
    tertiary: 'bg-tertiary/20 text-tertiary',
    default: 'bg-outline-variant text-on-surface-variant',
  };

  const trendColors: Record<TrendDirection, string> = {
    up: 'text-tertiary',
    down: 'text-error',
    neutral: 'text-on-surface-variant',
  };

  const trendIcons: Record<TrendDirection, string> = {
    up: 'arrow_upward',
    down: 'arrow_downward',
    neutral: 'remove',
  };

  return (
    <div
      className={cn(
        'rounded-xl border border-outline-variant bg-surface-container-lowest p-4',
        className,
      )}
    >
      <div className="flex items-start justify-between">
        <div className="flex flex-col gap-1">
          <span className="text-label-sm uppercase tracking-wider text-outline font-label-md">
            {label}
          </span>
          <span className="text-headline-lg font-semibold text-on-surface">
            {value}
          </span>
        </div>
        {icon && (
          <div
            className={cn(
              'flex items-center justify-center w-10 h-10 rounded-full',
              iconBg[variant],
            )}
          >
            <span className="material-symbols-outlined">{icon}</span>
          </div>
        )}
      </div>
      {trend && (
        <div
          className={cn(
            'flex items-center gap-1 mt-2 text-label-sm',
            trendColors[trend],
          )}
        >
          <span className="material-symbols-outlined text-[1em]">
            {trendIcons[trend]}
          </span>
          {trendValue && <span>{trendValue}</span>}
        </div>
      )}
    </div>
  );
}
