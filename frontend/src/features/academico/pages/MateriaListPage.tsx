import { useAuth } from '@/features/auth/hooks/useAuth';

export function MateriaListPage() {
  const { session } = useAuth();

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-headline-lg text-headline-lg text-on-surface">Mis Materias</h2>
        <p className="text-body-md text-on-surface-variant mt-1">
          Seleccioná una materia para gestionar sus calificaciones y alumnos.
        </p>
      </div>

      <div className="rounded-xl border border-outline-variant bg-surface-container-lowest p-md">
        <p className="text-body-md text-on-surface-variant">
          La lista de materias se integrará con el backend en próximas actualizaciones.
        </p>
      </div>
    </div>
  );
}
