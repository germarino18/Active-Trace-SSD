import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Spinner } from '@/shared/components/Spinner';
import { EmptyState } from '../components/EmptyState';
import { ErrorState } from '../components/ErrorState';
import { ReservaTurnoModal } from '../components/ReservaTurnoModal';
import * as alumnoService from '../services/alumno.service';
import type { ConvocatoriaColoquio } from '../types/alumno.types';

export function MisColoquiosPage() {
  const [selectedConvocatoria, setSelectedConvocatoria] = useState<ConvocatoriaColoquio | null>(null);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['alumno', 'coloquios'],
    queryFn: () => alumnoService.getConvocatorias(),
  });

  if (isLoading) return <div className="flex justify-center py-12"><Spinner size="lg" /></div>;
  if (error) return <ErrorState message="Error al cargar convocatorias" onRetry={() => refetch()} />;
  if (!data || data.length === 0) return <EmptyState message="No hay convocatorias de coloquio abiertas" icon="quiz" />;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-headline-lg text-headline-lg text-on-surface">Coloquios</h2>
        <p className="text-body-md text-on-surface-variant mt-1">Reservá tu turno para los coloquios disponibles</p>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {data.map((convocatoria) => {
          const totalCupos = convocatoria.fechas.reduce((acc, f) => acc + f.cupos_restantes, 0);
          const fechaMasProxima = [...convocatoria.fechas].sort(
            (a, b) => new Date(a.fecha).getTime() - new Date(b.fecha).getTime(),
          )[0];

          return (
            <div
              key={convocatoria.id}
              className="bg-surface-container-lowest rounded-xl border border-outline-variant p-4"
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="text-label-md font-medium text-on-surface">{convocatoria.materia_nombre}</h3>
                  <p className="text-label-sm text-on-surface-variant mt-0.5">
                    {convocatoria.fechas.length} fecha{convocatoria.fechas.length !== 1 ? 's' : ''} disponible{convocatoria.fechas.length !== 1 ? 's' : ''}
                    {totalCupos > 0 ? ` · ${totalCupos} cupo${totalCupos !== 1 ? 's' : ''}` : ' · Sin cupos'}
                  </p>
                </div>
                <span className="text-label-xs text-on-surface-variant">
                  Límite: {new Date(convocatoria.fecha_limite).toLocaleDateString('es-AR')}
                </span>
              </div>

              <div className="flex flex-wrap gap-2 mb-3">
                {convocatoria.fechas.map((f) => (
                  <span
                    key={f.fecha_id}
                    className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-label-xs font-medium ${
                      f.cupos_restantes > 0
                        ? 'bg-tertiary/10 text-tertiary'
                        : 'bg-error/10 text-error'
                    }`}
                  >
                    {new Date(f.fecha).toLocaleDateString('es-AR')}
                    <span className="opacity-70">({f.cupos_restantes})</span>
                  </span>
                ))}
              </div>

              <button
                type="button"
                onClick={() => setSelectedConvocatoria(convocatoria)}
                disabled={totalCupos === 0}
                className="rounded-lg bg-primary px-4 py-2 text-label-sm font-medium text-on-primary transition-colors hover:bg-primary/90 disabled:opacity-50"
              >
                Reservar turno
              </button>
            </div>
          );
        })}
      </div>

      {selectedConvocatoria && (
        <ReservaTurnoModal
          convocatoria={selectedConvocatoria}
          onClose={() => setSelectedConvocatoria(null)}
        />
      )}
    </div>
  );
}
