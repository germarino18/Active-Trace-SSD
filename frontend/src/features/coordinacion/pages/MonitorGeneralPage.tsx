import { useState } from 'react';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { useMonitorGeneral } from '../hooks/useMonitores';
import { ActionsChart } from '../components/ActionsChart';
import { DataTable, type ColumnDef } from '../components/DataTable';
import { HelpButton } from '../components/HelpButton';
import { EmptyState } from '@/features/academico/components/EmptyState';
import type { AccionPorDia, ComunicacionDocente, InteraccionDocente, AccionLog } from '../types';

export function MonitorGeneralPage() {
  const { session, hasPermission } = useAuth();
  const isAdmin = session.status === 'authenticated' && session.user.roles.includes('ADMIN');
  const canViewAll = hasPermission('monitor:general:ver_todo');

  const [maxLogEntries, setMaxLogEntries] = useState(200);

  const { data, isLoading, isError } = useMonitorGeneral({
    max_acciones: maxLogEntries,
  });

  const accionesColumns: ColumnDef<AccionPorDia>[] = [
    { key: 'fecha', label: 'Fecha', render: (row) => new Date(row.fecha).toLocaleDateString('es-AR') },
    { key: 'cantidad', label: 'Cantidad' },
  ];

  const comunicacionesColumns: ColumnDef<ComunicacionDocente>[] = [
    { key: 'docente_nombre', label: 'Docente' },
    { key: 'total_enviados', label: 'Total' },
    { key: 'pendientes', label: 'Pendientes' },
    { key: 'ok', label: 'Enviados OK' },
    { key: 'fallidos', label: 'Fallidos' },
  ];

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

  const logColumns: ColumnDef<AccionLog>[] = [
    { key: 'usuario_nombre', label: 'Usuario' },
    { key: 'accion', label: 'Acción' },
    { key: 'detalle', label: 'Detalle', render: (row) => row.detalle ?? '-' },
    { key: 'materia_nombre', label: 'Materia', render: (row) => row.materia_nombre ?? '-' },
    { key: 'created_at', label: 'Fecha', render: (row) => new Date(row.created_at).toLocaleString('es-AR') },
  ];

  const monitorData = data?.data;
  const totalAcciones = data?.total_acciones ?? 0;

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          <div>
            <h2 className="font-headline-lg text-headline-lg text-on-surface">Monitor General</h2>
            <p className="text-body-md text-on-surface-variant mt-1">
              Panel de monitoreo general de actividad del sistema
            </p>
          </div>
          <HelpButton tooltip="Vista general de acciones, comunicaciones e interacciones del sistema." />
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

      {isError ? (
        <EmptyState message="Error al cargar los datos del monitor" icon="error" />
      ) : isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-outline-variant border-t-primary" />
        </div>
      ) : monitorData ? (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="rounded-xl border border-outline-variant bg-surface-container-lowest p-4">
              <h3 className="text-label-md font-medium text-on-surface mb-3">
                Acciones por día (últimos 30 días)
              </h3>
              <ActionsChart data={monitorData.acciones_por_dia} height={200} />
              <p className="mt-2 text-label-xs text-on-surface-variant">
                Total: {totalAcciones} acciones registradas
              </p>
            </div>

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

          <div className="rounded-xl border border-outline-variant bg-surface-container-lowest p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-label-md font-medium text-on-surface">
                Últimas acciones
              </h3>
              <div className="flex items-center gap-2">
                <label className="text-label-xs text-on-surface-variant">Máx registros:</label>
                <input
                  type="number"
                  min={10}
                  max={1000}
                  value={maxLogEntries}
                  onChange={(e) => setMaxLogEntries(Number(e.target.value))}
                  className="w-20 rounded-lg border border-outline-variant bg-surface-container px-2 py-1 text-label-xs text-on-surface outline-none focus:border-primary"
                />
              </div>
            </div>
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
