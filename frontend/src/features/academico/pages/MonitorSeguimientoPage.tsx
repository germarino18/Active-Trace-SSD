import { useParams } from 'react-router-dom';
import { FiltrosMonitor } from '../components/FiltrosMonitor';
import { TablaMonitor } from '../components/TablaMonitor';
import { useMonitor } from '../hooks/useMonitor';

export function MonitorSeguimientoPage() {
  const { id: materiaId } = useParams<{ id: string }>();
  const { filters, updateFilter, applyFilters, clearFilters, query } = useMonitor(materiaId!);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-headline-lg text-headline-lg text-on-surface">Monitor de Seguimiento</h2>
        <p className="text-body-md text-on-surface-variant mt-1">
          Visualizá el estado de actividades de los alumnos.
        </p>
      </div>

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
        <p className="text-label-sm text-error">
          {query.error?.message || 'Error al cargar los datos del monitor'}
        </p>
      )}
    </div>
  );
}
