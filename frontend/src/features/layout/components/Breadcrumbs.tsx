import { Link, useLocation } from 'react-router-dom';

const routeLabels: Record<string, string> = {
  '/alumno/dashboard': 'Dashboard',
  '/profile': 'Mi Perfil',
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

  return (
    <nav className="flex items-center gap-2 text-label-sm text-on-surface-variant">
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
    </nav>
  );
}
