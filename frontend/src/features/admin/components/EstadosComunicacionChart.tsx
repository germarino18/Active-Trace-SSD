import type { EstadoComunicacion } from '../types/metricas';

interface EstadosComunicacionChartProps {
  data: EstadoComunicacion[] | undefined;
  isLoading: boolean;
}

const ESTADO_COLORS: Record<string, { bg: string; text: string; icon: string; label: string }> = {
  ok: { bg: 'bg-success/10', text: 'text-success', icon: 'check_circle', label: 'OK' },
  pendiente: { bg: 'bg-warning/10', text: 'text-warning', icon: 'schedule', label: 'Pendiente' },
  enviando: { bg: 'bg-info/10', text: 'text-info', icon: 'sync', label: 'Enviando' },
  fallido: { bg: 'bg-error/10', text: 'text-error', icon: 'error', label: 'Fallido' },
};

function LoadingSkeleton() {
  return (
    <div className="grid grid-cols-2 gap-3">
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="h-24 animate-pulse rounded-xl bg-surface-container-low" />
      ))}
    </div>
  );
}

export function EstadosComunicacionChart({ data, isLoading }: EstadosComunicacionChartProps) {
  if (isLoading) {
    return (
      <div className="rounded-xl border border-outline-variant bg-surface p-4">
        <h4 className="text-label-sm font-medium text-on-surface-variant mb-4">Estado de comunicaciones</h4>
        <LoadingSkeleton />
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="rounded-xl border border-outline-variant bg-surface p-4">
        <h4 className="text-label-sm font-medium text-on-surface-variant mb-4">Estado de comunicaciones</h4>
        <div className="flex flex-col items-center justify-center py-8 text-center">
          <span className="material-symbols-outlined text-[40px] text-outline mb-2">mail</span>
          <p className="text-body-md text-on-surface-variant">Sin comunicaciones</p>
        </div>
      </div>
    );
  }

  const total = data.reduce((sum, e) => sum + e.cantidad, 0);

  return (
    <div className="rounded-xl border border-outline-variant bg-surface p-4">
      <h4 className="text-label-sm font-medium text-on-surface-variant mb-4">Estado de comunicaciones</h4>
      <div className="grid grid-cols-2 gap-3">
        {data.map((item) => {
          const color = ESTADO_COLORS[item.estado] ?? {
            bg: 'bg-outline/10',
            text: 'text-on-surface-variant',
            icon: 'help',
            label: item.estado,
          };
          const pct = total > 0 ? Math.round((item.cantidad / total) * 100) : 0;

          return (
            <div
              key={item.estado}
              className={`rounded-xl border border-outline-variant p-4 transition-colors ${color.bg}`}
            >
              <div className="flex items-center gap-2 mb-2">
                <span className={`material-symbols-outlined text-[20px] ${color.text}`}>
                  {color.icon}
                </span>
                <span className={`text-label-sm font-medium ${color.text}`}>
                  {color.label}
                </span>
              </div>
              <p className="font-headline-lg text-headline-lg text-on-surface">{item.cantidad}</p>
              <p className="text-body-xs text-on-surface-variant mt-1">{pct}% del total</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
