import { Link } from 'react-router-dom';
import type { MateriaDashboardItem } from '../types/alumno.types';

interface MateriaCardProps {
  materia: MateriaDashboardItem;
}

const estadoStyles: Record<string, string> = {
  al_dia: 'bg-tertiary/10 text-tertiary border-tertiary/30',
  atrasado: 'bg-error/10 text-error border-error/30',
  sin_actividad: 'bg-surface-container-high text-on-surface-variant border-outline-variant',
};

const estadoLabels: Record<string, string> = {
  al_dia: 'Al día',
  atrasado: 'Atrasado',
  sin_actividad: 'Sin actividad',
};

export function MateriaCard({ materia }: MateriaCardProps) {
  const progreso = materia.progreso.total > 0
    ? Math.round((materia.progreso.aprobadas / materia.progreso.total) * 100)
    : 0;

  return (
    <Link
      to={`/alumno/materias/${materia.id}`}
      className="block bg-surface-container-lowest rounded-xl border border-outline-variant p-4 transition-colors hover:border-primary/50 hover:bg-surface-container-low"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <h3 className="text-label-md font-medium text-on-surface truncate">{materia.nombre}</h3>
          <p className="text-label-sm text-on-surface-variant mt-0.5 truncate">{materia.profesor}</p>
        </div>
        <span className={`inline-flex shrink-0 items-center rounded-full border px-2.5 py-0.5 text-label-xs font-medium ${estadoStyles[materia.estado]}`}>
          {estadoLabels[materia.estado]}
        </span>
      </div>

      <div className="space-y-1.5">
        <div className="flex items-center justify-between text-label-xs text-on-surface-variant">
          <span>Progreso</span>
          <span>{materia.progreso.aprobadas}/{materia.progreso.total} actividades</span>
        </div>
        <div className="h-2 w-full rounded-full bg-surface-container">
          <div
            className="h-full rounded-full bg-primary transition-all"
            style={{ width: `${progreso}%` }}
          />
        </div>
      </div>
    </Link>
  );
}
