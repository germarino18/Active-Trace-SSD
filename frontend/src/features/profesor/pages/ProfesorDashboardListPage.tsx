import { Link } from 'react-router-dom';
import { useProfesorDashboard } from '../hooks/useProfesor';
import { LoadingState } from '@/features/academico/components/LoadingState';
import { EmptyState } from '@/features/academico/components/EmptyState';
import type { DictadoResumen } from '../types';

export function ProfesorDashboardListPage() {
  const { data, isLoading, isError } = useProfesorDashboard();

  return (
    <div className="space-y-6">
      <div>
        <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>
          Mis Dictados
        </h2>
        <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>
          Dictados asignados a tu usuario en el período vigente.
        </p>
      </div>

      {isLoading ? (
        <LoadingState rows={4} cols={3} />
      ) : isError ? (
        <EmptyState message="Error al cargar los dictados" icon="error" />
      ) : !data || data.materias_asignadas.length === 0 ? (
        <EmptyState message="No tenés dictados asignados" icon="class" />
      ) : (
        <div className="overflow-x-auto rounded-xl border border-outline-variant">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-outline-variant bg-surface-container-low">
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Materia</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Alumnos</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {data.materias_asignadas.map((dictado: DictadoResumen) => (
                <tr
                  key={dictado.dictado_id}
                  className="border-b border-outline-variant transition-colors hover:bg-surface-container-low"
                >
                  <td className="px-4 py-3 text-body-sm font-medium text-on-surface">
                    {dictado.materia_nombre}
                  </td>
                  <td className="px-4 py-3 text-body-sm text-on-surface-variant">
                    {dictado.n_alumnos}
                  </td>
                  <td className="px-4 py-3">
                    <Link
                      to={`/profesor/dictados/${dictado.dictado_id}`}
                      className="inline-flex items-center gap-1 rounded-lg bg-primary/10 px-3 py-1.5 text-label-xs font-medium text-primary transition-colors hover:bg-primary/20"
                    >
                      <span className="material-symbols-outlined text-[14px]">open_in_new</span>
                      Ver dictado
                    </Link>
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
