import { useState, useCallback, useRef } from 'react';
import { useDashboard, useAtrasadosPorCohorte, useDistribucionNotas, usePrediccionAbandono } from '../hooks/useAnalytics';
import { AnalyticsFilters } from '../components/AnalyticsFilters';
import type { AnalyticsFiltersValues } from '../components/AnalyticsFilters';
import { TendenciasAtrasadosChart } from '../components/TendenciasAtrasadosChart';
import { DistribucionNotasChart } from '../components/DistribucionNotasChart';
import { PrediccionAbandonoTable } from '../components/PrediccionAbandonoTable';
import { ExportButtons } from '../components/ExportButtons';
import { HelpButton } from '@/features/coordinacion/components/HelpButton';

const DEFAULT_FILTERS: AnalyticsFiltersValues = {
  fecha_desde: '',
  fecha_hasta: '',
  carrera_id: '',
  cohorte_id: '',
  materia_id: '',
  riesgo: '',
};

function KpiCard({ icon, label, value, isLoading }: { icon: string; label: string; value: string | number; isLoading?: boolean }) {
  return (
    <div className="rounded-xl border border-outline-variant bg-surface p-4 transition-colors hover:bg-surface-container-low">
      <div className="flex items-center gap-3">
        <span className="material-symbols-outlined text-[28px] text-primary">{icon}</span>
        <div>
          <p className="text-label-sm text-on-surface-variant">{label}</p>
          {isLoading ? (
            <div className="mt-1 h-7 w-16 animate-pulse rounded bg-surface-container-low" />
          ) : (
            <p className="font-headline-lg text-headline-lg text-on-surface">{value}</p>
          )}
        </div>
      </div>
    </div>
  );
}

export function AnalyticsDashboardPage() {
  const dashboardRef = useRef<HTMLDivElement>(null);
  const [filters, setFilters] = useState<AnalyticsFiltersValues>(DEFAULT_FILTERS);

  const { data: dashboard, isLoading: isLoadingDashboard } = useDashboard();
  const { data: atrasadosData, isLoading: isLoadingAtrasados } = useAtrasadosPorCohorte({
    fecha_desde: filters.fecha_desde || undefined,
    fecha_hasta: filters.fecha_hasta || undefined,
    carrera_id: filters.carrera_id || undefined,
    cohorte_id: filters.cohorte_id || undefined,
  });
  const { data: notasData, isLoading: isLoadingNotas } = useDistribucionNotas({
    materia_id: filters.materia_id || undefined,
    cohorte_id: filters.cohorte_id || undefined,
  });
  const { data: prediccionData, isLoading: isLoadingPrediccion } = usePrediccionAbandono({
    cohorte_id: filters.cohorte_id || undefined,
    materia_id: filters.materia_id || undefined,
    riesgo: filters.riesgo as 'bajo' | 'medio' | 'alto' | undefined,
  });

  const handleFilterChange = useCallback((key: string, value: unknown) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  }, []);

  const handleClearFilters = useCallback(() => {
    setFilters(DEFAULT_FILTERS);
  }, []);

  const hasNoData = !dashboard;

  return (
    <div ref={dashboardRef} className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-headline-lg text-headline-lg text-on-surface">Analytics</h2>
          <p className="text-body-md text-on-surface-variant mt-1">
            Panel de análisis académico y predicción de abandono
          </p>
        </div>
        <div className="flex items-center gap-2">
          <ExportButtons
            dashboardRef={dashboardRef}
            prediccionData={prediccionData}
            disabled={hasNoData}
          />
          <HelpButton tooltip="Panel de analytics con KPIs, tendencias de atrasados, distribución de notas y predicción de abandono." />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard icon="school" label="Total Alumnos" value={dashboard?.total_alumnos ?? 0} isLoading={isLoadingDashboard} />
        <KpiCard icon="warning" label="Atrasados Actual" value={dashboard?.total_atrasados_actual ?? 0} isLoading={isLoadingDashboard} />
        <KpiCard icon="trending_up" label="Promedio General" value={dashboard ? `${dashboard.promedio_general.toFixed(1)}%` : 0} isLoading={isLoadingDashboard} />
        <KpiCard icon="monitoring" label="Materias Activas" value={dashboard?.total_materias ?? 0} isLoading={isLoadingDashboard} />
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <KpiCard icon="check_circle" label="Riesgo Bajo" value={dashboard?.alumnos_en_riesgo.bajo ?? 0} isLoading={isLoadingDashboard} />
        <KpiCard icon="warning" label="Riesgo Medio" value={dashboard?.alumnos_en_riesgo.medio ?? 0} isLoading={isLoadingDashboard} />
        <KpiCard icon="error" label="Riesgo Alto" value={dashboard?.alumnos_en_riesgo.alto ?? 0} isLoading={isLoadingDashboard} />
      </div>

      <AnalyticsFilters
        values={filters}
        onChange={handleFilterChange}
        onClear={handleClearFilters}
      />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <TendenciasAtrasadosChart data={atrasadosData} isLoading={isLoadingAtrasados} />
        <DistribucionNotasChart data={notasData} isLoading={isLoadingNotas} />
      </div>

      <PrediccionAbandonoTable data={prediccionData} isLoading={isLoadingPrediccion} />
    </div>
  );
}
