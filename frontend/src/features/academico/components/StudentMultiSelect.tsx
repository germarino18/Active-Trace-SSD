import type { AtrasadoEntry } from '../types';
import { EmptyState } from './EmptyState';
import { LoadingState } from './LoadingState';

interface StudentMultiSelectProps {
  students?: AtrasadoEntry[];
  selectedIds: Set<string>;
  onToggle: (id: string) => void;
  isLoading?: boolean;
}

export function StudentMultiSelect({ students, selectedIds, onToggle, isLoading }: StudentMultiSelectProps) {
  if (isLoading) {
    return <LoadingState rows={4} cols={4} />;
  }

  if (!students || students.length === 0) {
    return <EmptyState message="No hay alumnos atrasados para comunicar" />;
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <p className="text-label-sm font-medium text-on-surface">
          Alumnos atrasados ({students.length})
        </p>
        <p className="text-label-xs text-outline">
          {selectedIds.size} seleccionados
        </p>
      </div>
      <div className="overflow-x-auto rounded-xl border border-outline-variant">
        <table className="w-full text-left text-label-md">
          <thead>
            <tr className="border-b border-outline-variant bg-surface-container-low">
              <th className="w-12 px-4 py-3" />
              <th className="px-4 py-3 font-medium text-on-surface">Nombre</th>
              <th className="px-4 py-3 font-medium text-on-surface">Email</th>
              <th className="px-4 py-3 font-medium text-on-surface">Comisión</th>
              <th className="px-4 py-3 font-medium text-on-surface">Pendientes</th>
            </tr>
          </thead>
          <tbody>
            {students.map((entry) => (
              <tr
                key={entry.alumno.id}
                className="border-b border-outline-variant transition-colors hover:bg-surface-container-low"
              >
                <td className="px-4 py-3">
                  <input
                    type="checkbox"
                    checked={selectedIds.has(entry.alumno.id)}
                    onChange={() => onToggle(entry.alumno.id)}
                    className="h-4 w-4 rounded border-outline-variant text-primary focus:ring-primary"
                  />
                </td>
                <td className="px-4 py-3 text-on-surface font-medium">
                  {entry.alumno.apellido}, {entry.alumno.nombre}
                </td>
                <td className="px-4 py-3 text-on-surface-variant">{entry.alumno.email}</td>
                <td className="px-4 py-3 text-on-surface-variant">{entry.alumno.comision}</td>
                <td className="px-4 py-3 text-on-surface-variant">{entry.actividades_pendientes}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
