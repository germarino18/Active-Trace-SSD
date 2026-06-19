import { useState } from 'react';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { useMonitorCoordinacion } from '../hooks/useMonitores';
import { DataTable, type ColumnDef } from '../components/DataTable';
import { FilterBar, type FilterDefinition } from '../components/FilterBar';
import { ActionsChart } from '../components/ActionsChart';
import { HelpButton } from '../components/HelpButton';
import { EmptyState } from '@/features/academico/components/EmptyState';
import type { InteraccionDocente, ComunicacionDocente, AccionLog } from '../types';

const filterDefs: FilterDefinition[] = [
  {
    key: 'rango_fechas',
    label: 'Rango de fechas',
    type: 'date-range',
  },
  { key: 'materia_id', label: 'Materia', type: 'text', placeholder: 'ID de la materia' },
  { key: 'usuario_id', label: 'Usuario', type: 'text', placeholder: 'ID del usuario' },
];

export function MonitorCoordinacionPage() {
  const { session, hasPermission } = useAuth();
  const isAdmin = session.status === 'authenticated' && session.user.roles.includes('ADMIN');
  const canViewAll = hasPermission('monitor:coordinacion:ver_todo');

  const [filterValues, setFilterValues] = useState<
    Record<string, string | string[] | { desde?: string; hasta?: string }>
  >({});

  const apiFilters: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(filterValues)) {
    if (key === 'rango_fechas' && typeof value === 'object' && value !== null && !Array.isArray(value)) {
      const range = value as { desde?: string; hasta?: string };
      if (range.desde) apiFilters.desde = range.desde;
      if (range.hasta) apiFilters.hasta = range.hasta;
    } else if (typeof value === 'string' && value) {
      apiFilters[key] = value;
    }
  }

  const { data, isLoading, isError } = useMonitorCoordinacion(
    Object.keys(apiFilters).length > 0 ? apiFilters : undefined,
  );

  const interaccionesColumns: ColumnDef<InteraccionDocente>[] = [
    { key: 'docente_nombre', label: 'Docente' },
    { key: 'materia_nombre', label: 'Materia' },
    {
      key: 'acciones',
      label: 'Acciones por tipo',
      render: (row) => (
        <div className="flex flex-wrap gap-1">
          {Object.entries(row.acciones).map(([tipo, count]) => (
            <span
              key={tipo}
              className="inline-flex rounded-full bg-primary/10 px-2 py-0.5 text-label-xs text-primary"
            >
              {tipo}: {count}
            </span>
          ))}
        </div>
      ),
    },
  ];

  const comunicacionesColumns: ColumnDef<ComunicacionDocente>[] = [
    { key: 'docente_nombre', label: 'Docente' },
    { key: 'total_enviados', label: 'Total' },
    { key: 'pendientes', label: 'Pendientes' },
    { key: 'ok', label: 'OK' },
    { key: 'fallidos', label: 'Fallidos' },
  ];

  const logColumns: ColumnDef<AccionLog>[] = [
    { key: 'usuario_nombre', label: 'Usuario' },
    { key: 'accion', label: 'Acción' },
    { key: 'detalle', label: 'Detalle', render: (row) => row.detalle ?? '-' },
    { key: 'materia_nombre', label: 'Materia', render: (row) => row.materia_nombre ?? '-' },
    { key: 'created_at', label: 'Fecha', render: (row) => new Date(row.created_at).toLocaleString('es-AR') },
  ];

  const monitorData = data?.data;

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          <div>
            <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Monitor de Coordinación</h2>
            <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>
              Monitoreo detallado de actividad por coordinación
            </p>
          </div>
          <HelpButton tooltip="Vista detallada de actividad docente filtrada por rango de fechas, materia o usuario." />
        </div>
      </div>

      {(!isAdmin || !canViewAll) && (
        <div className="rounded-xl border border-warning/30 bg-warning/5 px-4 py-3 text-label-sm text-warning">
          <span className="material-symbols-outlined mr-1 align-middle text-[16px]">info</span>
          Mostrando datos de tu área (propio)
        </div>
      )}
      {isAdmin && canViewAll && (
        <div className="rounded-xl border border-primary/30 bg-primary/5 px-4 py-3 text-label-sm text-primary">
          <span className="material-symbols-outlined mr-1 align-middle text-[16px]">visibility</span>
          Mostrando datos de todo el tenant
        </div>
      )}

      <FilterBar
        filters={filterDefs}
        values={filterValues}
        onChange={(key, value) => {
          setFilterValues((prev) => ({ ...prev, [key]: value }));
        }}
        onClear={() => setFilterValues({})}
      />

      {isError ? (
        <EmptyState message="Error al cargar los datos del monitor" icon="error" />
      ) : isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-outline-variant border-t-primary" />
        </div>
      ) : monitorData ? (
        <>
          {monitorData.acciones_por_dia.length > 0 && (
            <div className="rounded-xl border border-outline-variant bg-surface-container-lowest p-4">
              <h3 className="text-label-md font-medium text-on-surface mb-3">
                Acciones por día
              </h3>
              <ActionsChart data={monitorData.acciones_por_dia} height={180} />
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="rounded-xl border border-outline-variant bg-surface-container-lowest p-4">
              <h3 className="text-label-md font-medium text-on-surface mb-3">
                Comunicaciones por docente
              </h3>
              <DataTable
                columns={comunicacionesColumns}
                data={monitorData.comunicaciones}
                rowKey="docente_id"
                emptyMessage="Sin comunicaciones registradas"
              />
            </div>

            <div className="rounded-xl border border-outline-variant bg-surface-container-lowest p-4">
              <h3 className="text-label-md font-medium text-on-surface mb-3">
                Interacciones por docente × materia
              </h3>
              <DataTable
                columns={interaccionesColumns}
                data={monitorData.interacciones}
                rowKey={(row) => `${row.docente_id}-${row.materia_id}`}
                emptyMessage="Sin interacciones registradas"
              />
            </div>
          </div>

          <div className="rounded-xl border border-outline-variant bg-surface-container-lowest p-4">
            <h3 className="text-label-md font-medium text-on-surface mb-3">
              Últimas acciones
            </h3>
            <DataTable
              columns={logColumns}
              data={monitorData.ultimas_acciones}
              rowKey="id"
              emptyMessage="Sin acciones registradas"
            />
          </div>
        </>
      ) : (
        <EmptyState message="No hay datos disponibles para el monitor" icon="monitoring" />
      )}
    </div>
  );
}
