import { useState } from 'react';
import { LoadingState } from '@/features/academico/components/LoadingState';
import { EmptyState } from '@/features/academico/components/EmptyState';
import { AuditoriaDetailModal } from './AuditoriaDetailModal';
import type { RegistroAuditoria } from '../types/auditoria';

interface AuditoriaTableProps {
  items: RegistroAuditoria[] | undefined;
  total: number;
  isLoading: boolean;
}

function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString('es-AR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function TipoAccionBadge({ tipo }: { tipo: string }) {
  const colorMap: Record<string, string> = {
    login: 'bg-info/10 text-info',
    logout: 'bg-outline/10 text-on-surface-variant',
    crear: 'bg-success/10 text-success',
    actualizar: 'bg-warning/10 text-warning',
    eliminar: 'bg-error/10 text-error',
    exportar: 'bg-primary/10 text-primary',
    importar: 'bg-secondary/10 text-secondary',
    enviar_comunicacion: 'bg-success/10 text-success',
    cancelar_comunicacion: 'bg-error/10 text-error',
  };

  const colorClass = colorMap[tipo] ?? 'bg-outline/10 text-on-surface-variant';

  return (
    <span className={`inline-flex rounded-full px-2.5 py-0.5 text-label-xs font-medium ${colorClass}`}>
      {tipo.replace(/_/g, ' ')}
    </span>
  );
}

export function AuditoriaTable({ items, total, isLoading }: AuditoriaTableProps) {
  const [selected, setSelected] = useState<RegistroAuditoria | null>(null);

  if (isLoading) {
    return <LoadingState rows={5} cols={6} />;
  }

  if (!items || items.length === 0) {
    return <EmptyState message="No hay registros de auditoría" icon="receipt_long" />;
  }

  return (
    <>
      <div className="text-body-sm text-on-surface-variant mb-2">
        {total} registro{total !== 1 ? 's' : ''}
      </div>

      <div className="overflow-x-auto rounded-xl border border-outline-variant">
        <table className="w-full text-left">
          <thead>
            <tr className="border-b border-outline-variant bg-surface-container-low">
              <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Fecha</th>
              <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Usuario</th>
              <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Materia</th>
              <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Acción</th>
              <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">IP</th>
              <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Agente</th>
              <th className="w-10 px-4 py-3" />
            </tr>
          </thead>
          <tbody>
            {items.map((registro) => (
              <tr
                key={registro.id}
                className="cursor-pointer border-b border-outline-variant transition-colors hover:bg-surface-container-low"
                onClick={() => setSelected(registro)}
              >
                <td className="px-4 py-3 text-body-sm text-on-surface whitespace-nowrap">
                  {formatDate(registro.fecha)}
                </td>
                <td className="px-4 py-3 text-body-sm text-on-surface font-medium">
                  {registro.usuario_nombre}
                </td>
                <td className="px-4 py-3 text-body-sm text-on-surface-variant">
                  {registro.materia_nombre ?? '—'}
                </td>
                <td className="px-4 py-3">
                  <TipoAccionBadge tipo={registro.tipo_accion} />
                </td>
                <td className="px-4 py-3 text-body-sm text-on-surface-variant font-mono">
                  {registro.ip_origen ?? '—'}
                </td>
                <td className="px-4 py-3 text-body-sm text-on-surface-variant max-w-[200px] truncate">
                  {registro.agente_usuario ?? '—'}
                </td>
                <td className="px-4 py-3">
                  <span className="material-symbols-outlined text-[18px] text-outline">
                    chevron_right
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selected && (
        <AuditoriaDetailModal
          registro={selected}
          onClose={() => setSelected(null)}
        />
      )}
    </>
  );
}
