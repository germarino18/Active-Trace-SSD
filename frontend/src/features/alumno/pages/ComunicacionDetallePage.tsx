import { useQuery } from '@tanstack/react-query';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { Spinner } from '@/shared/components/Spinner';
import { EmptyState, Badge, Button } from '@/shared/components/ds';
import * as alumnoService from '../services/alumno.service';

const estadoTone: Record<string, 'success' | 'primary' | 'neutral' | 'danger'> = {
  Enviado: 'primary',
  Entregado: 'success',
  Leido: 'neutral',
  Error: 'danger',
};

export function ComunicacionDetallePage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['alumno', 'comunicaciones', id],
    queryFn: () => alumnoService.getComunicacionDetalle(id!),
    enabled: !!id,
  });

  if (isLoading) return <div className="flex justify-center py-12"><Spinner size="lg" /></div>;

  if (error) {
    return (
      <EmptyState
        icon="error"
        title="Error al cargar comunicación"
        action={<Button variant="secondary" icon="refresh" onClick={() => refetch()}>Reintentar</Button>}
      />
    );
  }

  if (!data) {
    return <EmptyState icon="search_off" title="Comunicación no encontrada" />;
  }

  return (
    <div style={{ maxWidth: 720, display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, color: 'var(--on-surface-variant)' }}>
        <Link to="/alumno/comunicaciones" style={{ color: 'var(--on-surface-variant)', textDecoration: 'none' }}
          onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--primary)')}
          onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--on-surface-variant)')}
        >Comunicaciones</Link>
        <span className="material-symbols-outlined" style={{ fontSize: 16 }}>chevron_right</span>
        <span style={{ color: 'var(--on-surface)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{data.asunto}</span>
      </div>

      <div style={{ background: 'var(--surface-container-lowest)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--outline-variant)', padding: 28 }}>
        <h2 style={{ margin: '0 0 20px', fontSize: 24, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>{data.asunto}</h2>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 24, paddingBottom: 24, borderBottom: '1px solid var(--outline-variant)' }}>
          <div>
            <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--on-surface-variant)', marginBottom: 4 }}>Remitente</div>
            <div style={{ fontSize: 14, color: 'var(--on-surface)', fontWeight: 500 }}>{data.remitente}</div>
          </div>
          <div>
            <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--on-surface-variant)', marginBottom: 4 }}>Materia</div>
            <div style={{ fontSize: 14, color: 'var(--on-surface)' }}>{data.materia_nombre}</div>
          </div>
          <div>
            <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--on-surface-variant)', marginBottom: 4 }}>Fecha de envío</div>
            <div style={{ fontSize: 14, color: 'var(--on-surface)', fontFamily: 'var(--font-mono)' }}>
              {new Date(data.fecha_envio).toLocaleDateString('es-AR', {
                day: 'numeric', month: 'long', year: 'numeric',
                hour: '2-digit', minute: '2-digit',
              })}
            </div>
          </div>
          <div>
            <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--on-surface-variant)', marginBottom: 4 }}>Estado</div>
            <Badge tone={estadoTone[data.estado_entrega] ?? 'neutral'}>{data.estado_entrega}</Badge>
          </div>
        </div>

        <p style={{ margin: 0, fontSize: 15, color: 'var(--on-surface-variant)', lineHeight: '1.7', whiteSpace: 'pre-line' }}>
          {data.cuerpo}
        </p>
      </div>

      <Button variant="secondary" icon="arrow_back" onClick={() => navigate('/alumno/comunicaciones')}>
        Volver a comunicaciones
      </Button>
    </div>
  );
}
