import { EmptyState } from '@/features/academico/components/EmptyState';
import type { InteraccionDocente } from '../types/metricas';

interface InteraccionesDocenteTableProps {
  data: InteraccionDocente[] | undefined;
  isLoading: boolean;
}

function LoadingSkeleton() {
  return (
    <div className="space-y-2">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="flex items-center gap-4">
          <div className="h-4 w-32 animate-pulse rounded bg-surface-container-low" />
          <div className="h-4 w-24 animate-pulse rounded bg-surface-container-low" />
          <div className="h-4 w-12 animate-pulse rounded bg-surface-container-low" />
        </div>
      ))}
    </div>
  );
}

export function InteraccionesDocenteTable({ data, isLoading }: InteraccionesDocenteTableProps) {
  if (isLoading) {
    return (
      <div className="rounded-xl border border-outline-variant bg-surface p-4">
        <h4 className="text-label-sm font-medium text-on-surface-variant mb-4">
          Interacciones por docente
        </h4>
        <LoadingSkeleton />
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="rounded-xl border border-outline-variant bg-surface p-4">
        <h4 className="text-label-sm font-medium text-on-surface-variant mb-4">
          Interacciones por docente
        </h4>
        <EmptyState message="Sin interacciones registradas" icon="person_off" />
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-outline-variant bg-surface p-4">
      <h4 className="text-label-sm font-medium text-on-surface-variant mb-4">
        Interacciones por docente
      </h4>
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="border-b border-outline-variant">
              <th className="px-3 py-2 text-label-xs font-medium text-outline uppercase tracking-wider">
                Docente
              </th>
              <th className="px-3 py-2 text-label-xs font-medium text-outline uppercase tracking-wider">
                Tipo de acción
              </th>
              <th className="px-3 py-2 text-label-xs font-medium text-outline uppercase tracking-wider text-right">
                Cantidad
              </th>
            </tr>
          </thead>
          <tbody>
            {data.map((item, idx) => (
              <tr
                key={`${item.docente_nombre}-${item.tipo_accion}-${idx}`}
                className="border-b border-outline-variant/50 transition-colors hover:bg-surface-container-low"
              >
                <td className="px-3 py-2.5 text-body-sm text-on-surface font-medium">
                  {item.docente_nombre}
                </td>
                <td className="px-3 py-2.5 text-body-sm text-on-surface-variant">
                  <span className="inline-flex rounded-full bg-primary/10 px-2.5 py-0.5 text-label-xs font-medium text-primary">
                    {(item.tipo_accion ?? '').replace(/_/g, ' ')}
                  </span>
                </td>
                <td className="px-3 py-2.5 text-body-sm text-on-surface text-right font-semibold">
                  {item.cantidad}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
