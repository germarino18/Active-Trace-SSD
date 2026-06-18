import { Navigate, Link } from 'react-router-dom';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { Card } from '@/shared/components/ui/Card';
import { StatCard } from '@/shared/components/ui/StatCard';
import { Badge } from '@/shared/components/ui/Badge';

type Role = string;

const ROLE_REDIRECTS: Record<Role, string> = {
  ALUMNO: '/alumno/dashboard',
  ADMIN: '/admin/metricas',
  FINANZAS: '/finanzas/liquidaciones',
  TUTOR: '/tutor/alumnos',
};

interface QuickLink {
  label: string;
  path: string;
  icon: string;
  desc: string;
}

const QUICK_LINKS: Record<string, QuickLink[]> = {
  COORDINADOR: [
    { label: 'Equipos Docentes', path: '/equipos', icon: 'groups', desc: 'Gestioná las asignaciones del cuerpo docente' },
    { label: 'Avisos', path: '/avisos', icon: 'campaign', desc: 'Gestioná avisos y comunicaciones' },
    { label: 'Tareas', path: '/tareas', icon: 'checklist', desc: 'Administrá las tareas pendientes' },
    { label: 'Encuentros', path: '/encuentros', icon: 'event', desc: 'Coordiná encuentros y fechas' },
    { label: 'Coloquios', path: '/coloquios', icon: 'quiz', desc: 'Administrá convocatorias' },
    { label: 'Programas', path: '/programas', icon: 'description', desc: 'Gestioná programas académicos' },
    { label: 'Fechas', path: '/fechas', icon: 'calendar_month', desc: 'Calendario académico' },
    { label: 'Monitores', path: '/monitores/general', icon: 'monitoring', desc: 'Seguimiento y monitoreo' },
  ],
  PROFESOR: [
    { label: 'Calificaciones', path: '/materias', icon: 'grading', desc: 'Gestioná calificaciones de tus materias' },
    { label: 'Entregas sin corregir', path: '/entregas-sin-corregir', icon: 'assignment_late', desc: 'Revisá entregas pendientes' },
    { label: 'Guardias', path: '/guardias', icon: 'shield', desc: 'Tus guardias asignadas' },
    { label: 'Atrasados', path: '/materias', icon: 'warning', desc: 'Alumnos con atraso' },
    { label: 'Coloquios', path: '/coloquios', icon: 'quiz', desc: 'Evaluaciones y coloquios' },
  ],
  NEXO: [
    { label: 'Dashboard Alumno', path: '/alumno/dashboard', icon: 'dashboard', desc: 'Vista general del estado académico' },
    { label: 'Mis Materias', path: '/alumno/materias', icon: 'school', desc: 'Consultá materias y progreso' },
    { label: 'Coloquios', path: '/alumno/coloquios', icon: 'quiz', desc: 'Evaluaciones registradas' },
    { label: 'Comunicaciones', path: '/alumno/comunicaciones', icon: 'forward_to_inbox', desc: 'Comunicaciones recibidas' },
  ],
};

function getFirstRedirectRole(roles: string[]): string | null {
  for (const role of roles) {
    if (ROLE_REDIRECTS[role]) return ROLE_REDIRECTS[role];
  }
  return null;
}

function getQuickLinksForRoles(roles: string[]): QuickLink[] | null {
  for (const role of roles) {
    if (QUICK_LINKS[role]) return QUICK_LINKS[role];
  }
  return null;
}

function getRoleLabel(roles: string[]): string {
  if (roles.includes('COORDINADOR')) return 'Coordinador';
  if (roles.includes('PROFESOR')) return 'Profesor';
  if (roles.includes('NEXO')) return 'Nexo';
  return roles[0] ?? 'Usuario';
}

export function DashboardPage() {
  const { session } = useAuth();

  if (session.status !== 'authenticated') {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-body-md text-on-surface-variant">Cargando...</p>
      </div>
    );
  }

  const roles = session.user.roles;

  // Redirect roles with a dedicated landing page
  const redirectPath = getFirstRedirectRole(roles);
  if (redirectPath) {
    return <Navigate to={redirectPath} replace />;
  }

  // If we get here, user is COORDINADOR, PROFESOR, or NEXO
  const quickLinks = getQuickLinksForRoles(roles);
  const roleLabel = getRoleLabel(roles);

  return (
    <div className="space-y-lg">
      {/* Welcome Section */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="primary">{roleLabel}</Badge>
            <span className="text-label-sm text-outline">Panel Principal</span>
          </div>
          <h2 className="text-headline-lg font-semibold text-on-surface">
            Panel de {roleLabel === 'Coordinador' ? 'Coordinación' : roleLabel === 'Nexo' ? 'Consultas' : 'Control'}
          </h2>
          <p className="text-body-md text-on-surface-variant mt-1">
            Bienvenido, {session.user.nombre} {session.user.apellido}
          </p>
        </div>
      </div>

      {/* Quick Links — Bento Grid */}
      {quickLinks && (
        <div className="bento-grid">
          {quickLinks.map((link) => (
            <Link
              key={link.path}
              to={link.path}
              className="col-span-12 sm:col-span-6 lg:col-span-4 xl:col-span-3 group"
            >
              <Card hover padding="md" className="h-full">
                <div className="flex items-start gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary shrink-0">
                    <span className="material-symbols-outlined text-[22px]">{link.icon}</span>
                  </div>
                  <div className="min-w-0 flex-1">
                    <h3 className="text-label-md font-semibold text-on-surface group-hover:text-primary transition-colors">
                      {link.label}
                    </h3>
                    <p className="text-body-sm text-on-surface-variant mt-1 line-clamp-2">
                      {link.desc}
                    </p>
                  </div>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}

      {/* KPIs Row */}
      <div className="bento-grid">
        <div className="col-span-12 sm:col-span-6 lg:col-span-3">
          <StatCard
            icon="school"
            label="Materias"
            value="—"
            variant="primary"
          />
        </div>
        <div className="col-span-12 sm:col-span-6 lg:col-span-3">
          <StatCard
            icon="people"
            label="Alumnos"
            value="—"
            variant="default"
          />
        </div>
        <div className="col-span-12 sm:col-span-6 lg:col-span-3">
          <StatCard
            icon="pending_actions"
            label="Pendientes"
            value="—"
            variant="default"
          />
        </div>
        <div className="col-span-12 sm:col-span-6 lg:col-span-3">
          <StatCard
            icon="notifications"
            label="Avisos"
            value={session.user.roles.length.toString()}
            variant="default"
          />
        </div>
      </div>

      {/* Activity Section */}
      <div className="bento-grid">
        {/* Actividad Reciente */}
        <div className="col-span-12 lg:col-span-7">
          <Card padding="md">
            <h3 className="text-label-md font-bold uppercase tracking-wider text-outline mb-md">
              Actividad Reciente
            </h3>
            <div className="space-y-sm">
              {[
                { icon: 'grading', color: 'bg-primary/20 text-primary', title: 'Calificaciones actualizadas', time: 'Hoy, 10:30 AM' },
                { icon: 'group_add', color: 'bg-tertiary-container text-tertiary', title: 'Nuevo equipo docente asignado', time: 'Ayer, 4:15 PM' },
                { icon: 'campaign', color: 'bg-error-container text-error', title: 'Aviso importante: fechas de coloquios', time: 'Ayer, 11:00 AM' },
                { icon: 'event', color: 'bg-surface-container-high text-outline', title: 'Encuentro programado: Álgebra II', time: '18 jun, 2026' },
              ].map((item, i) => (
                <div key={i} className="flex items-center gap-md p-sm bg-surface-container-low rounded-lg hover:bg-surface-variant transition-colors">
                  <div className={`w-8 h-8 rounded-full ${item.color} flex items-center justify-center shrink-0`}>
                    <span className="material-symbols-outlined text-[18px]">{item.icon}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-label-md text-on-surface truncate">{item.title}</p>
                    <p className="text-label-sm text-outline">{item.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Acceso Rápido */}
        <div className="col-span-12 lg:col-span-5">
          <Card padding="md">
            <h3 className="text-label-md font-bold uppercase tracking-wider text-outline mb-md">
              Accesos Directos
            </h3>
            <div className="space-y-sm">
              <Link
                to="/profile"
                className="flex items-center gap-md p-sm rounded-lg border border-outline-variant bg-surface-container-lowest hover:bg-surface-container-low transition-colors"
              >
                <div className="w-10 h-10 rounded-lg bg-primary/10 text-primary flex items-center justify-center">
                  <span className="material-symbols-outlined">person</span>
                </div>
                <div>
                  <p className="text-label-md font-medium text-on-surface">Mi Perfil</p>
                  <p className="text-label-sm text-outline">Datos personales y preferencias</p>
                </div>
              </Link>
              <Link
                to={roleLabel === 'Nexo' ? '/alumno/materias' : '/materias'}
                className="flex items-center gap-md p-sm rounded-lg border border-outline-variant bg-surface-container-lowest hover:bg-surface-container-low transition-colors"
              >
                <div className="w-10 h-10 rounded-lg bg-tertiary-container text-tertiary flex items-center justify-center">
                  <span className="material-symbols-outlined">school</span>
                </div>
                <div>
                  <p className="text-label-md font-medium text-on-surface">Mis Materias</p>
                  <p className="text-label-sm text-outline">Accedé a tus materias activas</p>
                </div>
              </Link>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
