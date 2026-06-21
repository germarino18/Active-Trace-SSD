/**
 * MisTareasProfesorPage
 *
 * Dedicated page for PROFESORs to view and manage their own tasks.
 * Uses GET /api/v1/tareas/mias which returns a PLAIN ARRAY (not {items, total}).
 * DO NOT replace with coordinación's MisTareasPage — that reads data.items.length
 * and would crash here.
 *
 * 7b: "Crear tarea" button opens CrearTareaModal (portal, not clipped).
 *     Per-row "Editar" button opens EditarTareaModal (portal, not clipped).
 *     Old position:absolute dropdown removed — it was clipped by overflow-x-auto.
 */
import { useState } from 'react';
import { useMisTareasProfesor } from '../hooks/useProfesor';
import { LoadingState } from '@/features/academico/components/LoadingState';
import { EmptyState } from '@/features/academico/components/EmptyState';
import { Button } from '@/shared/components/ds';
import { CrearTareaModal } from '../components/CrearTareaModal';
import { EditarTareaModal } from '../components/EditarTareaModal';
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

interface TareaRowProps {
  tarea: TareaProfesor;
  onEdit: (tarea: TareaProfesor) => void;
}

function TareaRow({ tarea, onEdit }: TareaRowProps) {
  return (
    <tr className="border-b border-outline-variant transition-colors hover:bg-surface-container-low">
      <td className="px-4 py-3 text-body-sm text-on-surface font-medium">{tarea.descripcion}</td>
      <td className="px-4 py-3">
        <EstadoBadge estado={tarea.estado} />
      </td>
      <td className="px-4 py-3 text-body-sm text-on-surface-variant">
        {new Date(tarea.created_at).toLocaleDateString('es-AR')}
      </td>
      <td className="px-4 py-3">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onEdit(tarea)}
          aria-label="Editar tarea"
        >
          <span className="material-symbols-outlined text-[14px]">edit</span>
          Editar
        </Button>
      </td>
    </tr>
  );
}

export function MisTareasProfesorPage() {
  const { data, isLoading, isError } = useMisTareasProfesor();
  const [showCrear, setShowCrear] = useState(false);
  const [tareaAEditar, setTareaAEditar] = useState<TareaProfesor | null>(null);

  return (
    <div className="space-y-6">
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 16 }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>
            Mis Tareas
          </h2>
          <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>
            Tareas asignadas a mí.
          </p>
        </div>
        <Button variant="primary" size="sm" onClick={() => setShowCrear(true)}>
          <span className="material-symbols-outlined text-[14px]">add</span>
          Crear tarea
        </Button>
      </div>

      {isLoading ? (
        <LoadingState rows={6} cols={4} />
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
                <TareaRow key={tarea.id} tarea={tarea} onEdit={setTareaAEditar} />
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Portal modals — rendered to document.body, not clipped by overflow */}
      <CrearTareaModal open={showCrear} onClose={() => setShowCrear(false)} />
      <EditarTareaModal
        open={tareaAEditar !== null}
        tarea={tareaAEditar}
        onClose={() => setTareaAEditar(null)}
      />
    </div>
  );
}
