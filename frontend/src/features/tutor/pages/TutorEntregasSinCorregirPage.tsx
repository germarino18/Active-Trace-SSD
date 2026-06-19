import { useTutorEntregas } from '../hooks/useTutorEntregas';
import { TablaEntregasPendientes } from '@/features/academico/components/TablaEntregasPendientes';
import { EmptyState, Button } from '@/shared/components/ds';

export function TutorEntregasSinCorregirPage() {
  const { data, isLoading, isError, refetch } = useTutorEntregas();

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div>
        <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Entregas Sin Corregir</h2>
        <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>
          Actividades entregadas pendientes de corrección en tus materias.
        </p>
      </div>

      {isError ? (
        <EmptyState
          icon="error"
          title="Error al cargar entregas"
          action={<Button variant="secondary" icon="refresh" onClick={() => refetch()}>Reintentar</Button>}
        />
      ) : (
        <TablaEntregasPendientes
          data={data?.entregas}
          isLoading={isLoading}
        />
      )}
    </div>
  );
}
