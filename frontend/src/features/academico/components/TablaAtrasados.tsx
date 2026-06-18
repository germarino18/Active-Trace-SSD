import { useState, useMemo, useCallback } from 'react';
import type { AtrasadoEntry } from '../types';
import { EmptyState } from './EmptyState';
import { LoadingState } from './LoadingState';

interface TablaAtrasadosProps {
  data?: AtrasadoEntry[];
  isLoading?: boolean;
  umbral?: number;
}

type SortKey = 'nombre' | 'email' | 'comision' | 'actividades_pendientes' | 'nota_actual' | 'porcentaje' | 'estado';

export function TablaAtrasados({ data, isLoading, umbral }: TablaAtrasadosProps) {
  const [sortKey, setSortKey] = useState<SortKey>('porcentaje');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc');

  const handleSort = useCallback((key: SortKey) => {
    setSortKey((prev) => {
      if (prev === key) {
        setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
        return prev;
      }
      setSortDir('asc');
      return key;
    });
  }, []);

  const sorted = useMemo(() => {
    if (!data) return [];
    return [...data].sort((a, b) => {
      let cmp = 0;
      switch (sortKey) {
        case 'nombre':
          cmp = a.alumno.apellido.localeCompare(b.alumno.apellido);
          break;
        case 'email':
          cmp = a.alumno.email.localeCompare(b.alumno.email);
          break;
        case 'comision':
          cmp = a.alumno.comision.localeCompare(b.alumno.comision);
          break;
        case 'actividades_pendientes':
          cmp = a.actividades_pendientes - b.actividades_pendientes;
          break;
        case 'nota_actual':
          cmp = a.nota_actual - b.nota_actual;
          break;
        case 'porcentaje':
          cmp = a.porcentaje - b.porcentaje;
          break;
        case 'estado':
          cmp = a.estado.localeCompare(b.estado);
          break;
      }
      return sortDir === 'asc' ? cmp : -cmp;
    });
  }, [data, sortKey, sortDir]);

  if (isLoading) {
    return <LoadingState rows={5} cols={7} />;
  }

  if (!data || data.length === 0) {
    return <EmptyState message="No hay alumnos atrasados en esta materia" />;
  }

  const renderSortIcon = (key: SortKey) => {
    if (sortKey !== key) return null;
    return (
      <span className="material-symbols-outlined text-[16px] ml-1">
        {sortDir === 'asc' ? 'arrow_upward' : 'arrow_downward'}
      </span>
    );
  };

  const SortHeader = ({ label, sortKey: key }: { label: string; sortKey: SortKey }) => (
    <th
      className="cursor-pointer px-4 py-3 font-medium text-on-surface select-none hover:text-primary"
      onClick={() => handleSort(key)}
    >
      <div className="flex items-center">
        {label}
        {renderSortIcon(key)}
      </div>
    </th>
  );

  return (
    <div className="overflow-x-auto rounded-xl border border-outline-variant">
      <table className="w-full text-left text-label-md">
        <thead>
          <tr className="border-b border-outline-variant bg-surface-container-low">
            <SortHeader label="Nombre" sortKey="nombre" />
            <SortHeader label="Email" sortKey="email" />
            <SortHeader label="Comisión" sortKey="comision" />
            <SortHeader label="Pendientes" sortKey="actividades_pendientes" />
            <SortHeader label="Nota Actual" sortKey="nota_actual" />
            <SortHeader label="Porcentaje" sortKey="porcentaje" />
            <SortHeader label="Estado" sortKey="estado" />
          </tr>
        </thead>
        <tbody>
          {sorted.map((entry) => (
            <tr
              key={entry.alumno.id}
              className={`border-b border-outline-variant transition-colors hover:bg-surface-container-low ${
                entry.estado === 'atrasado' ? 'bg-error/5' : ''
              }`}
            >
              <td className="px-4 py-3 text-on-surface font-medium">
                {entry.alumno.apellido}, {entry.alumno.nombre}
              </td>
              <td className="px-4 py-3 text-on-surface-variant">{entry.alumno.email}</td>
              <td className="px-4 py-3 text-on-surface-variant">{entry.alumno.comision}</td>
              <td className="px-4 py-3 text-on-surface-variant">{entry.actividades_pendientes}</td>
              <td className="px-4 py-3 text-on-surface-variant">{entry.nota_actual}</td>
              <td className="px-4 py-3 text-on-surface-variant">{entry.porcentaje}%</td>
              <td className="px-4 py-3">
                <span
                  className={`inline-flex rounded-full px-2 py-0.5 text-label-xs font-medium ${
                    entry.estado === 'atrasado'
                      ? 'bg-error/10 text-error'
                      : 'bg-success/10 text-success'
                  }`}
                >
                  {entry.estado === 'atrasado' ? 'Atrasado' : 'Al día'}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
