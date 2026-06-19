import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAvisos, useConfirmarAck } from '../hooks/useAvisos';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { LoadingState } from '@/features/academico/components/LoadingState';
import { EmptyState } from '@/features/academico/components/EmptyState';
import type { Aviso, AvisoScope, AvisoSeverity } from '../types';
import { Button } from '@/shared/components/ds';

const severityConfig: Record<AvisoSeverity, { label: string; className: string }> = {
  info: { label: 'Info', className: 'bg-info/10 text-info' },
  warning: { label: 'Advertencia', className: 'bg-warning/10 text-warning' },
  critical: { label: 'Crítico', className: 'bg-error/10 text-error' },
};

const scopeLabels: Record<AvisoScope, string> = {
  Global: 'Global',
  Materia: 'Materia',
  Cohorte: 'Cohorte',
  Rol: 'Rol',
};

const isAdminView = (permissions: string[]) =>
  permissions.some((p) => p.startsWith('coordinacion:avisos:admin'));

export function AvisosListPage() {
  const { hasPermission, session } = useAuth();
  const confirmarAck = useConfirmarAck();
  const [page, setPage] = useState(0);
  const pageSize = 25;

  const canAdmin = session.status === 'authenticated' && isAdminView(session.user.permissions);
  const canCreate = hasPermission('coordinacion:avisos:crear');

  const { data, isLoading, isError } = useAvisos({
    offset: page * pageSize,
    limit: pageSize,
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Avisos</h2>
          <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>
            {canAdmin ? 'Gestión de avisos y comunicaciones internas.' : 'Mis avisos y notificaciones.'}
          </p>
        </div>
        {canCreate && (
          <Link
            to="/avisos/crear"
            className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-label-sm font-medium text-on-primary transition-colors hover:bg-primary/90"
          >
            <span className="material-symbols-outlined text-[18px]">add</span>
            Nuevo Aviso
          </Link>
        )}
      </div>

      {isLoading ? (
        <LoadingState rows={6} cols={6} />
      ) : isError ? (
        <EmptyState message="Error al cargar los avisos" icon="error" />
      ) : !data || data.items.length === 0 ? (
        <EmptyState message="No hay avisos disponibles" icon="notifications" />
      ) : (
        <>
          <div className="overflow-x-auto rounded-xl border border-outline-variant">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-outline-variant bg-surface-container-low">
                  <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Título</th>
                  <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Alcance</th>
                  <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Severidad</th>
                  <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Vigencia</th>
                  {canAdmin && (
                    <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Confirmados</th>
                  )}
                  <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((aviso: Aviso) => {
                  const sev = severityConfig[aviso.severidad];
                  return (
                    <tr
                      key={aviso.id}
                      className="border-b border-outline-variant transition-colors hover:bg-surface-container-low"
                    >
                      <td className="px-4 py-3">
                        <Link
                          to={`/avisos/${aviso.id}`}
                          className="text-body-sm font-medium text-primary hover:underline"
                        >
                          {aviso.titulo}
                        </Link>
                      </td>
                      <td className="px-4 py-3 text-body-sm text-on-surface-variant">
                        {scopeLabels[aviso.scope]}
                        {aviso.scope_value && ` (${aviso.scope_value})`}
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={`inline-flex items-center rounded-full px-2 py-0.5 text-label-xs font-medium ${sev.className}`}
                        >
                          {sev.label}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-body-sm text-on-surface-variant">
                        {aviso.vigencia_desde} — {aviso.vigencia_hasta}
                      </td>
                      {canAdmin && (
                        <td className="px-4 py-3 text-body-sm text-on-surface-variant">
                          {aviso.ack_count}/{aviso.total_acks} confirmado(s)
                        </td>
                      )}
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          {aviso.requiere_ack && !aviso.user_acked && (
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              onClick={() => confirmarAck.mutate(aviso.id)}
                              disabled={confirmarAck.isPending}
                            >
                              Confirmar lectura
                            </Button>
                          )}
                          {aviso.user_acked && (
                            <span className="text-label-xs text-success">✓ Leído</span>
                          )}
                          {canAdmin && (
                            <>
                              <Link
                                to={`/avisos/${aviso.id}/editar`}
                                className="inline-flex items-center gap-1 rounded-lg bg-surface-container-low px-2.5 py-1 text-label-xs font-medium text-on-surface-variant transition-colors hover:bg-surface-container"
                              >
                                <span className="material-symbols-outlined text-[14px]">edit</span>
                              </Link>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {data.total > pageSize && (
            <div className="flex items-center justify-center gap-2">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                disabled={page === 0}
              >
                Anterior
              </Button>
              <span className="text-label-sm text-on-surface-variant">
                Página {page + 1} de {Math.ceil(data.total / pageSize)}
              </span>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setPage((p) => p + 1)}
                disabled={(page + 1) * pageSize >= data.total}
              >
                Siguiente
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
