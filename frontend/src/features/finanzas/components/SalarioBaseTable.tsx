import { LoadingState } from '@/features/academico/components/LoadingState';
import { EmptyState } from '@/features/academico/components/EmptyState';
import type { SalarioBase } from '../types/grilla-salarial';

const rolLabels: Record<string, string> = {
  PROFESOR: 'Profesor',
  TUTOR: 'Tutor',
  NEXO: 'Nexo',
  COORDINADOR: 'Coordinador',
};

interface SalarioBaseTableProps {
  items: SalarioBase[] | undefined;
  isLoading: boolean;
  onEdit: (item: SalarioBase) => void;
  canEdit: boolean;
}

export function SalarioBaseTable({ items, isLoading, onEdit, canEdit }: SalarioBaseTableProps) {
  if (isLoading) {
    return <LoadingState rows={4} cols={4} />;
  }

  if (!items || items.length === 0) {
    return <EmptyState message="No hay salarios base configurados" icon="money_off" />;
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-outline-variant">
      <table className="w-full text-left">
        <thead>
          <tr className="border-b border-outline-variant bg-surface-container-low">
            <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Rol</th>
            <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant text-right">Importe</th>
            <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Vigencia desde</th>
            <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Vigencia hasta</th>
            {canEdit && (
              <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Acciones</th>
            )}
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr
              key={item.id}
              className="border-b border-outline-variant transition-colors hover:bg-surface-container-low"
            >
              <td className="px-4 py-3">
                <span className="inline-flex rounded-full bg-primary/10 px-2.5 py-0.5 text-label-xs font-medium text-primary">
                  {rolLabels[item.rol] ?? item.rol}
                </span>
              </td>
              <td className="px-4 py-3 text-body-sm text-on-surface text-right font-medium">
                ${item.importe.toLocaleString('es-AR')}
              </td>
              <td className="px-4 py-3 text-body-sm text-on-surface-variant">
                {item.vigencia_desde}
              </td>
              <td className="px-4 py-3 text-body-sm text-on-surface-variant">
                {item.vigencia_hasta ?? '—'}
              </td>
              {canEdit && (
                <td className="px-4 py-3">
                  <button
                    type="button"
                    onClick={() => onEdit(item)}
                    className="rounded-lg p-1.5 text-outline transition-colors hover:bg-surface-container-low hover:text-primary"
                    aria-label={`Editar salario base de ${rolLabels[item.rol] ?? item.rol}`}
                  >
                    <span className="material-symbols-outlined text-[18px]">edit</span>
                  </button>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
