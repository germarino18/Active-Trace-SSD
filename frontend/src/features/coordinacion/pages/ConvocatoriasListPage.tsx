import { Link } from 'react-router-dom';
import { useConvocatorias } from '../hooks/useColoquios';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { LoadingState } from '@/features/academico/components/LoadingState';
import { EmptyState } from '@/features/academico/components/EmptyState';

export function ConvocatoriasListPage() {
  const { hasPermission } = useAuth();
  const { data, isLoading, isError } = useConvocatorias();

  const canCreate = hasPermission('coordinacion:coloquios:crear');
  const canViewDetail = hasPermission('coordinacion:coloquios:ver');

  const totalDias = (conv: { dias?: { slots?: number; cupo_por_slot?: number }[] }) =>
    conv.dias?.reduce((sum, d) => sum + (d.slots ?? 0) * (d.cupo_por_slot ?? 0), 0) ?? 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Convocatorias a Coloquios</h2>
          <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>
            Gestioná las convocatorias a coloquios y exámenes orales.
          </p>
        </div>
        {canCreate && (
          <Link
            to="/coloquios/crear"
            className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-label-sm font-medium text-on-primary transition-colors hover:bg-primary/90"
          >
            <span className="material-symbols-outlined text-[18px]">add</span>
            Nueva Convocatoria
          </Link>
        )}
      </div>

      {isLoading ? (
        <LoadingState rows={5} cols={7} />
      ) : isError ? (
        <EmptyState message="Error al cargar las convocatorias" icon="error" />
      ) : !data || data.items.length === 0 ? (
        <EmptyState message="No hay convocatorias registradas" icon="calendar_month" />
      ) : (
        <div className="overflow-x-auto rounded-xl border border-outline-variant">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-outline-variant bg-surface-container-low">
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Materia</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Instancia</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Días</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Cupos Totales</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Creada</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((conv) => (
                <tr
                  key={conv.id}
                  className="border-b border-outline-variant transition-colors hover:bg-surface-container-low"
                >
                  <td className="px-4 py-3 text-body-sm font-medium text-on-surface">{conv.materia_nombre}</td>
                  <td className="px-4 py-3 text-body-sm text-on-surface-variant">{conv.instancia}</td>
                  <td className="px-4 py-3 text-body-sm text-on-surface-variant">{conv.dias?.length ?? 0}</td>
                  <td className="px-4 py-3 text-body-sm text-on-surface-variant">{totalDias(conv)}</td>
                  <td className="px-4 py-3 text-body-sm text-on-surface-variant">
                    {new Date(conv.created_at).toLocaleDateString('es-AR')}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      {canViewDetail && (
                        <Link
                          to={`/coloquios/${conv.id}`}
                          className="inline-flex items-center gap-1 rounded-lg bg-surface-container px-3 py-1.5 text-label-xs text-on-surface-variant transition-colors hover:bg-surface-container-high"
                        >
                          <span className="material-symbols-outlined text-[14px]">visibility</span>
                          Ver detalle
                        </Link>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
