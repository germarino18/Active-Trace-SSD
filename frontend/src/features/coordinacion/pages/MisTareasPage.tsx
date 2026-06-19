import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useMisTareas } from '../hooks/useTareas';
import { TareaStateBadge } from '../components/TareaStateBadge';
import { LoadingState } from '@/features/academico/components/LoadingState';
import { EmptyState } from '@/features/academico/components/EmptyState';
import type { Tarea } from '../types';
import { Button } from '@/shared/components/ds';

export function MisTareasPage() {
  const [filters, setFilters] = useState({ materia_id: '', cohorte_id: '' });
  const [page, setPage] = useState(0);
  const pageSize = 25;

  const activeFilters = Object.fromEntries(
    Object.entries(filters).filter(([, v]) => v !== ''),
  );

  const { data, isLoading, isError } = useMisTareas({
    ...activeFilters,
    offset: page * pageSize,
    limit: pageSize,
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Mis Tareas</h2>
          <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>
            Tareas asignadas a mí.
          </p>
        </div>
      </div>

      <div className="flex flex-wrap gap-3 rounded-xl border border-outline-variant bg-surface-container-lowest p-4">
        <input
          placeholder="Materia"
          value={filters.materia_id}
          onChange={(e) => { setFilters((f) => ({ ...f, materia_id: e.target.value })); setPage(0); }}
          className="rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-label-sm text-on-surface outline-none placeholder:text-outline focus:border-primary"
        />
        <input
          placeholder="Cohorte"
          value={filters.cohorte_id}
          onChange={(e) => { setFilters((f) => ({ ...f, cohorte_id: e.target.value })); setPage(0); }}
          className="rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-label-sm text-on-surface outline-none placeholder:text-outline focus:border-primary"
        />
      </div>

      {isLoading ? (
        <LoadingState rows={6} cols={5} />
      ) : isError ? (
        <EmptyState message="Error al cargar las tareas" icon="error" />
      ) : !data || data.items.length === 0 ? (
        <EmptyState message="No tenés tareas asignadas" icon="task" />
      ) : (
        <>
          <div className="overflow-x-auto rounded-xl border border-outline-variant">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-outline-variant bg-surface-container-low">
                  <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Título</th>
                  <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Estado</th>
                  <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Asignada por</th>
                  <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Materia</th>
                  <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Creada</th>
                  <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((tarea: Tarea) => (
                  <tr
                    key={tarea.id}
                    className="border-b border-outline-variant transition-colors hover:bg-surface-container-low"
                  >
                    <td className="px-4 py-3">
                      <Link
                        to={`/tareas/${tarea.id}`}
                        className="text-body-sm font-medium text-primary hover:underline"
                      >
                        {tarea.titulo}
                      </Link>
                    </td>
                    <td className="px-4 py-3">
                      <TareaStateBadge estado={tarea.estado} />
                    </td>
                    <td className="px-4 py-3 text-body-sm text-on-surface-variant">
                      {tarea.asignado_por_nombre}
                    </td>
                    <td className="px-4 py-3 text-body-sm text-on-surface-variant">
                      {tarea.materia_nombre ?? '-'}
                    </td>
                    <td className="px-4 py-3 text-body-sm text-on-surface-variant">
                      {new Date(tarea.created_at).toLocaleDateString('es-AR')}
                    </td>
                    <td className="px-4 py-3">
                      <Link
                        to={`/tareas/${tarea.id}`}
                        className="inline-flex items-center gap-1 rounded-lg bg-primary/10 px-2.5 py-1 text-label-xs font-medium text-primary transition-colors hover:bg-primary/20"
                      >
                        Ver detalle
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {data.total > pageSize && (
            <div className="flex items-center justify-center gap-2">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                disabled={page === 0}
              >
                Anterior
              </Button>
              <span className="text-label-sm text-on-surface-variant">
                Página {page + 1} de {Math.ceil(data.total / pageSize)}
              </span>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setPage((p) => p + 1)}
                disabled={(page + 1) * pageSize >= data.total}
              >
                Siguiente
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
