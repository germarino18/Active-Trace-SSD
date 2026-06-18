import type { AccionesPorDia } from '../types/metricas';

interface AccionesPorDiaChartProps {
  data: AccionesPorDia[] | undefined;
  isLoading: boolean;
}

function LoadingSkeleton() {
  return (
    <div className="space-y-2">
      {Array.from({ length: 7 }).map((_, i) => (
        <div key={i} className="flex items-center gap-3">
          <div className="h-4 w-20 animate-pulse rounded bg-surface-container-low" />
          <div className="h-6 flex-1 animate-pulse rounded bg-surface-container-low" />
          <div className="h-4 w-8 animate-pulse rounded bg-surface-container-low" />
        </div>
      ))}
    </div>
  );
}

function EmptyChart() {
  return (
    <div className="flex flex-col items-center justify-center py-8 text-center">
      <span className="material-symbols-outlined text-[40px] text-outline mb-2">bar_chart</span>
      <p className="text-body-md text-on-surface-variant">Sin datos de actividades</p>
    </div>
  );
}

export function AccionesPorDiaChart({ data, isLoading }: AccionesPorDiaChartProps) {
  if (isLoading) {
    return (
      <div className="rounded-xl border border-outline-variant bg-surface p-4">
        <h4 className="text-label-sm font-medium text-on-surface-variant mb-4">Acciones por día</h4>
        <LoadingSkeleton />
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="rounded-xl border border-outline-variant bg-surface p-4">
        <h4 className="text-label-sm font-medium text-on-surface-variant mb-4">Acciones por día</h4>
        <EmptyChart />
      </div>
    );
  }

  const maxTotal = Math.max(...data.map((d) => d.total), 1);

  return (
    <div className="rounded-xl border border-outline-variant bg-surface p-4">
      <h4 className="text-label-sm font-medium text-on-surface-variant mb-4">Acciones por día</h4>
      <div className="space-y-2">
        {data.map((item) => {
          const pct = Math.max((item.total / maxTotal) * 100, 4);
          return (
            <div key={item.fecha} className="flex items-center gap-3">
              <span className="w-24 flex-shrink-0 text-body-xs text-on-surface-variant truncate">
                {item.fecha}
              </span>
              <div className="flex-1">
                <div
                  className="h-6 rounded bg-primary/20 transition-all"
                  style={{ width: `${pct}%` }}
                >
                  <div
                    className="h-full rounded bg-primary transition-all"
                    style={{ width: `${pct}%` }}
                  />
                </div>
              </div>
              <span className="w-8 flex-shrink-0 text-right text-body-sm text-on-surface font-medium">
                {item.total}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
