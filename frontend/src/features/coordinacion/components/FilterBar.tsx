import { type ChangeEvent } from 'react';

export interface FilterDefinition {
  key: string;
  label: string;
  type: 'text' | 'select' | 'date-range' | 'multi-select';
  options?: { value: string; label: string }[];
  placeholder?: string;
}

interface FilterBarProps {
  filters: FilterDefinition[];
  values: Record<string, string | string[] | { desde?: string; hasta?: string }>;
  onChange: (key: string, value: unknown) => void;
  onClear: () => void;
}

export function FilterBar({ filters, values, onChange, onClear }: FilterBarProps) {
  const hasAnyValue = Object.values(values).some((v) => {
    if (Array.isArray(v)) return v.length > 0;
    if (v && typeof v === 'object' && 'desde' in v) {
      return !!(v as { desde?: string; hasta?: string }).desde || !!(v as { desde?: string; hasta?: string }).hasta;
    }
    return !!v;
  });

  return (
    <div className="rounded-xl border border-outline-variant bg-surface-container-lowest p-md">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {filters.map((filter) => {
          if (filter.type === 'text') {
            return (
              <div key={filter.key} className="space-y-1">
                <label className="text-label-xs font-medium text-outline uppercase tracking-wider">
                  {filter.label}
                </label>
                <input
                  type="text"
                  value={(values[filter.key] as string) ?? ''}
                  onChange={(e: ChangeEvent<HTMLInputElement>) =>
                    onChange(filter.key, e.target.value || undefined)
                  }
                  placeholder={filter.placeholder}
                  className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
            );
          }

          if (filter.type === 'select') {
            return (
              <div key={filter.key} className="space-y-1">
                <label className="text-label-xs font-medium text-outline uppercase tracking-wider">
                  {filter.label}
                </label>
                <select
                  value={(values[filter.key] as string) ?? ''}
                  onChange={(e: ChangeEvent<HTMLSelectElement>) =>
                    onChange(filter.key, e.target.value || undefined)
                  }
                  className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value="">Tod{filter.label.endsWith('a') ? 'a' : 'o'}s</option>
                  {filter.options?.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>
            );
          }

          if (filter.type === 'date-range') {
            const rangeValue = (values[filter.key] as { desde?: string; hasta?: string }) ?? {};
            return (
              <div key={filter.key} className="space-y-1">
                <label className="text-label-xs font-medium text-outline uppercase tracking-wider">
                  {filter.label}
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="date"
                    value={rangeValue.desde ?? ''}
                    onChange={(e) =>
                      onChange(filter.key, { ...rangeValue, desde: e.target.value || undefined })
                    }
                    className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                  <span className="text-on-surface-variant">a</span>
                  <input
                    type="date"
                    value={rangeValue.hasta ?? ''}
                    onChange={(e) =>
                      onChange(filter.key, { ...rangeValue, hasta: e.target.value || undefined })
                    }
                    className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>
            );
          }

          if (filter.type === 'multi-select') {
            const selected = (values[filter.key] as string[]) ?? [];
            return (
              <div key={filter.key} className="space-y-1">
                <label className="text-label-xs font-medium text-outline uppercase tracking-wider">
                  {filter.label}
                </label>
                <div className="flex flex-wrap gap-1 rounded-lg border border-outline-variant bg-surface-container-lowest p-2">
                  {filter.options?.map((opt) => {
                    const isSelected = selected.includes(opt.value);
                    return (
                      <button
                        key={opt.value}
                        type="button"
                        onClick={() => {
                          const next = isSelected
                            ? selected.filter((v) => v !== opt.value)
                            : [...selected, opt.value];
                          onChange(filter.key, next.length > 0 ? next : undefined);
                        }}
                        className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-label-xs font-medium transition-colors ${
                          isSelected
                            ? 'bg-primary/15 text-primary'
                            : 'bg-surface-container-low text-on-surface-variant hover:bg-surface-container'
                        }`}
                      >
                        {opt.label}
                        {isSelected && (
                          <span className="material-symbols-outlined text-[14px]">close</span>
                        )}
                      </button>
                    );
                  })}
                </div>
              </div>
            );
          }

          return null;
        })}
      </div>

      {hasAnyValue && (
        <div className="mt-4 flex items-center justify-end">
          <button
            type="button"
            onClick={onClear}
            className="flex items-center gap-1 rounded-lg border border-outline-variant px-3 py-1.5 text-label-sm text-on-surface-variant transition-colors hover:bg-surface-container-low"
          >
            <span className="material-symbols-outlined text-[16px]">close</span>
            Limpiar filtros
          </button>
        </div>
      )}
    </div>
  );
}
