import { type ChangeEvent } from 'react';

export interface UsuarioFilterValues {
  rol: string;
  activo: string;
  q: string;
}

interface UsuarioFiltersProps {
  values: UsuarioFilterValues;
  onChange: (key: string, value: unknown) => void;
  onClear: () => void;
}

const ROLES = [
  { value: 'ALUMNO', label: 'Alumno' },
  { value: 'TUTOR', label: 'Tutor' },
  { value: 'PROFESOR', label: 'Profesor' },
  { value: 'COORDINADOR', label: 'Coordinador' },
  { value: 'NEXO', label: 'Nexo' },
  { value: 'ADMIN', label: 'Admin' },
  { value: 'FINANZAS', label: 'Finanzas' },
];

export function UsuarioFilters({ values, onChange, onClear }: UsuarioFiltersProps) {
  const hasAnyValue = values.rol !== '' || values.activo !== '' || values.q !== '';

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
            placeholder="Buscar por nombre o email..."
            className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        <div className="space-y-1">
          <label className="text-label-xs font-medium text-outline uppercase tracking-wider">
            Rol
          </label>
          <select
            value={values.rol}
            onChange={(e: ChangeEvent<HTMLSelectElement>) =>
              onChange('rol', e.target.value || undefined)
            }
            className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="">Todos</option>
            {ROLES.map((r) => (
              <option key={r.value} value={r.value}>
                {r.label}
              </option>
            ))}
          </select>
        </div>

        <div className="space-y-1">
          <label className="text-label-xs font-medium text-outline uppercase tracking-wider">
            Estado
          </label>
          <select
            value={values.activo}
            onChange={(e: ChangeEvent<HTMLSelectElement>) =>
              onChange('activo', e.target.value || undefined)
            }
            className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="">Todos</option>
            <option value="true">Activo</option>
            <option value="false">Inactivo</option>
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
