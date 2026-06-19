import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useParams, Link } from 'react-router-dom';
import { Spinner } from '@/shared/components/Spinner';
import { EmptyState, Badge, Tabs, StatCard, Button } from '@/shared/components/ds';
import * as alumnoService from '../services/alumno.service';

const estadoTone: Record<string, 'success' | 'danger' | 'neutral'> = {
  aprobado: 'success',
  desaprobado: 'danger',
  ausente: 'neutral',
  pendiente: 'neutral',
};

const estadoLabels: Record<string, string> = {
  aprobado: 'Aprobado',
  desaprobado: 'Desaprobado',
  ausente: 'Ausente',
  pendiente: 'Pendiente',
};

const condicionTone: Record<string, 'success' | 'danger' | 'primary'> = {
  regular: 'success',
  libre: 'danger',
  promovido: 'primary',
};

const TABS = [
  { id: 'actividades', label: 'Actividades', icon: 'assignment' },
  { id: 'calificaciones', label: 'Calificaciones', icon: 'grade' },
  { id: 'material', label: 'Material', icon: 'description' },
];

export function MateriaDetallePage() {
  const { id } = useParams<{ id: string }>();
  const [tab, setTab] = useState('actividades');

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['alumno', 'materia', id],
    queryFn: () => alumnoService.getMateriaDetalle(id!),
    enabled: !!id,
  });

  if (isLoading) return <div className="flex justify-center py-12"><Spinner size="lg" /></div>;

  if (error) {
    return (
      <EmptyState
        icon="error"
        title="Error al cargar materia"
        action={<Button variant="secondary" icon="refresh" onClick={() => refetch()}>Reintentar</Button>}
      />
    );
  }

  if (!data) {
    return <EmptyState icon="search_off" title="Materia no encontrada" />;
  }

  const aprobadas = data.actividades.filter((a) => a.estado === 'aprobado').length;
  const progreso = data.actividades.length > 0
    ? Math.round((aprobadas / data.actividades.length) * 100)
    : 0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, color: 'var(--on-surface-variant)' }}>
        <Link to="/alumno/materias" style={{ color: 'var(--on-surface-variant)', textDecoration: 'none' }}
          onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--primary)')}
          onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--on-surface-variant)')}
        >Mis Materias</Link>
        <span className="material-symbols-outlined" style={{ fontSize: 16 }}>chevron_right</span>
        <span style={{ color: 'var(--on-surface)' }}>{data.nombre}</span>
      </div>

      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 16, flexWrap: 'wrap' }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 28, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>{data.nombre}</h2>
          <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>{data.profesor}</p>
        </div>
        <Badge tone={condicionTone[data.condicion]}>
          {data.condicion.charAt(0).toUpperCase() + data.condicion.slice(1)}
        </Badge>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 16 }}>
        {data.promedio !== null && (
          <StatCard label="Promedio general" value={data.promedio.toFixed(2)} icon="grade" tone="primary" />
        )}
        <StatCard label="Completitud" value={`${progreso}%`} icon="task_alt" progress={progreso} />
        <StatCard label="Actividades" value={`${aprobadas}/${data.actividades.length}`} icon="assignment_turned_in" />
      </div>

      <Tabs tabs={TABS} value={tab} onChange={setTab} />

      {tab === 'actividades' && (
        data.actividades.length === 0 ? (
          <EmptyState icon="assignment" title="No hay actividades registradas" />
        ) : (
          <div style={{ overflowX: 'auto', borderRadius: 'var(--radius-lg)', border: '1px solid var(--outline-variant)' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
              <thead>
                <tr style={{ background: 'var(--surface-container)' }}>
                  <th style={{ padding: '12px 16px', fontSize: 11, fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--on-surface-variant)' }}>Actividad</th>
                  <th style={{ padding: '12px 16px', fontSize: 11, fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--on-surface-variant)' }}>Nota</th>
                  <th style={{ padding: '12px 16px', fontSize: 11, fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--on-surface-variant)' }}>Estado</th>
                </tr>
              </thead>
              <tbody>
                {data.actividades.map((act, i) => (
                  <tr key={act.id} style={{ borderTop: i > 0 ? '1px solid var(--outline-variant)' : undefined, background: 'var(--surface-container-lowest)' }}>
                    <td style={{ padding: '12px 16px', fontSize: 14, color: 'var(--on-surface)' }}>{act.nombre}</td>
                    <td style={{ padding: '12px 16px', fontSize: 14, color: 'var(--on-surface-variant)', fontFamily: 'var(--font-mono)' }}>
                      {act.nota !== null ? act.nota.toFixed(2) : '—'}
                    </td>
                    <td style={{ padding: '12px 16px' }}>
                      <Badge tone={estadoTone[act.estado]}>{estadoLabels[act.estado]}</Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      )}

      {tab === 'calificaciones' && (
        data.actividades.filter((a) => a.nota !== null).length === 0 ? (
          <EmptyState icon="grade" title="Sin calificaciones" message="No hay notas registradas aún." />
        ) : (
          <div style={{ overflowX: 'auto', borderRadius: 'var(--radius-lg)', border: '1px solid var(--outline-variant)' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
              <thead>
                <tr style={{ background: 'var(--surface-container)' }}>
                  <th style={{ padding: '12px 16px', fontSize: 11, fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--on-surface-variant)' }}>Actividad</th>
                  <th style={{ padding: '12px 16px', fontSize: 11, fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--on-surface-variant)' }}>Nota</th>
                  <th style={{ padding: '12px 16px', fontSize: 11, fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--on-surface-variant)' }}>Estado</th>
                </tr>
              </thead>
              <tbody>
                {data.actividades.filter((a) => a.nota !== null).map((act, i) => (
                  <tr key={act.id} style={{ borderTop: i > 0 ? '1px solid var(--outline-variant)' : undefined, background: 'var(--surface-container-lowest)' }}>
                    <td style={{ padding: '12px 16px', fontSize: 14, color: 'var(--on-surface)' }}>{act.nombre}</td>
                    <td style={{ padding: '12px 16px', fontSize: 22, fontWeight: 700, color: act.estado === 'aprobado' ? 'var(--tertiary)' : 'var(--error)', fontFamily: 'var(--font-mono)' }}>
                      {act.nota!.toFixed(2)}
                    </td>
                    <td style={{ padding: '12px 16px' }}>
                      <Badge tone={estadoTone[act.estado]}>{estadoLabels[act.estado]}</Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      )}

      {tab === 'material' && (
        <EmptyState
          icon="description"
          title="Material de estudio"
          message="El material de estudio estará disponible cuando el docente lo publique."
        />
      )}
    </div>
  );
}
