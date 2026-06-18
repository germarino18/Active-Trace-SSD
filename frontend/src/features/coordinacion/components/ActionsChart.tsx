import { useMemo } from 'react';
import type { AccionPorDia } from '../types';

interface ActionsChartProps {
  data: AccionPorDia[];
  height?: number;
}

export function ActionsChart({ data, height = 200 }: ActionsChartProps) {
  const chartData = useMemo(() => {
    if (!data || data.length === 0) return null;

    const maxVal = Math.max(...data.map((d) => d.cantidad), 1);
    const padding = { top: 8, right: 8, bottom: 24, left: 32 };

    return {
      maxVal,
      padding,
      innerWidth: 100 - padding.left - padding.right,
    };
  }, [data]);

  if (!chartData || data.length === 0) {
    return (
      <div className="flex items-center justify-center text-label-sm text-on-surface-variant" style={{ height }}>
        Sin datos de acciones
      </div>
    );
  }

  const { maxVal, padding, innerWidth } = chartData;
  const barWidth = Math.max(4, Math.min(16, innerWidth / data.length - 2));
  const totalWidth = data.length * (barWidth + 2) + padding.left + padding.right;

  return (
    <div className="overflow-x-auto" style={{ height }}>
      <svg
        viewBox={`0 0 ${Math.max(totalWidth, 100)} ${height}`}
        className="h-full"
        preserveAspectRatio="xMidYMid meet"
      >
        {Array.from({ length: 5 }, (_, i) => {
          const val = Math.round((maxVal / 4) * i);
          const y = padding.top + ((height - padding.top - padding.bottom) * (maxVal - val)) / maxVal;
          return (
            <g key={i}>
              <line
                x1={padding.left}
                y1={y}
                x2={Math.max(totalWidth, 100) - padding.right}
                y2={y}
                className="stroke-outline-variant/40"
                strokeWidth={1}
              />
              <text
                x={padding.left - 4}
                y={y + 4}
                textAnchor="end"
                className="fill-on-surface-variant text-[9px]"
              >
                {val}
              </text>
            </g>
          );
        })}

        {data.map((d, i) => {
          const x = padding.left + i * (barWidth + 2);
          const barHeight = ((height - padding.top - padding.bottom) * d.cantidad) / maxVal;
          const y = height - padding.bottom - barHeight;

          return (
            <g key={d.fecha}>
              <rect
                x={x}
                y={y}
                width={barWidth}
                height={Math.max(barHeight, 1)}
                rx={2}
                className="fill-primary/70 hover:fill-primary"
              >
                <title>{`${d.fecha}: ${d.cantidad} acciones`}</title>
              </rect>
              {i % Math.max(1, Math.floor(data.length / 6)) === 0 && (
                <text
                  x={x + barWidth / 2}
                  y={height - 4}
                  textAnchor="end"
                  transform={`rotate(-45, ${x + barWidth / 2}, ${height - 4})`}
                  className="fill-on-surface-variant text-[7px]"
                >
                  {d.fecha}
                </text>
              )}
            </g>
          );
        })}
      </svg>
    </div>
  );
}
