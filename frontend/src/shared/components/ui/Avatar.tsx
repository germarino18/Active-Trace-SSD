import { cn } from '../../utils/cn';

type AvatarSize = 'sm' | 'md' | 'lg';

export interface AvatarProps {
  src?: string;
  name: string;
  size?: AvatarSize;
  className?: string;
}

function getInitials(name: string): string {
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0])
    .join('')
    .toUpperCase();
}

export function Avatar({
  src,
  name,
  size = 'md',
  className,
}: AvatarProps) {
  const sizes: Record<AvatarSize, string> = {
    sm: 'w-8 h-8 text-label-sm',
    md: 'w-10 h-10 text-body-md',
    lg: 'w-12 h-12 text-headline-md',
  };

  if (src) {
    return (
      <img
        src={src}
        alt={name}
        className={cn(
          'rounded-full object-cover border border-outline-variant',
          sizes[size],
          className,
        )}
      />
    );
  }

  return (
    <div
      className={cn(
        'flex items-center justify-center rounded-full bg-primary/20 text-primary font-bold',
        sizes[size],
        className,
      )}
      aria-label={name}
    >
      {getInitials(name)}
    </div>
  );
}
