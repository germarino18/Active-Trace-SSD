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

function formatDate(iso: string | null | undefined): string {
  if (!iso) return '—';
  const d = new Date(iso);
  if (isNaN(d.getTime())) return '—';
  return d.toLocaleDateString('es-AR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function TipoAccionBadge({ tipo }: { tipo: string }) {
  const prefixColorMap: Record<string, string> = {
    IMPERSONACION: 'bg-info/10 text-info',
    CARRERA: 'bg-primary/10 text-primary',
    MATERIA: 'bg-secondary/10 text-secondary',
    COHORTE: 'bg-warning/10 text-warning',
    DICTADO: 'bg-warning/10 text-warning',
    USUARIO: 'bg-success/10 text-success',
    ASIGNACION: 'bg-primary/10 text-primary',
    ENCUENTRO: 'bg-info/10 text-info',
    COLOQUIO: 'bg-secondary/10 text-secondary',
    AVISO: 'bg-info/10 text-info',
    TAREA: 'bg-outline/10 text-on-surface-variant',
    COMUNICACION: 'bg-success/10 text-success',
    LIQUIDACION: 'bg-error/10 text-error',
    PERFIL: 'bg-primary/10 text-primary',
  };

  const prefix = tipo.split('_')[0] ?? '';
  const colorClass = prefixColorMap[prefix] ?? 'bg-outline/10 text-on-surface-variant';

  return (
    <span className={`inline-flex rounded-full px-2.5 py-0.5 text-label-xs font-medium ${colorClass}`}>
      {(tipo ?? '').replace(/_/g, ' ')}
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
                  {formatDate(registro.fecha_hora)}
                </td>
                <td className="px-4 py-3 text-body-sm text-on-surface font-medium">
                  {registro.actor_nombre ?? '—'}
                </td>
                <td className="px-4 py-3 text-body-sm text-on-surface-variant">
                  {registro.materia_nombre ?? '—'}
                </td>
                <td className="px-4 py-3">
                  <TipoAccionBadge tipo={registro.accion} />
                </td>
                <td className="px-4 py-3 text-body-sm text-on-surface-variant font-mono">
                  {registro.ip ?? '—'}
                </td>
                <td className="px-4 py-3 text-body-sm text-on-surface-variant max-w-[200px] truncate">
                  {registro.user_agent ?? '—'}
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
