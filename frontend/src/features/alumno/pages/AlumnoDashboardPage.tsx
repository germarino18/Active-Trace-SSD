import { useAlumnoDashboard } from '../hooks/useAlumnoDashboard';
import { Spinner } from '@/shared/components/Spinner';
import { EmptyState, StatCard, Button } from '@/shared/components/ds';
import { MateriaCard } from '../components/MateriaCard';
import { AlertasPanel } from '../components/AlertasPanel';

export function AlumnoDashboardPage() {
  const { data, isLoading, error, refetch } = useAlumnoDashboard();

  if (isLoading) {
    return <div className="flex justify-center py-12"><Spinner size="lg" /></div>;
  }

  if (error) {
    return (
      <EmptyState
        icon="error"
        title="Error al cargar el dashboard"
        message="No se pudo conectar con el servidor. Verificá tu conexión."
        action={<Button variant="secondary" icon="refresh" onClick={() => refetch()}>Reintentar</Button>}
      />
    );
  }

  if (!data || data.materias.length === 0) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 24, maxWidth: 1400, margin: '0 auto', width: '100%' }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Dashboard</h2>
          <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>Resumen de tu actividad académica</p>
        </div>
        <EmptyState
          icon="school"
          title="Sin materias"
          message="No estás inscripto en ninguna materia en este período"
        />
      </div>
    );
  }

  const alDia = data.materias.filter((m) => m.estado === 'al_dia').length;
  const atrasados = data.materias.filter((m) => m.estado === 'atrasado').length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24, maxWidth: 1400, margin: '0 auto', width: '100%' }}>
      <div>
        <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Dashboard</h2>
        <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>
          Tenés {data.materias.length} materia{data.materias.length !== 1 ? 's' : ''} — {alDia} al día
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 16 }}>
        <StatCard label="Materias activas" value={data.materias.length} icon="menu_book" />
        <StatCard label="Al día" value={alDia} icon="check_circle" tone={alDia > 0 ? 'primary' : 'default'} />
        {atrasados > 0 && (
          <StatCard label="Atrasadas" value={atrasados} icon="warning" trend="Requieren atención" trendDir="down" />
        )}
        {data.avisos_no_leidos > 0 && (
          <StatCard label="Avisos no leídos" value={data.avisos_no_leidos} icon="campaign" />
        )}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: 24, alignItems: 'start' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div style={{ fontSize: 13, fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--on-surface-variant)' }}>
            Tus materias
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 16 }}>
            {data.materias.map((m) => (
              <MateriaCard key={m.id} materia={m} />
            ))}
          </div>
        </div>

        <AlertasPanel dashboard={data} />
      </div>
    </div>
  );
}
