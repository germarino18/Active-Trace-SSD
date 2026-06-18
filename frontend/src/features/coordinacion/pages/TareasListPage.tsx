import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useTareas } from '../hooks/useTareas';
import { TareaStateBadge } from '../components/TareaStateBadge';
import { DataTable } from '../components/DataTable';
import { FilterBar } from '../components/FilterBar';
import { EmptyState } from '@/features/academico/components/EmptyState';
import { useAuth } from '@/features/auth/hooks/useAuth';
import type { Tarea } from '../types';
import type { ColumnDef } from '../components/DataTable';
import type { FilterDefinition } from '../components/FilterBar';

const filters: FilterDefinition[] = [
  { key: 'q', label: 'Buscar', type: 'text', placeholder: 'Título o descripción' },
  { key: 'asignado_id', label: 'Asignado a', type: 'text', placeholder: 'ID del usuario' },
  { key: 'asignado_por_id', label: 'Asignado por', type: 'text', placeholder: 'ID del usuario' },
  { key: 'materia_id', label: 'Materia', type: 'text', placeholder: 'ID de la materia' },
  {
    key: 'estado',
    label: 'Estado',
    type: 'select',
    options: [
      { value: 'Pendiente', label: 'Pendiente' },
      { value: 'En progreso', label: 'En progreso' },
      { value: 'Resuelta', label: 'Resuelta' },
      { value: 'Cancelada', label: 'Cancelada' },
    ],
  },
];

const columns: ColumnDef<Tarea>[] = [
  { key: 'titulo', label: 'Título', render: (row) => (
    <Link to={`/tareas/${row.id}`} className="font-medium text-primary hover:underline">
      {row.titulo}
    </Link>
  )},
  { key: 'estado', label: 'Estado', render: (row) => <TareaStateBadge estado={row.estado} /> },
  { key: 'asignado_nombre', label: 'Asignado a' },
  { key: 'asignado_por_nombre', label: 'Asignado por' },
  { key: 'materia_nombre', label: 'Materia', render: (row) => row.materia_nombre ?? '-' },
  { key: 'created_at', label: 'Creada', render: (row) => new Date(row.created_at).toLocaleDateString('es-AR') },
];

export function TareasListPage() {
  const { hasPermission } = useAuth();
  const [filterValues, setFilterValues] = useState<Record<string, string | string[] | { desde?: string; hasta?: string }>>({});
  const [page, setPage] = useState(0);
  const pageSize = 25;

  const apiFilters: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(filterValues)) {
    if (value && typeof value === 'string') {
      apiFilters[key] = value;
    }
  }

  const { data, isLoading, isError } = useTareas({
    ...apiFilters,
    offset: page * pageSize,
    limit: pageSize,
  });

  const canCreate = hasPermission('coordinacion:tareas:crear');

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-headline-lg text-headline-lg text-on-surface">Tareas</h2>
          <p className="text-body-md text-on-surface-variant mt-1">
            Administración global de tareas.
          </p>
        </div>
        {canCreate && (
          <Link
            to="/tareas/crear"
            className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-label-sm font-medium text-on-primary transition-colors hover:bg-primary/90"
          >
            <span className="material-symbols-outlined text-[18px]">add</span>
            Nueva Tarea
          </Link>
        )}
      </div>

      <FilterBar
        filters={filters}
        values={filterValues}
        onChange={(key, value) => { setFilterValues((v) => ({ ...v, [key]: value })); setPage(0); }}
        onClear={() => { setFilterValues({}); setPage(0); }}
      />

      {isError ? (
        <EmptyState message="Error al cargar las tareas" icon="error" />
      ) : (
        <>
          <DataTable
            columns={columns}
            data={(data?.items ?? []) as unknown as Tarea[] & Record<string, unknown>[]}
            rowKey="id"
            isLoading={isLoading}
            emptyMessage="No se encontraron tareas con los filtros aplicados."
          />

          {data && data.total > pageSize && (
            <div className="flex items-center justify-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                disabled={page === 0}
                className="rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-sm text-on-surface transition-colors hover:bg-surface-container disabled:opacity-50"
              >
                Anterior
              </button>
              <span className="text-label-sm text-on-surface-variant">
                Página {page + 1} de {Math.ceil(data.total / pageSize)}
              </span>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={(page + 1) * pageSize >= data.total}
                className="rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-sm text-on-surface transition-colors hover:bg-surface-container disabled:opacity-50"
              >
                Siguiente
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
