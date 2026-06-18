import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Spinner } from '@/shared/components/Spinner';
import { EmptyState } from '../components/EmptyState';
import { ErrorState } from '../components/ErrorState';
import * as alumnoService from '../services/alumno.service';

export function AlumnoInboxPage() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['alumno', 'inbox'],
    queryFn: () => alumnoService.getHilos(),
  });

  if (isLoading) return <div className="flex justify-center py-12"><Spinner size="lg" /></div>;
  if (error) return <ErrorState message="Error al cargar mensajes" onRetry={() => refetch()} />;
  if (!data || data.length === 0) return <EmptyState message="No tenés mensajes" icon="mail" />;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-headline-lg text-headline-lg text-on-surface">Mensajes</h2>
        <p className="text-body-md text-on-surface-variant mt-1">Bandeja de entrada</p>
      </div>

      <div className="rounded-xl border border-outline-variant divide-y divide-outline-variant">
        {data.map((hilo) => (
          <Link
            key={hilo.id}
            to={`/alumno/inbox/${hilo.id}`}
            className={`flex items-start gap-4 px-4 py-3 transition-colors hover:bg-surface-container-low ${
              !hilo.leido ? 'bg-primary/[0.02]' : ''
            }`}
          >
            <div className="relative shrink-0">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/20 text-primary text-label-sm font-bold">
                {hilo.remitente.charAt(0)}
              </div>
              {!hilo.leido && (
                <span className="absolute -top-0.5 -right-0.5 h-3 w-3 rounded-full border-2 border-background bg-primary" />
              )}
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className={`text-label-sm font-medium truncate ${!hilo.leido ? 'text-on-surface' : 'text-on-surface-variant'}`}>
                  {hilo.remitente}
                </span>
                <span className="text-label-xs text-outline shrink-0">
                  {new Date(hilo.fecha).toLocaleDateString('es-AR')}
                </span>
              </div>
              <p className={`text-label-sm truncate mt-0.5 ${!hilo.leido ? 'text-on-surface font-medium' : 'text-on-surface-variant'}`}>
                {hilo.asunto}
              </p>
              <p className="text-label-xs text-outline truncate mt-0.5">{hilo.ultimo_mensaje}</p>
            </div>

            <span className="material-symbols-outlined text-outline text-[18px] shrink-0 self-center">chevron_right</span>
          </Link>
        ))}
      </div>
    </div>
  );
}
