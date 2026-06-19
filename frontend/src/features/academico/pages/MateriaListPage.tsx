import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { Card, Badge, StatCard, EmptyState, Button } from '@/shared/components/ds';
import * as api from '@/shared/services/api';
import type { Materia } from '../types';

function useMisMaterias() {
  return useQuery<Materia[]>({
    queryKey: ['academico', 'mis-materias'],
    queryFn: () => api.get<Materia[]>('/api/v1/materias/mis-materias'),
  });
}

export function MateriaListPage() {
  const navigate = useNavigate();
  const { session } = useAuth();
  const { data, isLoading, error, refetch } = useMisMaterias();

  const userName = session.status === 'authenticated'
    ? `${session.user.nombre} ${session.user.apellido}`
    : '';

  if (isLoading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
        <PageHeader name={userName} count={null} />
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 20 }}>
          {[1, 2, 3].map((i) => (
            <div key={i} style={{ height: 140, borderRadius: 'var(--radius-lg)', background: 'var(--surface-container)', border: '1px solid var(--outline-variant)', animation: 'pulse 1.5s ease-in-out infinite' }} />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <EmptyState
        icon="error"
        title="Error al cargar materias"
        message="No se pudo conectar con el servidor."
        action={<Button variant="secondary" icon="refresh" onClick={() => refetch()}>Reintentar</Button>}
      />
    );
  }

  if (!data || data.length === 0) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
        <PageHeader name={userName} count={0} />
        <EmptyState
          icon="class"
          title="Sin materias asignadas"
          message="No tenés materias asignadas para el período activo."
        />
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <PageHeader name={userName} count={data.length} />

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 16 }}>
        <StatCard label="Materias activas" value={data.length} icon="class" tone="primary" />
        <StatCard label="Cuatrimestre" value={data[0]?.cuatrimestre ?? '—'} icon="calendar_today" />
        <StatCard label="Año" value={data[0]?.anio ?? '—'} icon="school" />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 20 }}>
        {data.map((materia) => (
          <Card
            key={materia.id}
            hover
            style={{ cursor: 'pointer' }}
            action={
              <Badge tone="neutral">{materia.comision}</Badge>
            }
            onClick={() => navigate(`/academico/materias/${materia.id}/importar`)}
          >
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: 14, marginBottom: 12 }}>
              <div style={{ width: 44, height: 44, borderRadius: 'var(--radius-md)', background: 'color-mix(in srgb, var(--primary) 16%, transparent)', color: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <span className="material-symbols-outlined" style={{ fontSize: 24 }}>menu_book</span>
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 16, fontWeight: 700, color: 'var(--on-surface)', marginBottom: 2, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {materia.nombre}
                </div>
                <div style={{ fontSize: 12, color: 'var(--on-surface-variant)', fontFamily: 'var(--font-mono)' }}>
                  {materia.codigo}
                </div>
              </div>
            </div>
            <div style={{ fontSize: 13, color: 'var(--on-surface-variant)' }}>
              {materia.carrera}
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

function PageHeader({ name, count }: { name: string; count: number | null }) {
  return (
    <div>
      <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Mis Materias</h2>
      <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>
        {count !== null
          ? `${count > 0 ? `${count} materia${count !== 1 ? 's' : ''} asignada${count !== 1 ? 's' : ''} — seleccioná una para gestionarla` : 'Seleccioná una materia para gestionar sus calificaciones y alumnos'}`
          : `Cargando materias${name ? ` de ${name}` : ''}…`}
      </p>
    </div>
  );
}
