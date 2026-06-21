import { Link, useLocation, useParams } from 'react-router-dom';
import { useDictadoNombre } from '@/features/profesor/hooks/useProfesor';

const routeLabels: Record<string, string> = {
  '/alumno/dashboard': 'Dashboard',
  '/profile': 'Mi Perfil',
};

/** UUID v4 regex — detects raw UUID path segments */
const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

/** Sub-component that resolves a dictadoId UUID to its human label. */
function DictadoLabel({ dictadoId }: { dictadoId: string }) {
  const nombre = useDictadoNombre(dictadoId);
  return <span>{nombre}</span>;
}

export function Breadcrumbs() {
  const location = useLocation();
  // useParams() here gives us the :dictadoId if we are inside that route subtree
  const params = useParams<{ dictadoId?: string }>();
  const segments = location.pathname.split('/').filter(Boolean);

  if (segments.length === 0) return null;

  const crumbs = segments.map((seg, index) => {
    const path = '/' + segments.slice(0, index + 1).join('/');
    return { seg, path };
  });

  return (
    <nav className="flex items-center gap-2 text-label-sm text-on-surface-variant">
      {crumbs.map((crumb, index) => {
        const isLast = index === crumbs.length - 1;
        const isDictadoUuid = UUID_RE.test(crumb.seg) && params.dictadoId === crumb.seg;

        const labelNode = isDictadoUuid ? (
          <DictadoLabel dictadoId={crumb.seg} />
        ) : (
          <span>{routeLabels[crumb.path] || crumb.seg.replace(/-/g, ' ')}</span>
        );

        return (
          <span key={crumb.path} className="flex items-center gap-2">
            {index > 0 && <span className="text-outline">/</span>}
            {!isLast ? (
              <Link to={crumb.path} className="hover:text-primary transition-colors capitalize">
                {labelNode}
              </Link>
            ) : (
              <span className="text-on-surface capitalize">{labelNode}</span>
            )}
          </span>
        );
      })}
    </nav>
  );
}
