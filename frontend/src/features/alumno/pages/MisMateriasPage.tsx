import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Spinner } from '@/shared/components/Spinner';
import { EmptyState } from '../components/EmptyState';
import { ErrorState } from '../components/ErrorState';
import * as alumnoService from '../services/alumno.service';

const condicionStyles: Record<string, string> = {
  regular: 'bg-tertiary/10 text-tertiary',
  libre: 'bg-error/10 text-error',
  promovido: 'bg-primary/10 text-primary',
};

const condicionLabels: Record<string, string> = {
  regular: 'Regular',
  libre: 'Libre',
  promovido: 'Promovido',
};

export function MisMateriasPage() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['alumno', 'materias'],
    queryFn: () => alumnoService.getMaterias(),
  });

  if (isLoading) return <div className="flex justify-center py-12"><Spinner size="lg" /></div>;
  if (error) return <ErrorState message="Error al cargar materias" onRetry={() => refetch()} />;
  if (!data || data.length === 0) return <EmptyState message="No estás inscripto en ninguna materia" icon="school" />;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-headline-lg text-headline-lg text-on-surface">Mis Materias</h2>
        <p className="text-body-md text-on-surface-variant mt-1">Estado académico de todas tus materias</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {data.map((materia) => {
          const progreso = materia.actividades.length > 0
            ? Math.round((materia.actividades.filter(a => a.estado === 'aprobado').length / materia.actividades.length) * 100)
            : 0;

          return (
            <Link
              key={materia.id}
              to={`/alumno/materias/${materia.id}`}
              className="block bg-surface-container-lowest rounded-xl border border-outline-variant p-4 transition-colors hover:border-primary/50 hover:bg-surface-container-low"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1 min-w-0">
                  <h3 className="text-label-md font-medium text-on-surface truncate">{materia.nombre}</h3>
                  <p className="text-label-sm text-on-surface-variant mt-0.5">{materia.profesor}</p>
                </div>
                <span className={`inline-flex shrink-0 items-center rounded-full px-2.5 py-0.5 text-label-xs font-medium ${condicionStyles[materia.condicion]}`}>
                  {condicionLabels[materia.condicion]}
                </span>
              </div>

              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-label-xs text-on-surface-variant">
                  <span>Progreso</span>
                  <span>{progreso}%</span>
                </div>
                <div className="h-2 w-full rounded-full bg-surface-container">
                  <div
                    className="h-full rounded-full bg-primary transition-all"
                    style={{ width: `${progreso}%` }}
                  />
                </div>
              </div>

              {materia.promedio !== null && (
                <p className="mt-3 text-label-sm text-on-surface-variant">
                  Promedio: <span className="text-on-surface font-medium">{materia.promedio.toFixed(2)}</span>
                </p>
              )}
            </Link>
          );
        })}
      </div>
    </div>
  );
}
