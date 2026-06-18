import type { LiquidacionKPIs as LiquidacionKPIsType } from '../types/liquidaciones';

interface LiquidacionKPIsProps {
  kpis: LiquidacionKPIsType;
  isLoading?: boolean;
}

function KpiCard({
  icon,
  label,
  value,
  isLoading,
}: {
  icon: string;
  label: string;
  value: string | number;
  isLoading?: boolean;
}) {
  return (
    <div className="rounded-xl border border-outline-variant bg-surface p-4 transition-colors hover:bg-surface-container-low">
      <div className="flex items-center gap-3">
        <span className="material-symbols-outlined text-[28px] text-primary">{icon}</span>
        <div>
          <p className="text-label-sm text-on-surface-variant">{label}</p>
          {isLoading ? (
            <div className="mt-1 h-7 w-20 animate-pulse rounded bg-surface-container-low" />
          ) : (
            <p className="font-headline-lg text-headline-lg text-on-surface">{value}</p>
          )}
        </div>
      </div>
    </div>
  );
}

export function LiquidacionKPIs({ kpis, isLoading }: LiquidacionKPIsProps) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <KpiCard
        icon="people"
        label="Total docentes"
        value={kpis.total_docentes}
        isLoading={isLoading}
      />
      <KpiCard
        icon="payments"
        label="Monto total"
        value={`$${kpis.monto_total.toLocaleString('es-AR')}`}
        isLoading={isLoading}
      />
      <KpiCard
        icon="receipt"
        label="Facturas pendientes"
        value={kpis.facturas_pendientes}
        isLoading={isLoading}
      />
      <KpiCard
        icon="check_circle"
        label="Períodos cerrados"
        value={kpis.periodos_cerrados}
        isLoading={isLoading}
      />
    </div>
  );
}
