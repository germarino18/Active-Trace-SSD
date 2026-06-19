import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Spinner } from '@/shared/components/Spinner';
import { EmptyState, Badge, Button } from '@/shared/components/ds';
import * as alumnoService from '../services/alumno.service';

const estadoTone: Record<string, 'primary' | 'success' | 'neutral' | 'danger'> = {
  Enviado: 'primary',
  Entregado: 'success',
  Leido: 'neutral',
  Error: 'danger',
};

export function MisComunicacionesPage() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['alumno', 'comunicaciones'],
    queryFn: () => alumnoService.getComunicaciones(),
  });

  if (isLoading) return <div className="flex justify-center py-12"><Spinner size="lg" /></div>;

  if (error) {
    return (
      <EmptyState
        icon="error"
        title="Error al cargar comunicaciones"
        action={<Button variant="secondary" icon="refresh" onClick={() => refetch()}>Reintentar</Button>}
      />
    );
  }

  if (!data || data.length === 0) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
        <PageHeader />
        <EmptyState icon="forward_to_inbox" title="No tenés comunicaciones recibidas" />
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <PageHeader />

      <div style={{ overflowX: 'auto', borderRadius: 'var(--radius-lg)', border: '1px solid var(--outline-variant)' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ background: 'var(--surface-container)' }}>
              {['Remitente', 'Materia', 'Asunto', 'Fecha', 'Estado'].map((h) => (
                <th key={h} style={{ padding: '12px 16px', fontSize: 11, fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--on-surface-variant)' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((com, i) => (
              <tr
                key={com.id}
                style={{ borderTop: i > 0 ? '1px solid var(--outline-variant)' : undefined, background: 'var(--surface-container-lowest)', transition: 'background .12s ease' }}
                onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--surface-container-low)')}
                onMouseLeave={(e) => (e.currentTarget.style.background = 'var(--surface-container-lowest)')}
              >
                <td style={{ padding: '12px 16px' }}>
                  <Link
                    to={`/alumno/comunicaciones/${com.id}`}
                    style={{ fontSize: 14, color: 'var(--primary)', textDecoration: 'none', fontWeight: 600 }}
                    onMouseEnter={(e) => (e.currentTarget.style.textDecoration = 'underline')}
                    onMouseLeave={(e) => (e.currentTarget.style.textDecoration = 'none')}
                  >
                    {com.remitente}
                  </Link>
                </td>
                <td style={{ padding: '12px 16px', fontSize: 13, color: 'var(--on-surface-variant)' }}>{com.materia_nombre}</td>
                <td style={{ padding: '12px 16px', fontSize: 14, color: 'var(--on-surface)' }}>{com.asunto}</td>
                <td style={{ padding: '12px 16px', fontSize: 13, color: 'var(--on-surface-variant)', fontFamily: 'var(--font-mono)' }}>
                  {new Date(com.fecha_envio).toLocaleDateString('es-AR')}
                </td>
                <td style={{ padding: '12px 16px' }}>
                  <Badge tone={estadoTone[com.estado] ?? 'neutral'}>{com.estado}</Badge>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function PageHeader() {
  return (
    <div>
      <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Comunicaciones</h2>
      <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>Historial de comunicaciones recibidas</p>
    </div>
  );
}
