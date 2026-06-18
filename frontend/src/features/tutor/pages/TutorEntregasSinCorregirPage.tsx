import { useTutorEntregas } from '../hooks/useTutorEntregas';
import { TablaEntregasPendientes } from '@/features/academico/components/TablaEntregasPendientes';
import { ErrorState } from '../components/ErrorState';

export function TutorEntregasSinCorregirPage() {
  const { data, isLoading, isError, refetch } = useTutorEntregas();

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-headline-lg text-headline-lg text-on-surface">Entregas Sin Corregir</h2>
        <p className="text-body-md text-on-surface-variant mt-1">
          Actividades entregadas pendientes de corrección en tus materias.
        </p>
      </div>

      {isError ? (
        <ErrorState onRetry={() => refetch()} />
      ) : (
        <TablaEntregasPendientes
          data={data?.entregas}
          isLoading={isLoading}
        />
      )}
    </div>
  );
}
