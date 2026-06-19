import { useState, useCallback } from 'react';
import { useMetricasDashboard, useAccionesPorDia, useEstadosComunicacion, useInteracciones } from '../hooks/useMetricas';
import { MetricFilters } from '../components/MetricFilters';
import { AccionesPorDiaChart } from '../components/AccionesPorDiaChart';
import { EstadosComunicacionChart } from '../components/EstadosComunicacionChart';
import { InteraccionesDocenteTable } from '../components/InteraccionesDocenteTable';
import { HelpButton } from '@/features/coordinacion/components/HelpButton';

interface MetricFiltersState {
  fecha_desde: string;
  fecha_hasta: string;
  materia_id: string;
  usuario_id: string;
}

const DEFAULT_FILTERS: MetricFiltersState = {
  fecha_desde: '',
  fecha_hasta: '',
  materia_id: '',
  usuario_id: '',
};

function KpiCard({ icon, label, value, isLoading }: { icon: string; label: string; value: string | number; isLoading?: boolean }) {
  return (
    <div style={{ borderRadius: 'var(--radius-lg)', border: '1px solid var(--outline-variant)', background: 'var(--surface-container)', padding: 16, transition: 'background .15s ease' }}
      onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--surface-container-low)')}
      onMouseLeave={(e) => (e.currentTarget.style.background = 'var(--surface-container)')}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <span className="material-symbols-outlined" style={{ fontSize: 28, color: 'var(--primary)' }}>{icon}</span>
        <div>
          <p style={{ margin: 0, fontSize: 12, color: 'var(--on-surface-variant)', fontWeight: 500 }}>{label}</p>
          {isLoading ? (
            <div className="animate-pulse" style={{ marginTop: 4, height: 28, width: 64, borderRadius: 6, background: 'var(--surface-container-high)' }} />
          ) : (
            <p style={{ margin: '2px 0 0', fontSize: 28, fontWeight: 700, color: 'var(--on-surface)', lineHeight: 1 }}>{value}</p>
          )}
        </div>
      </div>
    </div>
  );
}

export function MetricasPage() {
  const [filters, setFilters] = useState<MetricFiltersState>(DEFAULT_FILTERS);

  const { data: dashboard, isLoading: isLoadingDashboard } = useMetricasDashboard();
  const { data: accionesPorDia, isLoading: isLoadingAcciones } = useAccionesPorDia({
    fecha_desde: filters.fecha_desde || undefined,
    fecha_hasta: filters.fecha_hasta || undefined,
  });
  const { data: estadosComunicacion, isLoading: isLoadingEstados } = useEstadosComunicacion({
    materia_id: filters.materia_id || undefined,
  });
  const { data: interacciones, isLoading: isLoadingInteracciones } = useInteracciones({
    materia_id: filters.materia_id || undefined,
    usuario_id: filters.usuario_id || undefined,
  });

  const handleFilterChange = useCallback((key: string, value: unknown) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  }, []);

  const handleClearFilters = useCallback(() => {
    setFilters(DEFAULT_FILTERS);
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <div>
          <h2 className="font-headline-lg text-headline-lg text-on-surface">Métricas</h2>
          <p className="text-body-md text-on-surface-variant mt-1">
            Panel de indicadores y estadísticas del sistema
          </p>
        </div>
        <HelpButton tooltip="Panel de métricas con KPIs, acciones por día, estado de comunicaciones e interacciones por docente y materia." />
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          icon="school"
          label="Docentes activos"
          value={dashboard?.total_docentes_activos ?? 0}
          isLoading={isLoadingDashboard}
        />
        <KpiCard
          icon="mail"
          label="Comunicaciones totales"
          value={dashboard?.total_comunicaciones ?? 0}
          isLoading={isLoadingDashboard}
        />
        <KpiCard
          icon="check_circle"
          label="Comunicaciones OK"
          value={dashboard?.comunicaciones_ok ?? 0}
          isLoading={isLoadingDashboard}
        />
        <KpiCard
          icon="error"
          label="Comunicaciones fallidas"
          value={dashboard?.comunicaciones_fallidas ?? 0}
          isLoading={isLoadingDashboard}
        />
      </div>

      <MetricFilters
        values={filters}
        onChange={handleFilterChange}
        onClear={handleClearFilters}
      />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <AccionesPorDiaChart
          data={accionesPorDia}
          isLoading={isLoadingAcciones}
        />
        <EstadosComunicacionChart
          data={estadosComunicacion}
          isLoading={isLoadingEstados}
        />
      </div>

      <InteraccionesDocenteTable
        data={interacciones}
        isLoading={isLoadingInteracciones}
      />
    </div>
  );
}
