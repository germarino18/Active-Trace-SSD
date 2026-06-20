import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Spinner } from '@/shared/components/Spinner';
import { EmptyState, Badge } from '@/shared/components/ds';
import * as alumnoService from '../services/alumno.service';

export function AlumnoInboxPage() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['alumno', 'inbox'],
    queryFn: () => alumnoService.getHilos(),
  });

  if (isLoading) return <div className="flex justify-center py-12"><Spinner size="lg" /></div>;

  if (error) {
    return (
      <EmptyState
        icon="error"
        title="Error al cargar mensajes"
        action={
          <button onClick={() => refetch()} style={{ fontSize: 13, color: 'var(--primary)', background: 'none', border: 'none', cursor: 'pointer', fontWeight: 500 }}>
            Reintentar
          </button>
        }
      />
    );
  }

  if (!data || data.length === 0) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
        <PageHeader unread={0} />
        <EmptyState icon="mail" title="No tenés mensajes" />
      </div>
    );
  }

  const unread = data.filter((h) => h.no_leido).length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <PageHeader unread={unread} />

      <div style={{ borderRadius: 'var(--radius-lg)', border: '1px solid var(--outline-variant)', overflow: 'hidden' }}>
        {data.map((hilo, i) => (
          <Link
            key={hilo.id}
            to={`/alumno/inbox/${hilo.id}`}
            style={{
              display: 'flex', alignItems: 'flex-start', gap: 16, padding: '12px 16px',
              textDecoration: 'none',
              background: hilo.no_leido ? 'color-mix(in srgb, var(--primary) 3%, var(--surface-container-lowest))' : 'var(--surface-container-lowest)',
              borderTop: i > 0 ? '1px solid var(--outline-variant)' : undefined,
              transition: 'background .15s ease',
            }}
            onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--surface-container-low)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = hilo.no_leido ? 'color-mix(in srgb, var(--primary) 3%, var(--surface-container-lowest))' : 'var(--surface-container-lowest)'; }}
          >
            <div style={{ position: 'relative', flexShrink: 0 }}>
              <div style={{ width: 40, height: 40, borderRadius: 'var(--radius-full)', background: 'color-mix(in srgb, var(--primary) 20%, transparent)', color: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, fontWeight: 700 }}>
                {hilo.remitente_nombre.charAt(0).toUpperCase()}
              </div>
              {hilo.no_leido && (
                <span style={{ position: 'absolute', top: -2, right: -2, width: 10, height: 10, borderRadius: 'var(--radius-full)', border: '2px solid var(--background)', background: 'var(--primary)' }} />
              )}
            </div>

            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 2 }}>
                <span style={{ fontSize: 14, fontWeight: hilo.no_leido ? 700 : 500, color: 'var(--on-surface)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {hilo.remitente_nombre}
                </span>
                <span style={{ fontSize: 12, color: 'var(--outline)', flexShrink: 0 }}>
                  {new Date(hilo.ultima_fecha).toLocaleDateString('es-AR')}
                </span>
                {hilo.no_leido && <Badge tone="primary" dot>Nuevo</Badge>}
              </div>
              <p style={{ margin: 0, fontSize: 13, fontWeight: hilo.no_leido ? 600 : 400, color: hilo.no_leido ? 'var(--on-surface)' : 'var(--on-surface-variant)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {hilo.asunto}
              </p>
              <p style={{ margin: '2px 0 0', fontSize: 12, color: 'var(--outline)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {hilo.ultimo_mensaje}
              </p>
            </div>

            <span className="material-symbols-outlined" style={{ fontSize: 18, color: 'var(--outline)', flexShrink: 0, alignSelf: 'center' }}>chevron_right</span>
          </Link>
        ))}
      </div>
    </div>
  );
}

function PageHeader({ unread }: { unread: number }) {
  return (
    <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
      <div>
        <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Mensajes</h2>
        <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>
          {unread > 0 ? `${unread} mensaje${unread !== 1 ? 's' : ''} sin leer` : 'Bandeja de entrada'}
        </p>
      </div>
    </div>
  );
}
