import { Link, useLocation } from 'react-router-dom';

const routeLabels: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/profile': 'Mi Perfil',
  '/materias': 'Calificaciones',
  '/materias/importar': 'Importar',
  '/equipos': 'Equipos Docentes',
  '/equipos/mis-equipos': 'Mis Equipos',
  '/equipos/asignar': 'Asignar Equipo',
  '/equipos/masiva': 'Asignación Masiva',
  '/equipos/clonar': 'Clonar Equipo',
  '/equipos/vigencia': 'Modificar Vigencia',
  '/avisos': 'Avisos',
  '/avisos/nuevo': 'Nuevo Aviso',
  '/tareas': 'Tareas',
  '/tareas/mias': 'Mis Tareas',
  '/tareas/nueva': 'Nueva Tarea',
  '/encuentros': 'Encuentros',
  '/encuentros/nuevo': 'Nuevo Encuentro',
  '/coloquios': 'Coloquios',
  '/coloquios/nuevo': 'Nueva Convocatoria',
  '/programas': 'Programas',
  '/programas/nuevo': 'Nuevo Programa',
  '/fechas': 'Fechas Académicas',
  '/monitores/general': 'Monitor General',
  '/monitores/coordinacion': 'Monitor Coordinación',
  '/tutor/alumnos': 'Mis Alumnos',
  '/entregas-sin-corregir': 'Entregas sin Corregir',
  '/guardias': 'Guardias',
  '/admin/estructura': 'Estructura Académica',
  '/admin/usuarios': 'Usuarios',
  '/admin/auditoria': 'Auditoría',
  '/admin/metricas': 'Métricas',
  '/admin/analytics': 'Analytics',
  '/alumno/dashboard': 'Dashboard Alumno',
  '/alumno/materias': 'Mis Materias',
  '/alumno/coloquios': 'Coloquios',
  '/alumno/avisos': 'Avisos',
  '/alumno/programas': 'Programas',
  '/alumno/fechas': 'Calendario',
  '/alumno/inbox': 'Mensajes',
  '/alumno/comunicaciones': 'Comunicaciones',
  '/finanzas/liquidaciones': 'Liquidaciones',
  '/finanzas/grilla': 'Grilla Salarial',
  '/finanzas/facturas': 'Facturas',
};

export function Breadcrumbs() {
  const location = useLocation();
  const segments = location.pathname.split('/').filter(Boolean);

  if (segments.length === 0) return null;

  const crumbs = segments.map((_, index) => {
    const path = '/' + segments.slice(0, index + 1).join('/');
    return {
      label: routeLabels[path] || segments[index]?.replace(/-/g, ' ') || path,
      path,
    };
  });

  // On mobile: only show current page name; on desktop: full breadcrumb trail
  const currentLabel = crumbs[crumbs.length - 1]?.label ?? '';

  return (
    <nav className="flex items-center gap-2 text-label-sm text-on-surface-variant">
      {/* Mobile: current page only */}
      <span className="text-on-surface capitalize sm:hidden">{currentLabel}</span>
      {/* Desktop: full trail */}
      <span className="hidden sm:flex items-center gap-2">
        {crumbs.map((crumb, index) => (
          <span key={crumb.path} className="flex items-center gap-2">
            {index > 0 && <span className="text-outline">/</span>}
            {index < crumbs.length - 1 ? (
              <Link to={crumb.path} className="hover:text-primary transition-colors capitalize">
                {crumb.label}
              </Link>
            ) : (
              <span className="text-on-surface capitalize">{crumb.label}</span>
            )}
          </span>
        ))}
      </span>
    </nav>
  );
}
