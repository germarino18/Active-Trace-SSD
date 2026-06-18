import type { TareaEstado } from '../types';

interface TareaStateBadgeProps {
  estado: TareaEstado;
}

const config: Record<TareaEstado, { label: string; className: string }> = {
  Pendiente: { label: 'Pendiente', className: 'bg-warning/10 text-warning' },
  'En progreso': { label: 'En progreso', className: 'bg-info/10 text-info' },
  Resuelta: { label: 'Resuelta', className: 'bg-success/10 text-success' },
  Cancelada: { label: 'Cancelada', className: 'bg-error/10 text-error' },
};

export function TareaStateBadge({ estado }: TareaStateBadgeProps) {
  const c = config[estado];
  return (
    <span
      className={`inline-flex items-center rounded-full px-2 py-0.5 text-label-xs font-medium ${c.className}`}
    >
      {c.label}
    </span>
  );
}
