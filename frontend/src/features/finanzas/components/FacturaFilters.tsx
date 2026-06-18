import { type ChangeEvent } from 'react';
import type { EstadoFactura } from '../types/facturas';

export interface FacturaFilterValues {
  docente: string;
  estado: EstadoFactura | '';
  fecha_desde: string;
  fecha_hasta: string;
  q: string;
}

interface FacturaFiltersProps {
  values: FacturaFilterValues;
  onChange: (key: string, value: unknown) => void;
  onClear: () => void;
}

export function FacturaFilters({ values, onChange, onClear }: FacturaFiltersProps) {
  const hasAnyValue = Object.values(values).some((v) => v !== '' && v !== undefined);

  return (
    <div className="rounded-xl border border-outline-variant bg-surface-container-lowest p-md">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="space-y-1">
          <label className="text-label-xs font-medium text-outline uppercase tracking-wider">
            Búsqueda
          </label>
          <input
            type="text"
            value={values.q}
            onChange={(e: ChangeEvent<HTMLInputElement>) =>
              onChange('q', e.target.value || undefined)
            }
            placeholder="Buscar por detalle, periodo..."
            className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        <div className="space-y-1">
          <label className="text-label-xs font-medium text-outline uppercase tracking-wider">
            Docente
          </label>
          <input
            type="text"
            value={values.docente}
            onChange={(e: ChangeEvent<HTMLInputElement>) =>
              onChange('docente', e.target.value || undefined)
            }
            placeholder="Nombre del docente..."
            className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        <div className="space-y-1">
          <label className="text-label-xs font-medium text-outline uppercase tracking-wider">
            Estado
          </label>
          <select
            value={values.estado}
            onChange={(e: ChangeEvent<HTMLSelectElement>) =>
              onChange('estado', e.target.value || undefined)
            }
            className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="">Todos</option>
            <option value="pendiente">Pendiente</option>
            <option value="abonada">Abonada</option>
          </select>
        </div>

        <div className="space-y-1">
          <label className="text-label-xs font-medium text-outline uppercase tracking-wider">
            Rango de fechas
          </label>
          <div className="flex items-center gap-2">
            <input
              type="date"
              value={values.fecha_desde}
              onChange={(e) =>
                onChange('fecha_desde', e.target.value || undefined)
              }
              className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
            />
            <span className="text-on-surface-variant">a</span>
            <input
              type="date"
              value={values.fecha_hasta}
              onChange={(e) =>
                onChange('fecha_hasta', e.target.value || undefined)
              }
              className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
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
