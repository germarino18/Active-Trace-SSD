import type { MonitorEntry } from '../types';
import { EmptyState } from './EmptyState';
import { LoadingState } from './LoadingState';

interface TablaMonitorProps {
  data?: MonitorEntry[];
  isLoading?: boolean;
}

export function TablaMonitor({ data, isLoading }: TablaMonitorProps) {
  if (isLoading) {
    return <LoadingState rows={5} cols={6} />;
  }

  if (!data || data.length === 0) {
    return <EmptyState message="No se encontraron alumnos con los filtros seleccionados" />;
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-outline-variant">
      <table className="w-full text-left text-label-md">
        <thead>
          <tr className="border-b border-outline-variant bg-surface-container-low">
            <th className="px-4 py-3 font-medium text-on-surface">Nombre</th>
            <th className="px-4 py-3 font-medium text-on-surface">Email</th>
            <th className="px-4 py-3 font-medium text-on-surface">Comisión</th>
            <th className="px-4 py-3 font-medium text-on-surface">Completadas</th>
            <th className="px-4 py-3 font-medium text-on-surface">Total</th>
            <th className="px-4 py-3 font-medium text-on-surface">Progreso</th>
            <th className="px-4 py-3 font-medium text-on-surface">Estado</th>
          </tr>
        </thead>
        <tbody>
          {data.map((entry) => (
            <tr
              key={entry.alumno.id}
              className="border-b border-outline-variant transition-colors hover:bg-surface-container-low"
            >
              <td className="px-4 py-3 text-on-surface font-medium">
                {entry.alumno.apellido}, {entry.alumno.nombre}
              </td>
              <td className="px-4 py-3 text-on-surface-variant">{entry.alumno.email}</td>
              <td className="px-4 py-3 text-on-surface-variant">{entry.alumno.comision}</td>
              <td className="px-4 py-3 text-on-surface-variant">{entry.actividades_completadas}</td>
              <td className="px-4 py-3 text-on-surface-variant">{entry.total_actividades}</td>
              <td className="px-4 py-3">
                <div className="flex items-center gap-2">
                  <div className="h-2 w-24 overflow-hidden rounded-full bg-surface-container-low">
                    <div
                      className={`h-full rounded-full transition-all ${
                        entry.porcentaje_completitud >= 80
                          ? 'bg-success'
                          : entry.porcentaje_completitud >= 50
                            ? 'bg-warning'
                            : 'bg-error'
                      }`}
                      style={{ width: `${entry.porcentaje_completitud}%` }}
                    />
                  </div>
                  <span className="text-label-xs text-on-surface-variant">
                    {entry.porcentaje_completitud}%
                  </span>
                </div>
              </td>
              <td className="px-4 py-3">
                <span
                  className={`inline-flex rounded-full px-2 py-0.5 text-label-xs font-medium ${
                    entry.porcentaje_completitud >= 80
                      ? 'bg-success/10 text-success'
                      : entry.porcentaje_completitud >= 50
                        ? 'bg-warning/10 text-warning'
                        : 'bg-error/10 text-error'
                  }`}
                >
                  {entry.porcentaje_completitud >= 80
                    ? 'Bueno'
                    : entry.porcentaje_completitud >= 50
                      ? 'Regular'
                      : 'Crítico'}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
