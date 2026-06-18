import logoSrc from '@/assets/logo.svg';

interface LogoProps {
  size?: 'sm' | 'md' | 'lg';
  showText?: boolean;
  className?: string;
}

const sizeMap = {
  sm: { box: 'h-8 w-8', text: 'text-sm' },
  md: { box: 'h-10 w-10', text: 'text-sm' },
  lg: { box: 'h-12 w-12', text: 'text-headline-md' },
};

export function Logo({ size = 'md', showText = true, className = '' }: LogoProps) {
  const s = sizeMap[size];

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <img
        src={logoSrc}
        alt="Activia-Trace logo"
        className={`${s.box} rounded-xl`}
      />
      {showText && (
        <div>
          <h1 className={`${s.text} font-bold text-on-surface`}>Activia-Trace</h1>
          {size !== 'sm' && (
            <p className="text-label-sm text-outline">Academic Management</p>
          )}
        </div>
      )}
    </div>
  );
}
