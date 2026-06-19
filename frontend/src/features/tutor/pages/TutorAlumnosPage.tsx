import { useNavigate } from 'react-router-dom';
import { useTutorAlumnos } from '../hooks/useTutorAlumnos';
import { Spinner } from '@/shared/components/Spinner';
import { EmptyState, Button, Badge } from '@/shared/components/ds';

export function TutorAlumnosPage() {
  const navigate = useNavigate();
  const { data, isLoading, isError, refetch } = useTutorAlumnos();

  if (isLoading) return <div className="flex justify-center py-12"><Spinner size="lg" /></div>;

  if (isError) {
    return (
      <EmptyState
        icon="error"
        title="Error al cargar alumnos"
        action={<Button variant="secondary" icon="refresh" onClick={() => refetch()}>Reintentar</Button>}
      />
    );
  }

  if (!data || data.length === 0) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
        <PageHeader />
        <EmptyState icon="group_off" title="No hay alumnos asignados" message="No tenés alumnos asignados a tus materias en este período." />
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <PageHeader />

      <div style={{ overflowX: 'auto', borderRadius: 'var(--radius-lg)', border: '1px solid var(--outline-variant)' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ background: 'var(--surface-container)', borderBottom: '1px solid var(--outline-variant)' }}>
              {['Nombre', 'Apellido', 'Email', 'Materia', 'Comisión', 'Estado', ''].map((h) => (
                <th key={h} style={{ padding: '12px 16px', fontSize: 11, fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--on-surface-variant)' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((alumno, i) => {
              const ext = alumno as typeof alumno & { en_riesgo?: boolean; materia_nombre?: string };
              return (
                <tr key={alumno.id}
                  style={{ borderTop: i > 0 ? '1px solid var(--outline-variant)' : undefined, background: 'var(--surface-container-lowest)', transition: 'background .12s ease' }}
                  onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--surface-container-low)')}
                  onMouseLeave={(e) => (e.currentTarget.style.background = 'var(--surface-container-lowest)')}
                >
                  <td style={{ padding: '12px 16px', fontSize: 14, color: 'var(--on-surface)', fontWeight: 500 }}>{alumno.nombre}</td>
                  <td style={{ padding: '12px 16px', fontSize: 14, color: 'var(--on-surface)' }}>{alumno.apellido}</td>
                  <td style={{ padding: '12px 16px', fontSize: 13, color: 'var(--on-surface-variant)' }}>{alumno.email}</td>
                  <td style={{ padding: '12px 16px', fontSize: 13, color: 'var(--on-surface-variant)' }}>{ext.materia_nombre}</td>
                  <td style={{ padding: '12px 16px', fontSize: 13, color: 'var(--on-surface-variant)', fontFamily: 'var(--font-mono)' }}>{alumno.comision}</td>
                  <td style={{ padding: '12px 16px' }}>
                    {ext.en_riesgo
                      ? <Badge tone="danger" dot>En riesgo</Badge>
                      : <Badge tone="success">Al día</Badge>}
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <Button size="sm" variant="ghost" icon="arrow_forward" onClick={() => navigate(`/materias/${alumno.id}`)}>
                      Ver detalle
                    </Button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function PageHeader() {
  return (
    <div>
      <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Mis Alumnos</h2>
      <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>Listado de alumnos asignados a tus materias.</p>
    </div>
  );
}
