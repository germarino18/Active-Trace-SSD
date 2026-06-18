import type { ReportesRapidosResponse } from '../types';
import { EmptyState } from './EmptyState';
import { LoadingState } from './LoadingState';

interface ReportesRapidosProps {
  data?: ReportesRapidosResponse;
  isLoading?: boolean;
}

export function ReportesRapidos({ data, isLoading }: ReportesRapidosProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-24 animate-pulse rounded-xl bg-surface-container-low" />
        ))}
      </div>
    );
  }

  if (!data) {
    return <EmptyState message="No hay datos importados para esta materia" />;
  }

  const cards = [
    { label: 'Total Alumnos', value: data.total_alumnos, icon: 'people' },
    { label: 'En Riesgo', value: data.en_riesgo, icon: 'warning', highlight: data.en_riesgo > 0 },
    { label: 'Prom. Completitud', value: `${data.promedio_completitud}%`, icon: 'trending_up' },
    { label: 'Actividades', value: data.total_actividades, icon: 'assignment' },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 lg:grid-cols-4">
      {cards.map((card) => (
        <div
          key={card.label}
          className={`rounded-xl border p-md ${
            card.highlight
              ? 'border-error/30 bg-error/5'
              : 'border-outline-variant bg-surface-container-lowest'
          }`}
        >
          <div className="flex items-center gap-2">
            <span
              className={`material-symbols-outlined text-[20px] ${
                card.highlight ? 'text-error' : 'text-outline'
              }`}
            >
              {card.icon}
            </span>
            <p className="text-label-xs uppercase tracking-wider text-outline">{card.label}</p>
          </div>
          <p
            className={`mt-2 text-headline-lg font-semibold ${
              card.highlight ? 'text-error' : 'text-on-surface'
            }`}
          >
            {card.value}
          </p>
        </div>
      ))}
    </div>
  );
}
