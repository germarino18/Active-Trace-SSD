import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Spinner } from '@/shared/components/Spinner';
import { EmptyState } from '../components/EmptyState';
import { ErrorState } from '../components/ErrorState';
import * as alumnoService from '../services/alumno.service';
import type { AvisoAlumno } from '../types/alumno.types';

type FiltroLeido = 'todos' | 'no_leidos' | 'leidos';

const prioridadBadge: Record<number, string> = {
  1: 'bg-error/10 text-error',
  2: 'bg-surface-container-high text-on-surface-variant',
  3: 'bg-surface-container-high text-on-surface-variant',
};

const prioridadLabel: Record<number, string> = {
  1: 'Alta',
  2: 'Media',
  3: 'Baja',
};

export function MisAvisosPage() {
  const queryClient = useQueryClient();
  const [filtro, setFiltro] = useState<FiltroLeido>('todos');

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['alumno', 'avisos'],
    queryFn: () => alumnoService.getAvisos(),
  });

  const confirmarMutation = useMutation({
    mutationFn: (avisoId: string) => alumnoService.confirmarAviso(avisoId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alumno', 'avisos'] });
    },
  });

  if (isLoading) return <div className="flex justify-center py-12"><Spinner size="lg" /></div>;
  if (error) return <ErrorState message="Error al cargar avisos" onRetry={() => refetch()} />;
  if (!data || data.length === 0) return <EmptyState message="No hay avisos activos" icon="campaign" />;

  const filtrados = data.filter((a: AvisoAlumno) => {
    if (filtro === 'no_leidos') return !a.leido;
    if (filtro === 'leidos') return a.leido;
    return true;
  });

  const tabs: { key: FiltroLeido; label: string }[] = [
    { key: 'todos', label: 'Todos' },
    { key: 'no_leidos', label: 'No leídos' },
    { key: 'leidos', label: 'Leídos' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-headline-lg text-headline-lg text-on-surface">Avisos</h2>
        <p className="text-body-md text-on-surface-variant mt-1">Tablón de avisos y comunicaciones oficiales</p>
      </div>

      <div className="border-b border-outline-variant">
        <nav className="flex gap-4 -mb-px">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              type="button"
              onClick={() => setFiltro(tab.key)}
              className={`px-4 py-3 text-label-md font-medium border-b-2 transition-colors ${
                filtro === tab.key
                  ? 'border-primary text-primary'
                  : 'border-transparent text-on-surface-variant hover:text-on-surface hover:border-outline-variant'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      <div className="space-y-3">
        {filtrados.length === 0 ? (
          <EmptyState message="No hay avisos que coincidan con el filtro" icon="filter_alt" />
        ) : (
          filtrados.map((aviso: AvisoAlumno) => (
            <div
              key={aviso.id}
              className={`bg-surface-container-lowest rounded-xl border p-4 transition-colors ${
                !aviso.leido ? 'border-primary/30' : 'border-outline-variant'
              }`}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    {!aviso.leido && (
                      <span className="h-2 w-2 rounded-full bg-primary shrink-0" />
                    )}
                    <h3 className="text-label-md font-medium text-on-surface">{aviso.titulo}</h3>
                    <span className={`inline-flex rounded-full px-2 py-0.5 text-label-xs font-medium ${prioridadBadge[aviso.prioridad] ?? ''}`}>
                      {prioridadLabel[aviso.prioridad] ?? aviso.prioridad}
                    </span>
                  </div>
                  <p className="text-body-md text-on-surface-variant whitespace-pre-line">{aviso.contenido}</p>
                  <p className="text-label-xs text-outline mt-2">
                    {new Date(aviso.fecha_publicacion).toLocaleDateString('es-AR', {
                      day: 'numeric', month: 'long', year: 'numeric',
                    })}
                    {aviso.vigencia_hasta && ` · Válido hasta ${new Date(aviso.vigencia_hasta).toLocaleDateString('es-AR')}`}
                  </p>
                </div>

                {aviso.require_ack && !aviso.leido && (
                  <button
                    type="button"
                    onClick={() => confirmarMutation.mutate(aviso.id)}
                    disabled={confirmarMutation.isPending}
                    className="shrink-0 rounded-lg bg-primary px-3 py-2 text-label-xs font-medium text-on-primary transition-colors hover:bg-primary/90 disabled:opacity-50"
                  >
                    {confirmarMutation.isPending ? 'Confirmando...' : 'Confirmar lectura'}
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
