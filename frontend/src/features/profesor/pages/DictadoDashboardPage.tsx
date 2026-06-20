import { NavLink, Outlet, useParams } from 'react-router-dom';
import { useDictadoMetricas, useDictadoNombre } from '../hooks/useProfesor';
import { StatCard } from '@/shared/components/ds';

const tabs = [
  { label: 'Alumnos', path: 'alumnos', icon: 'group' },
  { label: 'Actividades', path: 'actividades', icon: 'assignment' },
  { label: 'Atrasados', path: 'atrasados', icon: 'warning' },
  { label: 'Equipo', path: 'equipo', icon: 'groups' },
];

export function DictadoDashboardPage() {
  const { dictadoId } = useParams<{ dictadoId: string }>();
  const { data, isLoading } = useDictadoMetricas(dictadoId!);
  const dictadoNombre = useDictadoNombre(dictadoId!);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div>
        <h2 style={{ margin: 0, fontSize: 28, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>
          {dictadoNombre}
        </h2>
      </div>

      {isLoading ? (
        <div
          role="status"
          aria-label="Cargando"
          style={{ display: 'flex', justifyContent: 'center', padding: '32px 0' }}
        >
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-outline-variant border-t-primary" />
        </div>
      ) : data ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 16 }}>
          <StatCard label="Total alumnos" value={String(data.total_alumnos)} icon="group" />
          <StatCard label="Aprobados" value={String(data.aprobados)} icon="check_circle" />
          <StatCard label="Atrasados" value={String(data.atrasados)} icon="warning" />
          <StatCard label="Actividades" value={String(data.total_actividades)} icon="assignment" />
          <StatCard
            label="Promedio general"
            value={data.promedio_general !== null ? data.promedio_general.toFixed(2) : '—'}
            icon="grade"
          />
          <StatCard label="Sin datos" value={String(data.sin_datos)} icon="help_outline" />
        </div>
      ) : null}

      <div style={{ borderBottom: '1px solid var(--outline-variant)' }}>
        <nav style={{ display: 'flex', gap: 4, marginBottom: -1, flexWrap: 'wrap' }}>
          {tabs.map((tab) => (
            <NavLink
              key={tab.path}
              to={tab.path}
              style={({ isActive }) => ({
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6,
                padding: '10px 16px',
                fontSize: 14,
                fontWeight: 500,
                fontFamily: 'var(--font-sans)',
                textDecoration: 'none',
                borderBottom: `2px solid ${isActive ? 'var(--primary)' : 'transparent'}`,
                color: isActive ? 'var(--primary)' : 'var(--on-surface-variant)',
                transition: 'color .15s ease, border-color .15s ease',
              })}
            >
              <span className="material-symbols-outlined" style={{ fontSize: 16 }}>{tab.icon}</span>
              {tab.label}
            </NavLink>
          ))}
        </nav>
      </div>

      <Outlet />
    </div>
  );
}
