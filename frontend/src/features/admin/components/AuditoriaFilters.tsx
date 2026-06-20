import { type ChangeEvent } from 'react';
import type { AuditoriaFilters as AuditoriaFiltersType } from '../types/auditoria';

const TIPOS_ACCION = [
  'USUARIO_CREAR',
  'USUARIO_ACTUALIZAR',
  'USUARIO_ELIMINAR',
  'MATERIA_CREAR',
  'MATERIA_ACTUALIZAR',
  'MATERIA_ELIMINAR',
  'CARRERA_CREAR',
  'CARRERA_ACTUALIZAR',
  'CARRERA_ELIMINAR',
  'COHORTE_CREAR',
  'COHORTE_ACTUALIZAR',
  'COHORTE_ELIMINAR',
  'DICTADO_CREAR',
  'DICTADO_ACTUALIZAR',
  'DICTADO_ELIMINAR',
  'ASIGNACION_CREAR',
  'ASIGNACION_ACTUALIZAR',
  'ASIGNACION_ELIMINAR',
  'AVISO_CREAR',
  'AVISO_ACTUALIZAR',
  'AVISO_ELIMINAR',
  'AVISO_CONFIRMAR',
  'TAREA_CREAR',
  'TAREA_ACTUALIZAR_ESTADO',
  'TAREA_ELIMINAR',
  'COLOQUIO_CREAR',
  'COLOQUIO_RESERVAR',
  'COLOQUIO_CANCELAR_RESERVA',
  'COLOQUIO_REGISTRAR_RESULTADO',
  'ENCUENTRO_CREAR',
  'ENCUENTRO_EDITAR',
  'ENCUENTRO_CANCELAR',
  'GUARDIA_REGISTRAR',
  'COMUNICACION_ENVIAR',
  'COMUNICACION_APROBAR',
  'LIQUIDACION_CERRAR',
];

interface AuditoriaFiltersProps {
  values: AuditoriaFiltersType;
  onChange: (key: string, value: unknown) => void;
  onClear: () => void;
}

export function AuditoriaFilters({ values, onChange, onClear }: AuditoriaFiltersProps) {
  const hasAnyValue =
    values.fecha_desde ||
    values.fecha_hasta ||
    values.materia_id ||
    values.usuario_id ||
    values.accion;

  return (
    <div className="rounded-xl border border-outline-variant bg-surface-container-lowest p-md">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <div className="space-y-1">
          <label className="text-label-xs font-medium text-outline uppercase tracking-wider">
            Fecha desde
          </label>
          <input
            type="date"
            value={values.fecha_desde ?? ''}
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
            value={values.fecha_hasta ?? ''}
            onChange={(e: ChangeEvent<HTMLInputElement>) =>
              onChange('fecha_hasta', e.target.value || undefined)
            }
            className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        <div className="space-y-1">
          <label className="text-label-xs font-medium text-outline uppercase tracking-wider">
            Usuario
          </label>
          <input
            type="text"
            value={values.usuario_id ?? ''}
            onChange={(e: ChangeEvent<HTMLInputElement>) =>
              onChange('usuario_id', e.target.value || undefined)
            }
            placeholder="ID o nombre..."
            className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        <div className="space-y-1">
          <label className="text-label-xs font-medium text-outline uppercase tracking-wider">
            Materia
          </label>
          <input
            type="text"
            value={values.materia_id ?? ''}
            onChange={(e: ChangeEvent<HTMLInputElement>) =>
              onChange('materia_id', e.target.value || undefined)
            }
            placeholder="ID de materia..."
            className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        <div className="space-y-1">
          <label className="text-label-xs font-medium text-outline uppercase tracking-wider">
            Tipo de acción
          </label>
          <select
            value={values.accion ?? ''}
            onChange={(e: ChangeEvent<HTMLSelectElement>) =>
              onChange('accion', e.target.value || undefined)
            }
            className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="">Todos</option>
            {TIPOS_ACCION.map((tipo) => (
              <option key={tipo} value={tipo}>
                {tipo.replace(/_/g, ' ')}
              </option>
            ))}
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
