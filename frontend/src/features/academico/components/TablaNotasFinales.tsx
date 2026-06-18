import { useCallback, useRef } from 'react';
import type { NotaFinalEntry } from '../types';
import { EmptyState } from './EmptyState';
import { LoadingState } from './LoadingState';

interface TablaNotasFinalesProps {
  data?: NotaFinalEntry[];
  isLoading?: boolean;
}

export function TablaNotasFinales({ data, isLoading }: TablaNotasFinalesProps) {
  const tableRef = useRef<HTMLDivElement>(null);

  const handleExport = useCallback(() => {
    if (!data || data.length === 0) return;

    const headers = ['Nombre', 'Apellido', 'Email', 'Nota Final', 'Estado'];
    const rows = data.map(
      (entry) =>
        `${entry.alumno.nombre},${entry.alumno.apellido},${entry.alumno.email},${entry.nota_final},${entry.estado}`,
    );
    const csv = [headers.join(','), ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'notas-finales.csv';
    a.click();
    URL.revokeObjectURL(url);
  }, [data]);

  if (isLoading) {
    return <LoadingState rows={5} cols={4} />;
  }

  if (!data || data.length === 0) {
    return <EmptyState message="No hay notas finales disponibles" />;
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <button
          type="button"
          onClick={handleExport}
          className="flex items-center gap-2 rounded-lg border border-outline-variant px-3 py-2 text-label-sm font-medium text-on-surface transition-colors hover:bg-surface-container-low"
        >
          <span className="material-symbols-outlined text-[18px]">download</span>
          Exportar CSV
        </button>
      </div>
      <div className="overflow-x-auto rounded-xl border border-outline-variant" ref={tableRef}>
        <table className="w-full text-left text-label-md">
          <thead>
            <tr className="border-b border-outline-variant bg-surface-container-low">
              <th className="px-4 py-3 font-medium text-on-surface">Nombre</th>
              <th className="px-4 py-3 font-medium text-on-surface">Apellido</th>
              <th className="px-4 py-3 font-medium text-on-surface">Email</th>
              <th className="px-4 py-3 font-medium text-on-surface">Nota Final</th>
              <th className="px-4 py-3 font-medium text-on-surface">Estado</th>
            </tr>
          </thead>
          <tbody>
            {data.map((entry) => (
              <tr
                key={entry.alumno.id}
                className="border-b border-outline-variant transition-colors hover:bg-surface-container-low"
              >
                <td className="px-4 py-3 text-on-surface">{entry.alumno.nombre}</td>
                <td className="px-4 py-3 text-on-surface">{entry.alumno.apellido}</td>
                <td className="px-4 py-3 text-on-surface-variant">{entry.alumno.email}</td>
                <td className="px-4 py-3 text-on-surface-variant">{entry.nota_final}</td>
                <td className="px-4 py-3">
                  <span
                    className={`inline-flex rounded-full px-2 py-0.5 text-label-xs font-medium ${
                      entry.estado === 'aprobado'
                        ? 'bg-success/10 text-success'
                        : 'bg-error/10 text-error'
                    }`}
                  >
                    {entry.estado === 'aprobado' ? 'Aprobado' : 'Desaprobado'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
