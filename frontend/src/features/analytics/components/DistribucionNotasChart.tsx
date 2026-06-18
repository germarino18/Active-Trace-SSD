import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import type { DistribucionNotas } from '../types/analytics';

interface DistribucionNotasChartProps {
  data: DistribucionNotas[] | undefined;
  isLoading: boolean;
}

function LoadingSkeleton() {
  return (
    <div className="space-y-2">
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="h-4 w-full animate-pulse rounded bg-surface-container-low" />
      ))}
    </div>
  );
}

const BAR_COLORS = ['var(--color-primary)', 'var(--color-tertiary)', 'var(--color-secondary)', 'var(--color-error)'];

export function DistribucionNotasChart({ data, isLoading }: DistribucionNotasChartProps) {
  if (isLoading) {
    return (
      <div className="rounded-xl border border-outline-variant bg-surface p-4">
        <h4 className="text-label-sm font-medium text-on-surface-variant mb-4">
          Distribución de notas
        </h4>
        <LoadingSkeleton />
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="rounded-xl border border-outline-variant bg-surface p-4">
        <h4 className="text-label-sm font-medium text-on-surface-variant mb-4">
          Distribución de notas
        </h4>
        <div className="flex flex-col items-center justify-center py-8 text-center">
          <span className="material-symbols-outlined text-[40px] text-outline mb-2">bar_chart</span>
          <p className="text-body-md text-on-surface-variant">Sin datos de notas</p>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-outline-variant bg-surface p-4">
      <h4 className="text-label-sm font-medium text-on-surface-variant mb-4">
        Distribución de notas
      </h4>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-outline-variant)" />
          <XAxis dataKey="rango" tick={{ fill: 'var(--color-on-surface-variant)', fontSize: 12 }} />
          <YAxis tick={{ fill: 'var(--color-on-surface-variant)', fontSize: 12 }} allowDecimals={false} />
          <Tooltip
            contentStyle={{
              backgroundColor: 'var(--color-surface-container-high)',
              border: '1px solid var(--color-outline-variant)',
              borderRadius: '8px',
              color: 'var(--color-on-surface)',
            }}
          />
          <Bar dataKey="cantidad" radius={[4, 4, 0, 0]} barSize={60}>
            {data.map((_entry, idx) => (
              <Cell key={`cell-${idx}`} fill={BAR_COLORS[idx % BAR_COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
