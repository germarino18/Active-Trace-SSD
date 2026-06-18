import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { AtrasadosPorCohorte } from '../types/analytics';

interface TendenciasAtrasadosChartProps {
  data: AtrasadosPorCohorte[] | undefined;
  isLoading: boolean;
}

function LoadingSkeleton() {
  return (
    <div className="space-y-2">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="h-4 w-full animate-pulse rounded bg-surface-container-low" />
      ))}
    </div>
  );
}

export function TendenciasAtrasadosChart({ data, isLoading }: TendenciasAtrasadosChartProps) {
  if (isLoading) {
    return (
      <div className="rounded-xl border border-outline-variant bg-surface p-4">
        <h4 className="text-label-sm font-medium text-on-surface-variant mb-4">
          Tendencias de atrasados por cohorte
        </h4>
        <LoadingSkeleton />
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="rounded-xl border border-outline-variant bg-surface p-4">
        <h4 className="text-label-sm font-medium text-on-surface-variant mb-4">
          Tendencias de atrasados por cohorte
        </h4>
        <div className="flex flex-col items-center justify-center py-8 text-center">
          <span className="material-symbols-outlined text-[40px] text-outline mb-2">show_chart</span>
          <p className="text-body-md text-on-surface-variant">Sin datos de tendencias</p>
        </div>
      </div>
    );
  }

  const cohortes = [...new Set(data.map((d) => d.cohorte))];
  const lineColors = ['var(--color-primary)', 'var(--color-tertiary)', 'var(--color-secondary)', 'var(--color-error)'];

  return (
    <div className="rounded-xl border border-outline-variant bg-surface p-4">
      <h4 className="text-label-sm font-medium text-on-surface-variant mb-4">
        Tendencias de atrasados por cohorte
      </h4>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-outline-variant)" />
          <XAxis dataKey="fecha" tick={{ fill: 'var(--color-on-surface-variant)', fontSize: 12 }} />
          <YAxis tick={{ fill: 'var(--color-on-surface-variant)', fontSize: 12 }} />
          <Tooltip
            contentStyle={{
              backgroundColor: 'var(--color-surface-container-high)',
              border: '1px solid var(--color-outline-variant)',
              borderRadius: '8px',
              color: 'var(--color-on-surface)',
            }}
          />
          <Legend />
          {cohortes.map((cohorte, idx) => (
            <Line
              key={cohorte}
              type="monotone"
              dataKey="porcentaje"
              data={data.filter((d) => d.cohorte === cohorte)}
              name={cohorte}
              stroke={lineColors[idx % lineColors.length]}
              strokeWidth={2}
              dot={{ r: 4 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
