import { useColoquiosMios } from '../hooks/useProfesor';
import { LoadingState } from '@/features/academico/components/LoadingState';
import { EmptyState } from '@/features/academico/components/EmptyState';
import type { ColoquioProfesor } from '../types';

export function MisColoquiosProfesorPage() {
  const { data, isLoading, isError } = useColoquiosMios();

  return (
    <div className="space-y-4">
      <h3 style={{ margin: 0, fontSize: 20, fontWeight: 600, color: 'var(--on-surface)' }}>Mis Coloquios</h3>

      {isLoading ? (
        <LoadingState rows={4} cols={4} />
      ) : isError ? (
        <EmptyState message="Error al cargar los coloquios" icon="error" />
      ) : !data || data.length === 0 ? (
        <EmptyState message="No tenés coloquios registrados" icon="quiz" />
      ) : (
        <div className="overflow-x-auto rounded-xl border border-outline-variant">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-outline-variant bg-surface-container-low">
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Instancia</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Estado</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Tipo</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Dictado</th>
              </tr>
            </thead>
            <tbody>
              {data.map((col: ColoquioProfesor) => (
                <tr
                  key={col.id}
                  className="border-b border-outline-variant transition-colors hover:bg-surface-container-low"
                >
                  <td className="px-4 py-3 text-body-sm font-medium text-on-surface">{col.instancia}</td>
                  <td className="px-4 py-3">
                    <span className="inline-flex items-center rounded-full bg-primary/10 px-2 py-0.5 text-label-xs font-medium text-primary">
                      {col.estado}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-body-sm text-on-surface-variant">{col.tipo}</td>
                  <td className="px-4 py-3 text-body-sm text-on-surface-variant font-mono text-xs">{col.dictado_id}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
