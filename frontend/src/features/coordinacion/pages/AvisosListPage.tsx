import { Link } from 'react-router-dom';
import { useAvisos } from '../hooks/useAvisos';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { LoadingState } from '@/features/academico/components/LoadingState';
import { EmptyState } from '@/features/academico/components/EmptyState';
import type { Aviso, AvisoScope, AvisoSeverity } from '../types';

const severityConfig: Record<AvisoSeverity, { label: string; className: string }> = {
  INFO: { label: 'Info', className: 'bg-info/10 text-info' },
  ADVERTENCIA: { label: 'Advertencia', className: 'bg-warning/10 text-warning' },
  CRITICO: { label: 'Crítico', className: 'bg-error/10 text-error' },
};

const scopeLabels: Record<AvisoScope, string> = {
  GLOBAL: 'Global',
  POR_MATERIA: 'Materia',
  POR_COHORTE: 'Cohorte',
  POR_ROL: 'Rol',
};

function getScopeValueLabel(aviso: Aviso): string | null {
  if (aviso.materia_id) return aviso.materia_id;
  if (aviso.cohorte_id) return aviso.cohorte_id;
  if (aviso.rol_destino) return aviso.rol_destino;
  return null;
}

export function AvisosListPage() {
  const { hasPermission } = useAuth();

  const canAdmin = hasPermission('avisos:publicar');
  const canCreate = hasPermission('avisos:publicar');

  const { data, isLoading, isError } = useAvisos();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Avisos</h2>
          <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>
            Gestión de avisos y comunicaciones internas.
          </p>
        </div>
        {canCreate && (
          <Link
            to="/avisos/nuevo"
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
      ) : !data || data.length === 0 ? (
        <EmptyState message="No hay avisos disponibles" icon="notifications" />
      ) : (
        <div className="overflow-x-auto rounded-xl border border-outline-variant">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-outline-variant bg-surface-container-low">
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Título</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Alcance</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Severidad</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Vigencia</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {data.map((aviso: Aviso) => {
                const sev = severityConfig[aviso.severidad] ?? severityConfig.INFO;
                const scopeValue = getScopeValueLabel(aviso);
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
                      {scopeLabels[aviso.alcance]}
                      {scopeValue && ` (${scopeValue})`}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex items-center rounded-full px-2 py-0.5 text-label-xs font-medium ${sev.className}`}
                      >
                        {sev.label}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-body-sm text-on-surface-variant">
                      {aviso.inicio_en.slice(0, 10)} — {aviso.fin_en.slice(0, 10)}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        {canAdmin && (
                          <Link
                            to={`/avisos/${aviso.id}/editar`}
                            className="inline-flex items-center gap-1 rounded-lg bg-surface-container-low px-2.5 py-1 text-label-xs font-medium text-on-surface-variant transition-colors hover:bg-surface-container"
                          >
                            <span className="material-symbols-outlined text-[14px]">edit</span>
                          </Link>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
