import { useQuery } from '@tanstack/react-query';
import { Spinner } from '@/shared/components/Spinner';
import { EmptyState } from '../components/EmptyState';
import { ErrorState } from '../components/ErrorState';
import * as alumnoService from '../services/alumno.service';

export function MisProgramasPage() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['alumno', 'programas'],
    queryFn: () => alumnoService.getProgramas(),
  });

  if (isLoading) return <div className="flex justify-center py-12"><Spinner size="lg" /></div>;
  if (error) return <ErrorState message="Error al cargar programas" onRetry={() => refetch()} />;
  if (!data || data.length === 0) return <EmptyState message="No hay programas disponibles" icon="description" />;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-headline-lg text-headline-lg text-on-surface">Programas</h2>
        <p className="text-body-md text-on-surface-variant mt-1">Programas de estudio por materia</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {data.map((programa) => (
          <div
            key={programa.id}
            className="bg-surface-container-lowest rounded-xl border border-outline-variant p-4"
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1 min-w-0">
                <h3 className="text-label-md font-medium text-on-surface truncate">{programa.materia_nombre}</h3>
                <p className="text-label-sm text-on-surface-variant mt-0.5 truncate">{programa.programa_nombre}</p>
              </div>
              <span className="material-symbols-outlined text-outline text-[20px] shrink-0">description</span>
            </div>

            <p className="text-label-xs text-on-surface-variant mb-3">
              Publicado: {new Date(programa.fecha_publicacion).toLocaleDateString('es-AR')}
            </p>

            {programa.referencia_archivo ? (
              <a
                href={programa.referencia_archivo}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 rounded-lg bg-primary px-3 py-2 text-label-xs font-medium text-on-primary transition-colors hover:bg-primary/90"
              >
                <span className="material-symbols-outlined text-[16px]">download</span>
                Descargar
              </a>
            ) : (
              <span className="text-label-xs text-outline">Sin archivo disponible</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
