import { Link } from 'react-router-dom';
import { Badge, ProgressBar } from '@/shared/components/ds';
import type { MateriaDashboardItem } from '../types/alumno.types';

interface MateriaCardProps {
  materia: MateriaDashboardItem;
}

const estadoTone: Record<string, 'success' | 'danger' | 'neutral'> = {
  al_dia: 'success',
  atrasado: 'danger',
  sin_actividad: 'neutral',
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
      style={{ textDecoration: 'none', display: 'block' }}
    >
      <div
        style={{
          background: 'var(--surface-container-lowest)',
          borderRadius: 'var(--radius-lg)',
          border: '1px solid var(--outline-variant)',
          padding: 16,
          transition: 'border-color .15s ease, background .15s ease',
          cursor: 'pointer',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.borderColor = 'color-mix(in srgb, var(--primary) 50%, transparent)';
          e.currentTarget.style.background = 'var(--surface-container-low)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.borderColor = 'var(--outline-variant)';
          e.currentTarget.style.background = 'var(--surface-container-lowest)';
        }}
      >
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 12 }}>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--on-surface)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {materia.nombre}
            </div>
            <div style={{ fontSize: 12, color: 'var(--on-surface-variant)', marginTop: 2, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {materia.profesor}
            </div>
          </div>
          <div style={{ marginLeft: 8, flexShrink: 0 }}>
            <Badge tone={estadoTone[materia.estado]}>{estadoLabels[materia.estado]}</Badge>
          </div>
        </div>

        <ProgressBar
          value={progreso}
          label={`${materia.progreso.aprobadas}/${materia.progreso.total} actividades`}
          showValue
        />
      </div>
    </Link>
  );
}
