import { useQuery } from '@tanstack/react-query';
import { useParams, Link } from 'react-router-dom';
import { Spinner } from '@/shared/components/Spinner';
import { EmptyState } from '../components/EmptyState';
import { ErrorState } from '../components/ErrorState';
import * as alumnoService from '../services/alumno.service';

const estadoStyles: Record<string, string> = {
  aprobado: 'bg-tertiary/10 text-tertiary',
  desaprobado: 'bg-error/10 text-error',
  ausente: 'bg-surface-container-high text-on-surface-variant',
  pendiente: 'bg-surface-container-high text-on-surface-variant',
};

const estadoLabels: Record<string, string> = {
  aprobado: 'Aprobado',
  desaprobado: 'Desaprobado',
  ausente: 'Ausente',
  pendiente: 'Pendiente',
};

const condicionStyles: Record<string, string> = {
  regular: 'bg-tertiary/10 text-tertiary border-tertiary/30',
  libre: 'bg-error/10 text-error border-error/30',
  promovido: 'bg-primary/10 text-primary border-primary/30',
};

export function MateriaDetallePage() {
  const { id } = useParams<{ id: string }>();
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['alumno', 'materia', id],
    queryFn: () => alumnoService.getMateriaDetalle(id!),
    enabled: !!id,
  });

  if (isLoading) return <div className="flex justify-center py-12"><Spinner size="lg" /></div>;
  if (error) return <ErrorState message="Error al cargar materia" onRetry={() => refetch()} />;
  if (!data) return <EmptyState message="Materia no encontrada" icon="search_off" />;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 text-label-sm text-on-surface-variant mb-2">
        <Link to="/alumno/materias" className="hover:text-primary transition-colors">Mis Materias</Link>
        <span className="material-symbols-outlined text-[16px]">chevron_right</span>
        <span className="text-on-surface">{data.nombre}</span>
      </div>

      <div className="flex items-start justify-between">
        <div>
          <h2 className="font-headline-lg text-headline-lg text-on-surface">{data.nombre}</h2>
          <p className="text-body-md text-on-surface-variant mt-1">{data.profesor}</p>
        </div>
        <span className={`inline-flex items-center rounded-full border px-3 py-1 text-label-sm font-medium ${condicionStyles[data.condicion]}`}>
          {data.condicion.charAt(0).toUpperCase() + data.condicion.slice(1)}
        </span>
      </div>

      {data.promedio !== null && (
        <div className="bg-surface-container-lowest rounded-xl border border-outline-variant p-4 inline-block">
          <p className="text-label-sm text-on-surface-variant">Promedio general</p>
          <p className="font-headline-lg text-headline-lg text-primary">{data.promedio.toFixed(2)}</p>
        </div>
      )}

      <div>
        <h3 className="text-label-md font-medium text-on-surface mb-3">Actividades</h3>
        {data.actividades.length === 0 ? (
          <EmptyState message="No hay actividades registradas" icon="assignment" />
        ) : (
          <div className="overflow-x-auto rounded-xl border border-outline-variant">
            <table className="w-full text-left">
              <thead>
                <tr className="bg-surface-container">
                  <th className="px-4 py-3 text-label-xs font-medium text-on-surface-variant uppercase">Actividad</th>
                  <th className="px-4 py-3 text-label-xs font-medium text-on-surface-variant uppercase">Nota</th>
                  <th className="px-4 py-3 text-label-xs font-medium text-on-surface-variant uppercase">Estado</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant">
                {data.actividades.map((act) => (
                  <tr key={act.id} className="bg-surface-container-lowest transition-colors hover:bg-surface-container-low">
                    <td className="px-4 py-3 text-label-sm text-on-surface">{act.nombre}</td>
                    <td className="px-4 py-3 text-label-sm text-on-surface-variant">
                      {act.nota !== null ? act.nota.toFixed(2) : '-'}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex rounded-full px-2.5 py-0.5 text-label-xs font-medium ${estadoStyles[act.estado]}`}>
                        {estadoLabels[act.estado]}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
