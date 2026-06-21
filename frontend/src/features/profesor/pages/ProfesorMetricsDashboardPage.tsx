import { useAuth } from '@/features/auth/hooks/useAuth';
import { StatCard, Card } from '@/shared/components/ds';
import { useProfesorDashboard } from '../hooks/useProfesor';

/**
 * Dedicated dashboard for professors showing live metrics:
 * Materias asignadas, Alumnos en riesgo, Encuentros.
 *
 * This page was split out of the generic DashboardPage (D4 decision in design.md).
 * Registered at /profesor-dashboard in App.tsx.
 */
export function ProfesorMetricsDashboardPage() {
  const { session } = useAuth();
  const { data: profesorData } = useProfesorDashboard();

  if (session.status !== 'authenticated') return null;

  const { user } = session;

  const stats = [
    {
      label: 'Materias asignadas',
      value: profesorData ? String(profesorData.materias_asignadas.length) : '—',
      icon: 'class',
    },
    {
      label: 'Alumnos en riesgo',
      value: profesorData ? String(profesorData.total_atrasados) : '—',
      icon: 'warning',
      trend: 'Requieren atención',
    },
    {
      label: 'Encuentros',
      value: profesorData ? String(profesorData.total_encuentros) : '—',
      icon: 'assignment_late',
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div>
        <h2
          role="heading"
          aria-level={2}
          style={{
            margin: 0,
            fontSize: 32,
            fontWeight: 700,
            letterSpacing: '-0.01em',
            color: 'var(--on-surface)',
          }}
        >
          Dashboard del Profesor
        </h2>
        <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>
          Bienvenido, {user.nombre} {user.apellido} — resumen de tus dictados en tiempo real.
        </p>
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: 16,
        }}
      >
        {stats.map((stat) => (
          <StatCard
            key={stat.label}
            label={stat.label}
            value={stat.value}
            icon={stat.icon}
            trend={stat.trend}
          />
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 16 }}>
        <Card title="Mis Métricas" icon="person_book" variant="default">
          <p style={{ margin: 0, fontSize: 14, color: 'var(--on-surface-variant)' }}>
            Los datos se actualizan en tiempo real desde el backend. Navegá a{' '}
            <strong>Mis Dictados</strong> para gestionar alumnos, actividades y atrasados por dictado.
          </p>
        </Card>
      </div>
    </div>
  );
}
