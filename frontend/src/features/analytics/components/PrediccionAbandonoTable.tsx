import { useState, useMemo } from 'react';
import { EmptyState } from '@/features/academico/components/EmptyState';
import type { PrediccionAbandono } from '../types/analytics';

interface PrediccionAbandonoTableProps {
  data: PrediccionAbandono[] | undefined;
  isLoading: boolean;
}

type SortKey = 'alumno_nombre' | 'materia' | 'promedio' | 'atrasos' | 'riesgo';

function LoadingSkeleton() {
  return (
    <div className="space-y-2">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="flex items-center gap-4">
          <div className="h-4 w-32 animate-pulse rounded bg-surface-container-low" />
          <div className="h-4 w-24 animate-pulse rounded bg-surface-container-low" />
          <div className="h-4 w-16 animate-pulse rounded bg-surface-container-low" />
          <div className="h-4 w-12 animate-pulse rounded bg-surface-container-low" />
          <div className="h-4 w-16 animate-pulse rounded bg-surface-container-low" />
        </div>
      ))}
    </div>
  );
}

const RISKO_STYLES: Record<string, { bg: string; text: string }> = {
  alto: { bg: 'bg-error/10', text: 'text-error' },
  medio: { bg: 'bg-warning/10', text: 'text-warning' },
  bajo: { bg: 'bg-tertiary/10', text: 'text-tertiary' },
};

const RISKO_LABELS: Record<string, string> = {
  alto: 'ALTO',
  medio: 'MEDIO',
  bajo: 'BAJO',
};

export function PrediccionAbandonoTable({ data, isLoading }: PrediccionAbandonoTableProps) {
  const [sortKey, setSortKey] = useState<SortKey>('riesgo');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc');

  const [filterRiesgo, setFilterRiesgo] = useState<string>('');

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(key);
      setSortDir('asc');
    }
  };

  const sortedData = useMemo(() => {
    if (!data) return [];
    let filtered = data;
    if (filterRiesgo) {
      filtered = data.filter((d) => d.riesgo === filterRiesgo);
    }
    return [...filtered].sort((a, b) => {
      const aVal = a[sortKey];
      const bVal = b[sortKey];
      if (aVal < bVal) return sortDir === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortDir === 'asc' ? 1 : -1;
      return 0;
    });
  }, [data, sortKey, sortDir, filterRiesgo]);

  const renderSortIcon = (key: SortKey) => {
    if (sortKey !== key) return null;
    return (
      <span className="material-symbols-outlined text-[14px] ml-1 align-middle">
        {sortDir === 'asc' ? 'arrow_upward' : 'arrow_downward'}
      </span>
    );
  };

  const getSortableHeader = (label: string, key: SortKey) => (
    <th
      className="px-3 py-2 text-label-xs font-medium text-outline uppercase tracking-wider cursor-pointer select-none hover:text-on-surface transition-colors"
      onClick={() => handleSort(key)}
    >
      {label}
      {renderSortIcon(key)}
    </th>
  );

  if (isLoading) {
    return (
      <div className="rounded-xl border border-outline-variant bg-surface p-4">
        <h4 className="text-label-sm font-medium text-on-surface-variant mb-4">
          Predicción de abandono
        </h4>
        <LoadingSkeleton />
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="rounded-xl border border-outline-variant bg-surface p-4">
        <h4 className="text-label-sm font-medium text-on-surface-variant mb-4">
          Predicción de abandono
        </h4>
        <EmptyState message="Sin datos de predicción" icon="person_off" />
      </div>
    );
  }

  const riesgoCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const d of data) {
      counts[d.riesgo] = (counts[d.riesgo] || 0) + 1;
    }
    return counts;
  }, [data]);

  return (
    <div className="rounded-xl border border-outline-variant bg-surface p-4">
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-label-sm font-medium text-on-surface-variant">
          Predicción de abandono
        </h4>
        <select
          value={filterRiesgo}
          onChange={(e) => setFilterRiesgo(e.target.value)}
          className="rounded-lg border border-outline-variant bg-surface-container-lowest px-2 py-1 text-label-sm text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <option value="">Todos los riesgos</option>
          <option value="alto">Alto ({riesgoCounts.alto || 0})</option>
          <option value="medio">Medio ({riesgoCounts.medio || 0})</option>
          <option value="bajo">Bajo ({riesgoCounts.bajo || 0})</option>
        </select>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="border-b border-outline-variant">
              {getSortableHeader('Nombre', 'alumno_nombre')}
              {getSortableHeader('Materia', 'materia')}
              {getSortableHeader('Promedio', 'promedio')}
              {getSortableHeader('Atrasos', 'atrasos')}
              {getSortableHeader('Riesgo', 'riesgo')}
            </tr>
          </thead>
          <tbody>
            {sortedData.map((item, idx) => {
              const style = RISKO_STYLES[item.riesgo] ?? { bg: 'bg-outline/10', text: 'text-on-surface-variant' };
              const label = RISKO_LABELS[item.riesgo] ?? item.riesgo;
              return (
                <tr
                  key={`${item.alumno_id}-${item.materia}-${idx}`}
                  className="border-b border-outline-variant/50 transition-colors hover:bg-surface-container-low"
                >
                  <td className="px-3 py-2.5 text-body-sm text-on-surface font-medium">
                    {item.alumno_nombre}
                  </td>
                  <td className="px-3 py-2.5 text-body-sm text-on-surface-variant">
                    {item.materia}
                  </td>
                  <td className="px-3 py-2.5 text-body-sm text-on-surface">
                    {item.promedio.toFixed(1)}%
                  </td>
                  <td className="px-3 py-2.5 text-body-sm text-on-surface">
                    {item.atrasos}
                  </td>
                  <td className="px-3 py-2.5">
                    <span className={`inline-flex rounded-full ${style.bg} px-2.5 py-0.5 text-label-xs font-medium ${style.text}`}>
                      {label}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
