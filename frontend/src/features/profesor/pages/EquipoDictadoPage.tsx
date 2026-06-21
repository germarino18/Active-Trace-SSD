import { useParams } from 'react-router-dom';
import { useEquipoDictado } from '../hooks/useProfesor';
import { LoadingState } from '@/features/academico/components/LoadingState';
import { EmptyState } from '@/features/academico/components/EmptyState';
import type { MiembroEquipo } from '../types';

export function EquipoDictadoPage() {
  const { dictadoId } = useParams<{ dictadoId: string }>();
  const { data, isLoading, isError } = useEquipoDictado(dictadoId!);

  return (
    <div className="space-y-4">
      <h3 style={{ margin: 0, fontSize: 20, fontWeight: 600, color: 'var(--on-surface)' }}>Equipo Docente</h3>

      {isLoading ? (
        <LoadingState rows={4} cols={5} />
      ) : isError ? (
        <EmptyState message="Error al cargar el equipo" icon="error" />
      ) : !data || data.length === 0 ? (
        <EmptyState message="No hay miembros en el equipo de este dictado" icon="groups" />
      ) : (
        <div className="overflow-x-auto rounded-xl border border-outline-variant">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-outline-variant bg-surface-container-low">
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Nombre</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Apellidos</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Rol</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Desde</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Hasta</th>
              </tr>
            </thead>
            <tbody>
              {data.map((miembro: MiembroEquipo) => (
                <tr
                  key={miembro.usuario_id}
                  className="border-b border-outline-variant transition-colors hover:bg-surface-container-low"
                >
                  <td className="px-4 py-3 text-body-sm text-on-surface">{miembro.nombre}</td>
                  <td className="px-4 py-3 text-body-sm text-on-surface">{miembro.apellidos}</td>
                  <td className="px-4 py-3">
                    <span className="inline-flex items-center rounded-full bg-primary/10 px-2 py-0.5 text-label-xs font-medium text-primary">
                      {miembro.rol}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-body-sm text-on-surface-variant">
                    {new Date(miembro.desde).toLocaleDateString('es-AR')}
                  </td>
                  <td className="px-4 py-3 text-body-sm text-on-surface-variant">
                    {miembro.hasta ? new Date(miembro.hasta).toLocaleDateString('es-AR') : '—'}
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
