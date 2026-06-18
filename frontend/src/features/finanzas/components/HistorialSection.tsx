import { useState } from 'react';
import { LoadingState } from '@/features/academico/components/LoadingState';
import { EmptyState } from '@/features/academico/components/EmptyState';
import { Spinner } from '@/shared/components/Spinner';
import type { LiquidacionHistorialItem } from '../types/liquidaciones';

interface HistorialSectionProps {
  items: LiquidacionHistorialItem[] | undefined;
  isLoading: boolean;
}

export function HistorialSection({ items, isLoading }: HistorialSectionProps) {
  const [expanded, setExpanded] = useState<string | null>(null);

  if (isLoading) {
    return (
      <div className="space-y-3">
        <div className="h-6 w-48 animate-pulse rounded bg-surface-container-low" />
        <LoadingState rows={3} cols={3} />
      </div>
    );
  }

  if (!items || items.length === 0) {
    return (
      <div>
        <h3 className="font-headline-sm text-headline-sm text-on-surface mb-4">Historial</h3>
        <EmptyState message="No hay liquidaciones cerradas aún" icon="history" />
      </div>
    );
  }

  return (
    <div>
      <h3 className="font-headline-sm text-headline-sm text-on-surface mb-4">Historial de liquidaciones cerradas</h3>
      <div className="space-y-2">
        {items.map((item) => (
          <div
            key={item.periodo}
            className="rounded-xl border border-outline-variant bg-surface transition-colors hover:bg-surface-container-low"
          >
            <button
              type="button"
              onClick={() => setExpanded(expanded === item.periodo ? null : item.periodo)}
              className="flex w-full items-center justify-between px-4 py-3 text-left"
            >
              <div className="flex items-center gap-3">
                <span className="material-symbols-outlined text-[18px] text-outline transition-transform" style={{ transform: expanded === item.periodo ? 'rotate(90deg)' : 'rotate(0deg)' }}>
                  chevron_right
                </span>
                <div>
                  <p className="text-body-sm text-on-surface font-medium">{item.periodo}</p>
                  <p className="text-label-xs text-on-surface-variant">
                    Cerrada el {new Date(item.cerrada_en).toLocaleDateString('es-AR', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                    })}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-6">
                <div className="text-right">
                  <p className="text-label-xs text-on-surface-variant">Docentes</p>
                  <p className="text-body-sm text-on-surface">{item.total_docentes}</p>
                </div>
                <div className="text-right">
                  <p className="text-label-xs text-on-surface-variant">Monto</p>
                  <p className="text-body-sm text-on-surface font-semibold">
                    ${item.monto_total.toLocaleString('es-AR')}
                  </p>
                </div>
              </div>
            </button>

            {expanded === item.periodo && (
              <div className="border-t border-outline-variant px-4 py-4">
                <div className="rounded-lg border border-outline-variant bg-surface-container-low p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="material-symbols-outlined text-[18px] text-primary">lock</span>
                    <p className="text-label-sm text-on-surface-variant">
                      Liquidación cerrada — solo lectura
                    </p>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-body-sm">
                    <div>
                      <span className="text-on-surface-variant">Período: </span>
                      <span className="text-on-surface font-medium">{item.periodo}</span>
                    </div>
                    <div>
                      <span className="text-on-surface-variant">Cerrada el: </span>
                      <span className="text-on-surface font-medium">
                        {new Date(item.cerrada_en).toLocaleString('es-AR')}
                      </span>
                    </div>
                    <div>
                      <span className="text-on-surface-variant">Total docentes: </span>
                      <span className="text-on-surface font-medium">{item.total_docentes}</span>
                    </div>
                    <div>
                      <span className="text-on-surface-variant">Monto total: </span>
                      <span className="text-on-surface font-semibold">
                        ${item.monto_total.toLocaleString('es-AR')}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
