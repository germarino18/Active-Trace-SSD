interface HelpButtonProps {
  tooltip: string;
}

export function HelpButton({ tooltip }: HelpButtonProps) {
  return (
    <div className="group relative inline-flex">
      <button
        type="button"
        className="flex h-6 w-6 items-center justify-center rounded-full text-outline transition-colors hover:bg-surface-container-low hover:text-on-surface-variant"
        aria-label={tooltip}
      >
        <span className="material-symbols-outlined text-[18px]">help</span>
      </button>
      <div className="absolute bottom-full left-1/2 z-50 mb-2 hidden -translate-x-1/2 whitespace-nowrap rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-1.5 text-label-xs text-on-surface shadow-lg group-hover:block">
        {tooltip}
        <div className="absolute left-1/2 top-full -translate-x-1/2 border-4 border-transparent border-t-outline-variant" />
      </div>
    </div>
  );
}
