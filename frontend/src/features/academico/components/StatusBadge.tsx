import type { MensajeStatus } from '../types';

interface StatusBadgeProps {
  status: MensajeStatus;
}

const statusConfig: Record<MensajeStatus, { label: string; className: string }> = {
  Pendiente: { label: 'Pendiente', className: 'bg-surface-container-low text-on-surface-variant' },
  Enviando: { label: 'Enviando', className: 'bg-info/10 text-info' },
  OK: { label: 'Enviado', className: 'bg-success/10 text-success' },
  Fallido: { label: 'Fallido', className: 'bg-error/10 text-error' },
  Cancelado: { label: 'Cancelado', className: 'bg-warning/10 text-warning' },
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const config = statusConfig[status] ?? statusConfig.Pendiente;

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-label-xs font-medium ${config.className}`}
    >
      {status === 'Enviando' && (
        <span className="h-2 w-2 animate-pulse rounded-full bg-current" />
      )}
      {config.label}
    </span>
  );
}
