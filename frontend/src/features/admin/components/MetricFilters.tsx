import { type ChangeEvent } from 'react';

interface MetricFiltersValues {
  fecha_desde: string;
  fecha_hasta: string;
  materia_id: string;
  usuario_id: string;
}

interface MetricFiltersProps {
  values: MetricFiltersValues;
  onChange: (key: string, value: unknown) => void;
  onClear: () => void;
}

export function MetricFilters({ values, onChange, onClear }: MetricFiltersProps) {
  const hasAnyValue = values.fecha_desde || values.fecha_hasta || values.materia_id || values.usuario_id;

  return (
    <div className="rounded-xl border border-outline-variant bg-surface-container-lowest p-md">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="space-y-1">
          <label className="text-label-xs font-medium text-outline uppercase tracking-wider">
            Fecha desde
          </label>
          <input
            type="date"
            value={values.fecha_desde}
            onChange={(e: ChangeEvent<HTMLInputElement>) =>
              onChange('fecha_desde', e.target.value || undefined)
            }
            className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        <div className="space-y-1">
          <label className="text-label-xs font-medium text-outline uppercase tracking-wider">
            Fecha hasta
          </label>
          <input
            type="date"
            value={values.fecha_hasta}
            onChange={(e: ChangeEvent<HTMLInputElement>) =>
              onChange('fecha_hasta', e.target.value || undefined)
            }
            className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        <div className="space-y-1">
          <label className="text-label-xs font-medium text-outline uppercase tracking-wider">
            Materia
          </label>
          <input
            type="text"
            value={values.materia_id}
            onChange={(e: ChangeEvent<HTMLInputElement>) =>
              onChange('materia_id', e.target.value || undefined)
            }
            placeholder="ID de materia..."
            className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        <div className="space-y-1">
          <label className="text-label-xs font-medium text-outline uppercase tracking-wider">
            Usuario
          </label>
          <input
            type="text"
            value={values.usuario_id}
            onChange={(e: ChangeEvent<HTMLInputElement>) =>
              onChange('usuario_id', e.target.value || undefined)
            }
            placeholder="ID o nombre..."
            className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
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
