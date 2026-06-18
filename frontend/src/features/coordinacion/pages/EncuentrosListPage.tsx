import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useEncuentros } from '../hooks/useEncuentros';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { LoadingState } from '@/features/academico/components/LoadingState';
import { EmptyState } from '@/features/academico/components/EmptyState';
import { Spinner } from '@/shared/components/Spinner';
import type { InstanciaEstado } from '../types';

const estadoConfig: Record<InstanciaEstado, { label: string; className: string }> = {
  Pendiente: { label: 'Pendiente', className: 'bg-warning/10 text-warning' },
  Realizado: { label: 'Realizado', className: 'bg-success/10 text-success' },
  Cancelado: { label: 'Cancelado', className: 'bg-error/10 text-error' },
};

export function EncuentrosListPage() {
  const { hasPermission } = useAuth();
  const [filters, setFilters] = useState({
    materia_id: '',
    docente_id: '',
    estado: '',
    desde: '',
    hasta: '',
  });
  const [page, setPage] = useState(0);
  const pageSize = 25;

  const activeFilters = Object.fromEntries(
    Object.entries(filters).filter(([, v]) => v !== ''),
  );

  const { data, isLoading, isError } = useEncuentros({
    ...activeFilters,
    offset: page * pageSize,
    limit: pageSize,
  });

  const canCreate = hasPermission('coordinacion:encuentros:crear');

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-headline-lg text-headline-lg text-on-surface">Encuentros</h2>
          <p className="text-body-md text-on-surface-variant mt-1">
            Administración de encuentros y clases en vivo.
          </p>
        </div>
        {canCreate && (
          <Link
            to="/encuentros/crear"
            className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-label-sm font-medium text-on-primary transition-colors hover:bg-primary/90"
          >
            <span className="material-symbols-outlined text-[18px]">add</span>
            Nuevo Encuentro
          </Link>
        )}
      </div>

      <div className="flex flex-wrap gap-3 rounded-xl border border-outline-variant bg-surface-container-lowest p-4">
        <input
          placeholder="Materia"
          value={filters.materia_id}
          onChange={(e) => { setFilters((f) => ({ ...f, materia_id: e.target.value })); setPage(0); }}
          className="rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-label-sm text-on-surface outline-none placeholder:text-outline focus:border-primary"
        />
        <input
          placeholder="Docente"
          value={filters.docente_id}
          onChange={(e) => { setFilters((f) => ({ ...f, docente_id: e.target.value })); setPage(0); }}
          className="rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-label-sm text-on-surface outline-none placeholder:text-outline focus:border-primary"
        />
        <select
          value={filters.estado}
          onChange={(e) => { setFilters((f) => ({ ...f, estado: e.target.value })); setPage(0); }}
          className="rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-label-sm text-on-surface outline-none focus:border-primary"
        >
          <option value="">Todos los estados</option>
          <option value="Pendiente">Pendiente</option>
          <option value="Realizado">Realizado</option>
          <option value="Cancelado">Cancelado</option>
        </select>
        <input
          type="date"
          value={filters.desde}
          onChange={(e) => { setFilters((f) => ({ ...f, desde: e.target.value })); setPage(0); }}
          className="rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-label-sm text-on-surface outline-none focus:border-primary"
        />
        <input
          type="date"
          value={filters.hasta}
          onChange={(e) => { setFilters((f) => ({ ...f, hasta: e.target.value })); setPage(0); }}
          className="rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-label-sm text-on-surface outline-none focus:border-primary"
        />
      </div>

      {isLoading ? (
        <LoadingState rows={8} cols={6} />
      ) : isError ? (
        <EmptyState message="Error al cargar los encuentros" icon="error" />
      ) : !data || data.items.length === 0 ? (
        <EmptyState message="No se encontraron encuentros" icon="event" />
      ) : (
        <>
          <div className="overflow-x-auto rounded-xl border border-outline-variant">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-outline-variant bg-surface-container-low">
                  <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Materia</th>
                  <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Título</th>
                  <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Fecha</th>
                  <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Hora</th>
                  <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Docente</th>
                  <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Estado</th>
                  <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Meet</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((item) => (
                  <tr
                    key={item.id}
                    className="border-b border-outline-variant transition-colors hover:bg-surface-container-low"
                  >
                    <td className="px-4 py-3 text-body-sm text-on-surface">{item.materia_nombre}</td>
                    <td className="px-4 py-3">
                      <Link
                        to={`/encuentros/${item.id}`}
                        className="text-body-sm font-medium text-primary hover:underline"
                      >
                        {item.titulo}
                      </Link>
                    </td>
                    <td className="px-4 py-3 text-body-sm text-on-surface-variant">{item.fecha}</td>
                    <td className="px-4 py-3 text-body-sm text-on-surface-variant">
                      {item.hora_inicio} - {item.hora_fin}
                    </td>
                    <td className="px-4 py-3 text-body-sm text-on-surface-variant">{item.docente_nombre ?? '-'}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex items-center rounded-full px-2 py-0.5 text-label-xs font-medium ${estadoConfig[item.estado].className}`}
                      >
                        {estadoConfig[item.estado].label}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {item.url_meet ? (
                        <a
                          href={item.url_meet}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 text-label-sm text-primary hover:underline"
                        >
                          <span className="material-symbols-outlined text-[14px]">videocam</span>
                          Abrir
                        </a>
                      ) : (
                        <span className="text-label-sm text-outline">-</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {data.total > pageSize && (
            <div className="flex items-center justify-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                disabled={page === 0}
                className="rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-sm text-on-surface transition-colors hover:bg-surface-container disabled:opacity-50"
              >
                Anterior
              </button>
              <span className="text-label-sm text-on-surface-variant">
                <span className="hidden sm:inline">Página </span>
                {page + 1}
                <span className="hidden sm:inline"> de {Math.ceil(data.total / pageSize)}</span>
              </span>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={(page + 1) * pageSize >= data.total}
                className="rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-sm text-on-surface transition-colors hover:bg-surface-container disabled:opacity-50"
              >
                Siguiente
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
