import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Spinner } from '@/shared/components/Spinner';
import { EmptyState } from '../components/EmptyState';
import { ErrorState } from '../components/ErrorState';
import * as alumnoService from '../services/alumno.service';

export function MisFechasPage() {
  const [filtroMateria, setFiltroMateria] = useState<string>('');

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['alumno', 'fechas'],
    queryFn: () => alumnoService.getFechas(),
  });

  const materias = useMemo(() => {
    if (!data) return [];
    return [...new Set(data.map((f) => f.materia_nombre))];
  }, [data]);

  const filtradas = useMemo(() => {
    if (!data) return [];
    if (!filtroMateria) return data;
    return data.filter((f) => f.materia_nombre === filtroMateria);
  }, [data, filtroMateria]);

  if (isLoading) return <div className="flex justify-center py-12"><Spinner size="lg" /></div>;
  if (error) return <ErrorState message="Error al cargar fechas" onRetry={() => refetch()} />;
  if (!data || data.length === 0) return <EmptyState message="No hay fechas académicas registradas" icon="calendar_month" />;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-headline-lg text-headline-lg text-on-surface">Calendario Académico</h2>
        <p className="text-body-md text-on-surface-variant mt-1">Fechas importantes de tus materias</p>
      </div>

      <div className="flex items-center gap-2">
        <span className="material-symbols-outlined text-outline text-[20px]">filter_list</span>
        <select
          value={filtroMateria}
          onChange={(e) => setFiltroMateria(e.target.value)}
          className="rounded-lg bg-surface-container border border-outline-variant px-3 py-2 text-label-sm text-on-surface focus:ring-2 focus:ring-primary focus:outline-none max-w-xs"
        >
          <option value="">Todas las materias</option>
          {materias.map((m) => (
            <option key={m} value={m}>{m}</option>
          ))}
        </select>
      </div>

      <div className="space-y-3">
        {filtradas.length === 0 ? (
          <EmptyState message="No hay fechas para el filtro seleccionado" icon="filter_alt" />
        ) : (
          filtradas.map((fecha) => (
            <div
              key={fecha.id}
              className="bg-surface-container-lowest rounded-xl border border-outline-variant p-4 flex items-start gap-3"
            >
              <div className="flex flex-col items-center justify-center w-14 h-14 rounded-lg bg-primary/10 shrink-0">
                <span className="text-label-xs font-medium text-primary uppercase">
                  {new Date(fecha.fecha).toLocaleDateString('es-AR', { month: 'short' })}
                </span>
                <span className="font-headline-lg text-headline-md text-primary leading-none">
                  {new Date(fecha.fecha).getDate()}
                </span>
              </div>

              <div className="flex-1 min-w-0">
                <h3 className="text-label-sm font-medium text-on-surface">{fecha.descripcion}</h3>
                <p className="text-label-xs text-on-surface-variant mt-0.5">
                  {fecha.materia_nombre}
                </p>
                <span className="inline-flex rounded-full bg-surface-container-high px-2 py-0.5 text-label-xs text-on-surface-variant mt-1.5">
                  {fecha.tipo}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
