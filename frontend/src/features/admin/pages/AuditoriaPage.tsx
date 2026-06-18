import { useState, useCallback } from 'react';
import { useAuditoriaLog } from '../hooks/useAuditoriaLog';
import { AuditoriaFilters } from '../components/AuditoriaFilters';
import { AuditoriaTable } from '../components/AuditoriaTable';
import { HelpButton } from '@/features/coordinacion/components/HelpButton';
import type { AuditoriaFilters as AuditoriaFiltersType } from '../types/auditoria';

const DEFAULT_LIMIT = 200;

const DEFAULT_FILTERS: AuditoriaFiltersType = {
  offset: 0,
  limit: DEFAULT_LIMIT,
};

export function AuditoriaPage() {
  const [filters, setFilters] = useState<AuditoriaFiltersType>(DEFAULT_FILTERS);

  const { data, isLoading } = useAuditoriaLog(filters);

  const handleFilterChange = useCallback((key: string, value: unknown) => {
    setFilters((prev) => ({ ...prev, [key]: value, offset: 0 }));
  }, []);

  const handleClearFilters = useCallback(() => {
    setFilters(DEFAULT_FILTERS);
  }, []);

  const handlePrevPage = useCallback(() => {
    setFilters((prev) => ({
      ...prev,
      offset: Math.max(0, (prev.offset ?? 0) - DEFAULT_LIMIT),
    }));
  }, []);

  const handleNextPage = useCallback(() => {
    setFilters((prev) => ({
      ...prev,
      offset: (prev.offset ?? 0) + DEFAULT_LIMIT,
    }));
  }, []);

  const total = data?.total ?? 0;
  const offset = filters.offset ?? 0;
  const hasPrev = offset > 0;
  const hasNext = offset + DEFAULT_LIMIT < total;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <div>
          <h2 className="font-headline-lg text-headline-lg text-on-surface">Auditoría</h2>
          <p className="text-body-md text-on-surface-variant mt-1">
            Registro completo de actividades del sistema
          </p>
        </div>
        <HelpButton tooltip="Visualizá el log completo de auditoría del sistema con filtros por fecha, usuario, materia y tipo de acción." />
      </div>

      <AuditoriaFilters
        values={filters}
        onChange={handleFilterChange}
        onClear={handleClearFilters}
      />

      <AuditoriaTable
        items={data?.items}
        total={total}
        isLoading={isLoading}
      />

      <div className="flex items-center justify-between">
        <div className="text-body-sm text-on-surface-variant">
          Mostrando {offset + 1}–{Math.min(offset + DEFAULT_LIMIT, total)} de {total}
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            disabled={!hasPrev}
            onClick={handlePrevPage}
            className="flex items-center gap-1 rounded-lg border border-outline-variant px-3 py-1.5 text-label-sm text-on-surface transition-colors hover:bg-surface-container-low disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <span className="material-symbols-outlined text-[16px]">chevron_left</span>
            Anterior
          </button>
          <button
            type="button"
            disabled={!hasNext}
            onClick={handleNextPage}
            className="flex items-center gap-1 rounded-lg border border-outline-variant px-3 py-1.5 text-label-sm text-on-surface transition-colors hover:bg-surface-container-low disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Siguiente
            <span className="material-symbols-outlined text-[16px]">chevron_right</span>
          </button>
        </div>
      </div>
    </div>
  );
}
