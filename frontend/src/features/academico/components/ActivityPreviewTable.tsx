import type { Actividad } from '../types';

interface ActivityPreviewTableProps {
  actividades: Actividad[];
  onToggle: (id: string) => void;
}

export function ActivityPreviewTable({ actividades, onToggle }: ActivityPreviewTableProps) {
  if (actividades.length === 0) {
    return (
      <p className="text-body-md text-on-surface-variant py-4 text-center">
        No se detectaron actividades en el archivo.
      </p>
    );
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-outline-variant">
      <table className="w-full text-left text-label-md">
        <thead>
          <tr className="border-b border-outline-variant bg-surface-container-low">
            <th className="px-4 py-3 font-medium text-on-surface">Incluir</th>
            <th className="px-4 py-3 font-medium text-on-surface">Actividad</th>
            <th className="px-4 py-3 font-medium text-on-surface">Tipo</th>
            <th className="px-4 py-3 font-medium text-on-surface">Calificaciones</th>
          </tr>
        </thead>
        <tbody>
          {actividades.map((actividad) => (
            <tr
              key={actividad.id}
              className="border-b border-outline-variant transition-colors hover:bg-surface-container-low"
            >
              <td className="px-4 py-3">
                <input
                  type="checkbox"
                  checked={actividad.selected ?? true}
                  onChange={() => onToggle(actividad.id)}
                  className="h-4 w-4 rounded border-outline-variant text-primary focus:ring-primary"
                />
              </td>
              <td className="px-4 py-3 text-on-surface">{actividad.nombre}</td>
              <td className="px-4 py-3 text-on-surface-variant">{actividad.tipo}</td>
              <td className="px-4 py-3 text-on-surface-variant">{actividad.calificaciones_count}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
