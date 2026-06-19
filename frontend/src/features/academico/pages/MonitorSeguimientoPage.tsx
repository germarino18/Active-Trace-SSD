import { useParams } from 'react-router-dom';
import { FiltrosMonitor } from '../components/FiltrosMonitor';
import { TablaMonitor } from '../components/TablaMonitor';
import { useMonitor } from '../hooks/useMonitor';
import { StatCard } from '@/shared/components/ds';

export function MonitorSeguimientoPage() {
  const { id: materiaId } = useParams<{ id: string }>();
  const { filters, updateFilter, applyFilters, clearFilters, query } = useMonitor(materiaId!);

  const alumnos = query.data?.alumnos ?? [];
  const total = alumnos.length;
  const enRiesgo = alumnos.filter((a) => a.estado === 'atrasado').length;
  const promedio = total > 0
    ? Math.round(alumnos.reduce((sum, a) => sum + a.porcentaje_completitud, 0) / total)
    : 0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      <div>
        <h2 style={{ margin: 0, fontSize: 28, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Monitor de Seguimiento</h2>
        <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>
          Visualizá el estado de actividades de los alumnos.
        </p>
      </div>

      {total > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 16 }}>
          <StatCard label="Total alumnos" value={total} icon="people" />
          <StatCard label="Progreso promedio" value={`${promedio}%`} icon="trending_up" progress={promedio} tone="primary" />
          <StatCard label="En riesgo" value={enRiesgo} icon="warning" trend={enRiesgo > 0 ? 'Requieren atención' : 'Sin alumnos en riesgo'} trendDir={enRiesgo > 0 ? 'down' : 'up'} />
          <StatCard label="Al día" value={total - enRiesgo} icon="check_circle" />
        </div>
      )}

      <FiltrosMonitor
        filters={filters}
        onFilterChange={updateFilter}
        onApply={applyFilters}
        onClear={clearFilters}
      />

      <TablaMonitor
        data={query.data?.alumnos}
        isLoading={query.isLoading}
      />

      {query.isError && (
        <p style={{ fontSize: 13, color: 'var(--error)' }}>
          {query.error?.message || 'Error al cargar los datos del monitor'}
        </p>
      )}
    </div>
  );
}
