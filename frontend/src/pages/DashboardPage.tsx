import { useAuth } from '@/features/auth/hooks/useAuth';
import { StatCard, Card } from '@/shared/components/ds';
import { useProfesorDashboard } from '@/features/profesor/hooks/useProfesor';

const ROLE_CONFIG: Record<string, { icon: string; stats: Array<{ label: string; value: string; icon: string; trend?: string }> }> = {
  ALUMNO: {
    icon: 'school',
    stats: [
      { label: 'Materias activas', value: '—', icon: 'menu_book' },
      { label: 'Promedio general', value: '—', icon: 'grade' },
      { label: 'Comunicaciones', value: '—', icon: 'mail' },
    ],
  },
  PROFESOR: {
    icon: 'person_book',
    stats: [
      { label: 'Materias asignadas', value: '—', icon: 'class' },
      { label: 'Alumnos en riesgo', value: '—', icon: 'warning', trend: 'Requieren atención' },
      { label: 'Entregas pendientes', value: '—', icon: 'assignment_late' },
    ],
  },
  TUTOR: {
    icon: 'supervisor_account',
    stats: [
      { label: 'Alumnos a cargo', value: '—', icon: 'people' },
      { label: 'En riesgo', value: '—', icon: 'warning' },
      { label: 'Guardias esta semana', value: '—', icon: 'calendar_today' },
    ],
  },
  COORDINADOR: {
    icon: 'manage_accounts',
    stats: [
      { label: 'Equipos activos', value: '—', icon: 'groups' },
      { label: 'Alumnos totales', value: '—', icon: 'people' },
      { label: 'Tareas pendientes', value: '—', icon: 'task_alt' },
    ],
  },
  ADMIN: {
    icon: 'admin_panel_settings',
    stats: [
      { label: 'Usuarios activos', value: '—', icon: 'person' },
      { label: 'Alumnos en riesgo', value: '—', icon: 'warning' },
      { label: 'Progreso promedio', value: '—', icon: 'trending_up', trend: 'del tenant' },
    ],
  },
};

const FALLBACK_CONFIG = ROLE_CONFIG.ADMIN;

export function DashboardPage() {
  const { session } = useAuth();

  const primaryRole =
    session.status === 'authenticated' ? (session.user.roles[0]?.toUpperCase() ?? '') : '';

  const { data: profesorData } = useProfesorDashboard(primaryRole === 'PROFESOR');

  if (session.status !== 'authenticated') return null;

  const { user } = session;
  const config = ROLE_CONFIG[primaryRole] ?? FALLBACK_CONFIG;

  const resolvedStats =
    primaryRole === 'PROFESOR'
      ? [
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
        ]
      : config.stats;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div>
        <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Panel Principal</h2>
        <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>
          Bienvenido, {user.nombre} {user.apellido}
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16 }}>
        {resolvedStats.map((stat) => (
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
        <Card
          title="Resumen"
          icon={config.icon}
          variant="default"
        >
          <p style={{ margin: 0, fontSize: 14, color: 'var(--on-surface-variant)' }}>
            Los datos en tiempo real se cargarán al conectar el backend. Navegá a las secciones del menú lateral para gestionar tu actividad.
          </p>
        </Card>
      </div>
    </div>
  );
}
