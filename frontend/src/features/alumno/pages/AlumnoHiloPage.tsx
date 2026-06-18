import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useParams, Link } from 'react-router-dom';
import { Spinner } from '@/shared/components/Spinner';
import { EmptyState } from '../components/EmptyState';
import { ErrorState } from '../components/ErrorState';
import * as alumnoService from '../services/alumno.service';

export function AlumnoHiloPage() {
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const [contenido, setContenido] = useState('');

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['alumno', 'inbox', id],
    queryFn: () => alumnoService.getHilo(id!),
    enabled: !!id,
  });

  const responderMutation = useMutation({
    mutationFn: () => alumnoService.responderHilo(id!, contenido),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alumno', 'inbox', id] });
      setContenido('');
    },
  });

  if (isLoading) return <div className="flex justify-center py-12"><Spinner size="lg" /></div>;
  if (error) return <ErrorState message="Error al cargar mensajes" onRetry={() => refetch()} />;
  if (!data || data.length === 0) return <EmptyState message="No se encontró el hilo" icon="search_off" />;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (contenido.trim() && !responderMutation.isPending) {
      responderMutation.mutate();
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 text-label-sm text-on-surface-variant mb-2">
        <Link to="/alumno/inbox" className="hover:text-primary transition-colors">Mensajes</Link>
        <span className="material-symbols-outlined text-[16px]">chevron_right</span>
        <span className="text-on-surface truncate">{data[0]?.remitente ?? 'Hilo'}</span>
      </div>

      <h2 className="font-headline-lg text-headline-lg text-on-surface">{data[0]?.remitente}</h2>

      <div className="space-y-4">
        {data.map((msg) => (
          <div
            key={msg.id}
            className="bg-surface-container-lowest rounded-xl border border-outline-variant p-4"
          >
            <div className="flex items-center gap-2 mb-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/20 text-primary text-label-xs font-bold">
                {msg.remitente.charAt(0)}
              </div>
              <div>
                <p className="text-label-sm font-medium text-on-surface">{msg.remitente}</p>
                <p className="text-label-xs text-outline">
                  {new Date(msg.fecha).toLocaleDateString('es-AR', {
                    day: 'numeric', month: 'long', year: 'numeric',
                    hour: '2-digit', minute: '2-digit',
                  })}
                </p>
              </div>
            </div>
            <p className="text-body-md text-on-surface-variant whitespace-pre-line">{msg.contenido}</p>
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="space-y-3">
        <textarea
          value={contenido}
          onChange={(e) => setContenido(e.target.value)}
          placeholder="Escribí tu respuesta..."
          rows={4}
          className="w-full rounded-lg bg-surface-container border border-outline-variant px-4 py-3 text-body-md text-on-surface placeholder:text-outline focus:ring-2 focus:ring-primary focus:outline-none resize-none"
        />
        <div className="flex justify-end gap-2">
          <Link
            to="/alumno/inbox"
            className="rounded-lg border border-outline-variant px-4 py-2 text-label-sm font-medium text-on-surface transition-colors hover:bg-surface-container-low"
          >
            Volver
          </Link>
          <button
            type="submit"
            disabled={!contenido.trim() || responderMutation.isPending}
            className="rounded-lg bg-primary px-4 py-2 text-label-sm font-medium text-on-primary transition-colors hover:bg-primary/90 disabled:opacity-50"
          >
            {responderMutation.isPending ? 'Enviando...' : 'Enviar respuesta'}
          </button>
        </div>
        {responderMutation.isError && (
          <p className="text-label-sm text-error text-right">Error al enviar. Intentá de nuevo.</p>
        )}
        {responderMutation.isSuccess && (
          <p className="text-label-sm text-tertiary text-right">Respuesta enviada correctamente</p>
        )}
      </form>
    </div>
  );
}
