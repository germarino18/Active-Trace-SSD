/**
 * MisTareasProfesorPage
 *
 * Dedicated page for PROFESORs to view and manage their own tasks.
 * Uses GET /api/v1/tareas/mias which returns a PLAIN ARRAY (not {items, total}).
 * DO NOT replace with coordinación's MisTareasPage — that reads data.items.length
 * and would crash here.
 */
import { useState } from 'react';
import { useMisTareasProfesor, useMutationCambiarEstadoTareaProfesor } from '../hooks/useProfesor';
import { LoadingState } from '@/features/academico/components/LoadingState';
import { EmptyState } from '@/features/academico/components/EmptyState';
import { Button } from '@/shared/components/ds';
import type { TareaProfesor } from '../types';

const ESTADO_OPTIONS: { value: string; label: string }[] = [
  { value: 'PENDIENTE', label: 'Pendiente' },
  { value: 'EN_PROGRESO', label: 'En progreso' },
  { value: 'RESUELTA', label: 'Resuelta' },
  { value: 'CANCELADA', label: 'Cancelada' },
];

const estadoColor: Record<string, string> = {
  PENDIENTE: 'var(--on-surface-variant)',
  EN_PROGRESO: 'var(--primary)',
  RESUELTA: 'var(--success, #22c55e)',
  CANCELADA: 'var(--error)',
};

const estadoLabel = (estado: string): string =>
  ESTADO_OPTIONS.find((o) => o.value === estado)?.label ?? estado;

function EstadoBadge({ estado }: { estado: string }) {
  return (
    <span
      style={{
        padding: '2px 10px',
        borderRadius: 999,
        fontSize: 12,
        fontWeight: 600,
        background: 'color-mix(in srgb, currentColor 12%, transparent)',
        color: estadoColor[estado] ?? 'var(--on-surface-variant)',
      }}
    >
      {estadoLabel(estado)}
    </span>
  );
}

function TareaRow({ tarea }: { tarea: TareaProfesor }) {
  const [showEstado, setShowEstado] = useState(false);
  const mutation = useMutationCambiarEstadoTareaProfesor();

  const handleEstado = async (nuevoEstado: string) => {
    if (nuevoEstado === tarea.estado) { setShowEstado(false); return; }
    await mutation.mutateAsync({ tareaId: tarea.id, estado: nuevoEstado });
    setShowEstado(false);
  };

  return (
    <tr className="border-b border-outline-variant transition-colors hover:bg-surface-container-low">
      <td className="px-4 py-3 text-body-sm text-on-surface font-medium">{tarea.descripcion}</td>
      <td className="px-4 py-3">
        <EstadoBadge estado={tarea.estado} />
      </td>
      <td className="px-4 py-3 text-body-sm text-on-surface-variant">
        {new Date(tarea.created_at).toLocaleDateString('es-AR')}
      </td>
      <td className="px-4 py-3" style={{ position: 'relative' }}>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setShowEstado((v) => !v)}
          disabled={mutation.isPending}
          aria-label="Cambiar estado"
        >
          <span className="material-symbols-outlined text-[14px]">edit</span>
          Estado
        </Button>
        {showEstado && (
          <div
            style={{
              position: 'absolute',
              right: 0,
              top: '100%',
              zIndex: 50,
              background: 'var(--surface-container)',
              border: '1px solid var(--outline-variant)',
              borderRadius: 8,
              overflow: 'hidden',
              minWidth: 160,
              boxShadow: '0 4px 16px rgba(0,0,0,0.12)',
            }}
          >
            {ESTADO_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                type="button"
                onClick={() => handleEstado(opt.value)}
                style={{
                  display: 'block',
                  width: '100%',
                  padding: '8px 16px',
                  textAlign: 'left',
                  fontSize: 14,
                  color: opt.value === tarea.estado ? 'var(--primary)' : 'var(--on-surface)',
                  background: 'transparent',
                  border: 'none',
                  cursor: 'pointer',
                }}
              >
                {opt.label}
              </button>
            ))}
          </div>
        )}
      </td>
    </tr>
  );
}

export function MisTareasProfesorPage() {
  const { data, isLoading, isError } = useMisTareasProfesor();

  return (
    <div className="space-y-6">
      <div>
        <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>
          Mis Tareas
        </h2>
        <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>
          Tareas asignadas a mí.
        </p>
      </div>

      {isLoading ? (
        <LoadingState rows={6} cols={5} />
      ) : isError ? (
        <EmptyState message="Error al cargar las tareas" icon="error" />
      ) : !data || data.length === 0 ? (
        <EmptyState message="No tenés tareas asignadas" icon="task" />
      ) : (
        <div className="overflow-x-auto rounded-xl border border-outline-variant">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-outline-variant bg-surface-container-low">
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Descripción</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Estado</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Creada</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {(data as TareaProfesor[]).map((tarea) => (
                <TareaRow key={tarea.id} tarea={tarea} />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
