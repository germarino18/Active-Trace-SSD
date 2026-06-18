import type { EntregaEntry } from '../types';
import { EmptyState } from './EmptyState';
import { LoadingState } from './LoadingState';

interface TablaEntregasPendientesProps {
  data?: EntregaEntry[];
  isLoading?: boolean;
}

export function TablaEntregasPendientes({ data, isLoading }: TablaEntregasPendientesProps) {
  if (isLoading) {
    return <LoadingState rows={5} cols={4} />;
  }

  if (!data || data.length === 0) {
    return <EmptyState message="No se detectaron entregas sin corregir" />;
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-outline-variant">
      <table className="w-full text-left text-label-md">
        <thead>
          <tr className="border-b border-outline-variant bg-surface-container-low">
            <th className="px-4 py-3 font-medium text-on-surface">Alumno</th>
            <th className="px-4 py-3 font-medium text-on-surface">Actividad</th>
            <th className="px-4 py-3 font-medium text-on-surface">Fecha de Entrega</th>
            <th className="px-4 py-3 font-medium text-on-surface">Estado</th>
          </tr>
        </thead>
        <tbody>
          {data.map((entry, index) => (
            <tr
              key={`${entry.alumno.id}-${entry.actividad}-${index}`}
              className="border-b border-outline-variant transition-colors hover:bg-surface-container-low"
            >
              <td className="px-4 py-3 text-on-surface font-medium">
                {entry.alumno.apellido}, {entry.alumno.nombre}
              </td>
              <td className="px-4 py-3 text-on-surface-variant">{entry.actividad}</td>
              <td className="px-4 py-3 text-on-surface-variant">
                {new Date(entry.fecha_entrega).toLocaleDateString('es-AR')}
              </td>
              <td className="px-4 py-3">
                <span className="inline-flex rounded-full bg-warning/10 px-2 py-0.5 text-label-xs font-medium text-warning">
                  {entry.estado}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
