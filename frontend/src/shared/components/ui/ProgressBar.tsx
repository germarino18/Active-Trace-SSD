import { cn } from '../../utils/cn';

type ProgressVariant = 'primary' | 'tertiary' | 'outline';

export interface ProgressBarProps {
  value: number;
  variant?: ProgressVariant;
  className?: string;
  showLabel?: boolean;
}

export function ProgressBar({
  value = 0,
  variant = 'primary',
  className,
  showLabel = false,
}: ProgressBarProps) {
  const clamped = Math.min(100, Math.max(0, value));

  const colors: Record<ProgressVariant, string> = {
    primary: 'bg-primary',
    tertiary: 'bg-tertiary',
    outline: 'bg-outline',
  };

  return (
    <div className={cn('flex items-center gap-3', className)}>
      <div className="flex-1 h-2 rounded-full bg-surface-container-high overflow-hidden">
        <div
          className={cn('h-full rounded-full transition-all duration-1000', colors[variant])}
          style={{ width: `${clamped}%` }}
          role="progressbar"
          aria-valuenow={clamped}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>
      {showLabel && (
        <span className="text-label-sm text-on-surface-variant font-label-md whitespace-nowrap">
          {clamped}%
        </span>
      )}
    </div>
  );
}
