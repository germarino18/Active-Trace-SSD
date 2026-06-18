import { useNavigate } from 'react-router-dom';
import { useTutorAlumnos } from '../hooks/useTutorAlumnos';
import { LoadingState } from '@/features/academico/components/LoadingState';
import { EmptyState } from '@/features/academico/components/EmptyState';
import { ErrorState } from '../components/ErrorState';

export function TutorAlumnosPage() {
  const navigate = useNavigate();
  const { data, isLoading, isError, refetch } = useTutorAlumnos();

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-headline-lg text-headline-lg text-on-surface">Mis Alumnos</h2>
        <p className="text-body-md text-on-surface-variant mt-1">
          Listado de alumnos asignados a tus materias.
        </p>
      </div>

      {isLoading ? (
        <LoadingState rows={6} cols={5} />
      ) : isError ? (
        <ErrorState onRetry={() => refetch()} />
      ) : !data || data.length === 0 ? (
        <EmptyState message="No hay alumnos asignados" icon="group_off" />
      ) : (
        <div className="overflow-x-auto rounded-xl border border-outline-variant">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-outline-variant bg-surface-container-low">
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Nombre</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Apellido</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Email</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Materia</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Comisión</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {data.map((alumno) => (
                <tr
                  key={alumno.id}
                  className="border-b border-outline-variant transition-colors hover:bg-surface-container-low"
                >
                  <td className="px-4 py-3 text-body-sm text-on-surface">{alumno.nombre}</td>
                  <td className="px-4 py-3 text-body-sm text-on-surface">{alumno.apellido}</td>
                  <td className="px-4 py-3 text-body-sm text-on-surface-variant">{alumno.email}</td>
                  <td className="px-4 py-3 text-body-sm text-on-surface-variant">{alumno.materia_nombre}</td>
                  <td className="px-4 py-3 text-body-sm text-on-surface-variant">{alumno.comision}</td>
                  <td className="px-4 py-3">
                    <button
                      type="button"
                      onClick={() => navigate(`/materias/${alumno.id}`)}
                      className="inline-flex items-center gap-1 rounded-lg bg-primary/10 px-2.5 py-1 text-label-xs font-medium text-primary transition-colors hover:bg-primary/20"
                    >
                      Ver detalle
                    </button>
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
