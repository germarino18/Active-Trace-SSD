import type { MetricasColoquio } from '../types';

interface MetricasColoquioProps {
  metrics: MetricasColoquio;
}

interface KpiCard {
  icon: string;
  value: number;
  label: string;
  className: string;
}

export function MetricasColoquioCard({ metrics }: MetricasColoquioProps) {
  const cards: KpiCard[] = [
    {
      icon: 'group',
      value: metrics.total_alumnos,
      label: 'Total Alumnos',
      className: 'bg-primary/10 text-primary',
    },
    {
      icon: 'calendar_month',
      value: metrics.instancias_activas,
      label: 'Instancias Activas',
      className: 'bg-tertiary/10 text-tertiary',
    },
    {
      icon: 'event',
      value: metrics.reservas_activas,
      label: 'Reservas Activas',
      className: 'bg-info/10 text-info',
    },
    {
      icon: 'event_available',
      value: metrics.cupos_libres,
      label: 'Cupos Libres',
      className: 'bg-warning/10 text-warning',
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {cards.map((card) => (
        <div
          key={card.label}
          className="flex items-center gap-4 rounded-xl border border-outline-variant bg-surface-container-lowest p-4"
        >
          <div className={`flex h-12 w-12 items-center justify-center rounded-lg ${card.className}`}>
            <span className="material-symbols-outlined text-[24px]">{card.icon}</span>
          </div>
          <div>
            <p className="text-headline-lg font-bold text-on-surface">{card.value}</p>
            <p className="text-label-sm text-on-surface-variant">{card.label}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
