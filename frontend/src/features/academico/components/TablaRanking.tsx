import type { RankingEntry } from '../types';
import { EmptyState } from './EmptyState';
import { LoadingState } from './LoadingState';

interface TablaRankingProps {
  data?: RankingEntry[];
  isLoading?: boolean;
}

export function TablaRanking({ data, isLoading }: TablaRankingProps) {
  if (isLoading) {
    return <LoadingState rows={5} cols={5} />;
  }

  if (!data || data.length === 0) {
    return <EmptyState message="No hay datos de ranking disponibles" />;
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-outline-variant">
      <table className="w-full text-left text-label-md">
        <thead>
          <tr className="border-b border-outline-variant bg-surface-container-low">
            <th className="px-4 py-3 font-medium text-on-surface">#</th>
            <th className="px-4 py-3 font-medium text-on-surface">Nombre</th>
            <th className="px-4 py-3 font-medium text-on-surface">Aprobadas</th>
            <th className="px-4 py-3 font-medium text-on-surface">Total</th>
            <th className="px-4 py-3 font-medium text-on-surface">Porcentaje</th>
          </tr>
        </thead>
        <tbody>
          {data.map((entry) => (
            <tr
              key={entry.alumno.id}
              className="border-b border-outline-variant transition-colors hover:bg-surface-container-low"
            >
              <td className="px-4 py-3 text-on-surface-variant">{entry.rank}</td>
              <td className="px-4 py-3 text-on-surface font-medium">
                {entry.alumno.apellido}, {entry.alumno.nombre}
              </td>
              <td className="px-4 py-3 text-on-surface-variant">{entry.aprobadas}</td>
              <td className="px-4 py-3 text-on-surface-variant">{entry.total_actividades}</td>
              <td className="px-4 py-3 text-on-surface-variant">{entry.porcentaje}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
