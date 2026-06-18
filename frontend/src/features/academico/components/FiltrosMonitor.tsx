import { useState, type ChangeEvent } from 'react';
import type { MonitorFilters } from '../services/monitor.service';

interface FiltrosMonitorProps {
  filters: MonitorFilters;
  onFilterChange: <K extends keyof MonitorFilters>(key: K, value: MonitorFilters[K]) => void;
  onApply: () => void;
  onClear: () => void;
}

export function FiltrosMonitor({ filters, onFilterChange, onApply, onClear }: FiltrosMonitorProps) {
  const [completitudInput, setCompletitudInput] = useState(
    filters.completitud_min?.toString() ?? '',
  );

  const handleCompletitudChange = (e: ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value;
    setCompletitudInput(raw);
    const parsed = parseInt(raw, 10);
    if (!isNaN(parsed) && parsed >= 0 && parsed <= 100) {
      onFilterChange('completitud_min', parsed);
    } else if (raw === '') {
      onFilterChange('completitud_min', undefined);
    }
  };

  return (
    <div className="rounded-xl border border-outline-variant bg-surface-container-lowest p-md">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="space-y-1">
          <label className="text-label-xs font-medium text-outline uppercase tracking-wider">
            Alumno
          </label>
          <input
            type="text"
            value={filters.nombre ?? ''}
            onChange={(e) => onFilterChange('nombre', e.target.value || undefined)}
            placeholder="Buscar por nombre..."
            className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        <div className="space-y-1">
          <label className="text-label-xs font-medium text-outline uppercase tracking-wider">
            Comisión
          </label>
          <input
            type="text"
            value={filters.comision ?? ''}
            onChange={(e) => onFilterChange('comision', e.target.value || undefined)}
            placeholder="Ej: A, B, C..."
            className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        <div className="space-y-1">
          <label className="text-label-xs font-medium text-outline uppercase tracking-wider">
            Actividad
          </label>
          <input
            type="text"
            value={filters.actividad ?? ''}
            onChange={(e) => onFilterChange('actividad', e.target.value || undefined)}
            placeholder="Nombre de actividad..."
            className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        <div className="space-y-1">
          <label className="text-label-xs font-medium text-outline uppercase tracking-wider">
            Completitud mín. (%)
          </label>
          <input
            type="number"
            min={0}
            max={100}
            value={completitudInput}
            onChange={handleCompletitudChange}
            placeholder="0-100"
            className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
      </div>

      <div className="mt-4 flex items-center gap-3">
        <button
          type="button"
          onClick={onApply}
          className="rounded-lg bg-primary px-4 py-2 text-label-sm font-medium text-on-primary transition-colors hover:bg-primary/90"
        >
          Aplicar filtros
        </button>
        <button
          type="button"
          onClick={onClear}
          className="rounded-lg border border-outline-variant px-4 py-2 text-label-sm font-medium text-on-surface transition-colors hover:bg-surface-container-low"
        >
          Limpiar filtros
        </button>
      </div>
    </div>
  );
}
