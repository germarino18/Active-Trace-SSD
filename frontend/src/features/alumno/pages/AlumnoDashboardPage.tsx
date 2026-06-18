import { useAlumnoDashboard } from '../hooks/useAlumnoDashboard';
import { Spinner } from '@/shared/components/Spinner';
import { EmptyState } from '../components/EmptyState';
import { ErrorState } from '../components/ErrorState';
import { MateriaCard } from '../components/MateriaCard';
import { AlertasPanel } from '../components/AlertasPanel';

export function AlumnoDashboardPage() {
  const { data, isLoading, error, refetch } = useAlumnoDashboard();

  if (isLoading) {
    return <div className="flex justify-center py-12"><Spinner size="lg" /></div>;
  }

  if (error) {
    return <ErrorState message="Error al cargar el dashboard" onRetry={() => refetch()} />;
  }

  if (!data || data.materias.length === 0) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="font-headline-lg text-headline-lg text-on-surface">Dashboard</h2>
          <p className="text-body-md text-on-surface-variant mt-1">Resumen de tu actividad académica</p>
        </div>
        <EmptyState message="No estás inscripto en ninguna materia en este período" icon="school" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-headline-lg text-headline-lg text-on-surface">Dashboard</h2>
        <p className="text-body-md text-on-surface-variant mt-1">
          Tenés {data.materias.length} materia{data.materias.length !== 1 ? 's' : ''} — {data.materias.filter(m => m.estado === 'al_dia').length} al día
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <h3 className="text-label-md font-medium text-on-surface">Tus materias</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {data.materias.map((m) => (
              <MateriaCard key={m.id} materia={m} />
            ))}
          </div>
        </div>

        <div className="lg:col-span-1">
          <AlertasPanel dashboard={data} />
        </div>
      </div>
    </div>
  );
}
