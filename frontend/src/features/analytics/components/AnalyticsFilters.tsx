import { type ChangeEvent } from 'react';

export interface AnalyticsFiltersValues {
  fecha_desde: string;
  fecha_hasta: string;
  carrera_id: string;
  cohorte_id: string;
  materia_id: string;
  riesgo: string;
}

interface AnalyticsFiltersProps {
  values: AnalyticsFiltersValues;
  onChange: (key: string, value: unknown) => void;
  onClear: () => void;
}

export function AnalyticsFilters({ values, onChange, onClear }: AnalyticsFiltersProps) {
  const hasAnyValue = values.fecha_desde || values.fecha_hasta || values.carrera_id || values.cohorte_id || values.materia_id || values.riesgo;

  return (
    <div className="rounded-xl border border-outline-variant bg-surface-container-lowest p-md">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
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
            Carrera
          </label>
          <input
            type="text"
            value={values.carrera_id}
            onChange={(e: ChangeEvent<HTMLInputElement>) =>
              onChange('carrera_id', e.target.value || undefined)
            }
            placeholder="ID de carrera..."
            className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        <div className="space-y-1">
          <label className="text-label-xs font-medium text-outline uppercase tracking-wider">
            Cohorte
          </label>
          <input
            type="text"
            value={values.cohorte_id}
            onChange={(e: ChangeEvent<HTMLInputElement>) =>
              onChange('cohorte_id', e.target.value || undefined)
            }
            placeholder="ID de cohorte..."
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
            Riesgo
          </label>
          <select
            value={values.riesgo}
            onChange={(e: ChangeEvent<HTMLSelectElement>) =>
              onChange('riesgo', e.target.value || undefined)
            }
            className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="">Todos</option>
            <option value="bajo">Bajo</option>
            <option value="medio">Medio</option>
            <option value="alto">Alto</option>
          </select>
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
