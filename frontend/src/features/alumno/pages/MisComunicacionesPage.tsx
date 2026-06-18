import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Spinner } from '@/shared/components/Spinner';
import { EmptyState } from '../components/EmptyState';
import { ErrorState } from '../components/ErrorState';
import * as alumnoService from '../services/alumno.service';

const estadoBadge: Record<string, string> = {
  Enviado: 'bg-primary/10 text-primary',
  Entregado: 'bg-tertiary/10 text-tertiary',
  Leido: 'bg-surface-container-high text-on-surface-variant',
  Error: 'bg-error/10 text-error',
};

export function MisComunicacionesPage() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['alumno', 'comunicaciones'],
    queryFn: () => alumnoService.getComunicaciones(),
  });

  if (isLoading) return <div className="flex justify-center py-12"><Spinner size="lg" /></div>;
  if (error) return <ErrorState message="Error al cargar comunicaciones" onRetry={() => refetch()} />;
  if (!data || data.length === 0) return <EmptyState message="No tenés comunicaciones recibidas" icon="forward_to_inbox" />;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-headline-lg text-headline-lg text-on-surface">Comunicaciones</h2>
        <p className="text-body-md text-on-surface-variant mt-1">Historial de comunicaciones recibidas</p>
      </div>

      <div className="overflow-x-auto rounded-xl border border-outline-variant">
        <table className="w-full text-left">
          <thead>
            <tr className="bg-surface-container">
              <th className="px-4 py-3 text-label-xs font-medium text-on-surface-variant uppercase">Remitente</th>
              <th className="px-4 py-3 text-label-xs font-medium text-on-surface-variant uppercase">Materia</th>
              <th className="px-4 py-3 text-label-xs font-medium text-on-surface-variant uppercase">Asunto</th>
              <th className="px-4 py-3 text-label-xs font-medium text-on-surface-variant uppercase">Fecha</th>
              <th className="px-4 py-3 text-label-xs font-medium text-on-surface-variant uppercase">Estado</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-outline-variant">
            {data.map((com) => (
              <tr
                key={com.id}
                className="bg-surface-container-lowest transition-colors hover:bg-surface-container-low"
              >
                <td className="px-4 py-3">
                  <Link
                    to={`/alumno/comunicaciones/${com.id}`}
                    className="text-label-sm text-primary hover:underline font-medium"
                  >
                    {com.remitente}
                  </Link>
                </td>
                <td className="px-4 py-3 text-label-sm text-on-surface-variant">{com.materia_nombre}</td>
                <td className="px-4 py-3 text-label-sm text-on-surface">{com.asunto}</td>
                <td className="px-4 py-3 text-label-sm text-on-surface-variant">
                  {new Date(com.fecha_envio).toLocaleDateString('es-AR')}
                </td>
                <td className="px-4 py-3">
                  <span className={`inline-flex rounded-full px-2.5 py-0.5 text-label-xs font-medium ${estadoBadge[com.estado] ?? ''}`}>
                    {com.estado}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
