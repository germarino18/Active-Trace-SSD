import { useQuery } from '@tanstack/react-query';
import { useParams, Link } from 'react-router-dom';
import { Spinner } from '@/shared/components/Spinner';
import { EmptyState } from '../components/EmptyState';
import { ErrorState } from '../components/ErrorState';
import * as alumnoService from '../services/alumno.service';

export function ComunicacionDetallePage() {
  const { id } = useParams<{ id: string }>();
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['alumno', 'comunicaciones', id],
    queryFn: () => alumnoService.getComunicacionDetalle(id!),
    enabled: !!id,
  });

  if (isLoading) return <div className="flex justify-center py-12"><Spinner size="lg" /></div>;
  if (error) return <ErrorState message="Error al cargar comunicación" onRetry={() => refetch()} />;
  if (!data) return <EmptyState message="Comunicación no encontrada" icon="search_off" />;

  return (
    <div className="max-w-3xl space-y-6">
      <div className="flex items-center gap-2 text-label-sm text-on-surface-variant mb-2">
        <Link to="/alumno/comunicaciones" className="hover:text-primary transition-colors">Comunicaciones</Link>
        <span className="material-symbols-outlined text-[16px]">chevron_right</span>
        <span className="text-on-surface truncate">{data.asunto}</span>
      </div>

      <div className="bg-surface-container-lowest rounded-xl border border-outline-variant p-6">
        <h2 className="font-headline-lg text-headline-lg text-on-surface mb-4">{data.asunto}</h2>

        <div className="grid grid-cols-2 gap-4 mb-6 pb-6 border-b border-outline-variant">
          <div>
            <p className="text-label-xs text-on-surface-variant">Remitente</p>
            <p className="text-label-sm text-on-surface">{data.remitente}</p>
          </div>
          <div>
            <p className="text-label-xs text-on-surface-variant">Materia</p>
            <p className="text-label-sm text-on-surface">{data.materia_nombre}</p>
          </div>
          <div>
            <p className="text-label-xs text-on-surface-variant">Fecha de envío</p>
            <p className="text-label-sm text-on-surface">
              {new Date(data.fecha_envio).toLocaleDateString('es-AR', {
                day: 'numeric', month: 'long', year: 'numeric',
                hour: '2-digit', minute: '2-digit',
              })}
            </p>
          </div>
          <div>
            <p className="text-label-xs text-on-surface-variant">Estado</p>
            <span className="inline-flex rounded-full bg-tertiary/10 px-2.5 py-0.5 text-label-xs font-medium text-tertiary">
              {data.estado_entrega}
            </span>
          </div>
        </div>

        <div className="prose prose-sm max-w-none">
          <p className="text-body-md text-on-surface-variant whitespace-pre-line leading-relaxed">
            {data.cuerpo}
          </p>
        </div>
      </div>

      <Link
        to="/alumno/comunicaciones"
        className="inline-flex items-center gap-1.5 rounded-lg border border-outline-variant px-4 py-2 text-label-sm font-medium text-on-surface transition-colors hover:bg-surface-container-low"
      >
        <span className="material-symbols-outlined text-[18px]">arrow_back</span>
        Volver a comunicaciones
      </Link>
    </div>
  );
}
