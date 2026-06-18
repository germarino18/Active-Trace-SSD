import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { useDocentes, useCrearAsignacion } from '../hooks/useEquipos';
import { HelpButton } from '../components/HelpButton';
import { Spinner } from '@/shared/components/Spinner';
import { EmptyState } from '@/features/academico/components/EmptyState';

const asignacionSchema = z.object({
  usuario_id: z.string().min(1, 'Seleccioná un docente'),
  materia_id: z.string().min(1, 'Seleccioná una materia'),
  carrera_id: z.string().min(1, 'Seleccioná una carrera'),
  cohorte_id: z.string().min(1, 'Seleccioná una cohorte'),
  rol: z.enum(['PROFESOR', 'TUTOR', 'NEXO', 'COORDINADOR'], {
    error: 'Seleccioná un rol',
  }),
  vigencia_desde: z.string().min(1, 'Seleccioná una fecha de inicio'),
  vigencia_hasta: z.string().min(1, 'Seleccioná una fecha de fin'),
});

type AsignacionFormData = z.infer<typeof asignacionSchema>;

export function AsignacionIndividualPage() {
  const { hasAnyPermission } = useAuth();
  const navigate = useNavigate();
  const { data: docentes, isLoading: docentesLoading } = useDocentes();
  const crearMutation = useCrearAsignacion();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<AsignacionFormData>({
    resolver: zodResolver(asignacionSchema),
    defaultValues: {
      usuario_id: '',
      materia_id: '',
      carrera_id: '',
      cohorte_id: '',
      rol: undefined,
      vigencia_desde: '',
      vigencia_hasta: '',
    },
  });

  if (!hasAnyPermission(['COORDINADOR', 'ADMIN'])) {
    return <EmptyState message="No tenés permisos para crear asignaciones" icon="lock" />;
  }

  const onSubmit = async (data: AsignacionFormData) => {
    try {
      await crearMutation.mutateAsync(data);
      reset();
      navigate('/equipos');
    } catch {
      // Error handled by mutation
    }
  };

  const fieldClass = 'w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary';
  const errorClass = 'text-label-xs text-error mt-1';
  const labelClass = 'text-label-xs font-medium text-outline uppercase tracking-wider';

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="flex items-center gap-2">
        <div>
          <h2 className="font-headline-lg text-headline-lg text-on-surface">Nueva Asignación</h2>
          <p className="text-body-md text-on-surface-variant mt-1">
            Asigná un docente a una materia con rol y vigencia
          </p>
        </div>
        <HelpButton tooltip="Creá una asignación individual. Seleccioná el docente, la materia, carrera, cohorte, el rol que cumplirá y las fechas de vigencia." />
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
        <div className="rounded-xl border border-outline-variant bg-surface-container-lowest p-md space-y-5">
          <div className="space-y-1">
            <label className={labelClass}>Docente</label>
            {docentesLoading ? (
              <Spinner size="sm" />
            ) : (
              <select {...register('usuario_id')} className={fieldClass}>
                <option value="">Seleccionar docente...</option>
                {docentes?.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.apellido}, {d.nombre} — {d.email}
                  </option>
                ))}
              </select>
            )}
            {errors.usuario_id && (
              <p className={errorClass}>{errors.usuario_id.message}</p>
            )}
          </div>

          <div className="space-y-1">
            <label className={labelClass}>Materia</label>
            <input
              {...register('materia_id')}
              placeholder="ID de la materia"
              className={fieldClass}
            />
            {errors.materia_id && (
              <p className={errorClass}>{errors.materia_id.message}</p>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className={labelClass}>Carrera</label>
              <input
                {...register('carrera_id')}
                placeholder="ID de la carrera"
                className={fieldClass}
              />
              {errors.carrera_id && (
                <p className={errorClass}>{errors.carrera_id.message}</p>
              )}
            </div>

            <div className="space-y-1">
              <label className={labelClass}>Cohorte</label>
              <input
                {...register('cohorte_id')}
                placeholder="ID de la cohorte"
                className={fieldClass}
              />
              {errors.cohorte_id && (
                <p className={errorClass}>{errors.cohorte_id.message}</p>
              )}
            </div>
          </div>

          <div className="space-y-1">
            <label className={labelClass}>Rol</label>
            <select {...register('rol')} className={fieldClass}>
              <option value="">Seleccionar rol...</option>
              <option value="PROFESOR">Profesor</option>
              <option value="TUTOR">Tutor</option>
              <option value="NEXO">Nexo</option>
              <option value="COORDINADOR">Coordinador</option>
            </select>
            {errors.rol && (
              <p className={errorClass}>{errors.rol.message}</p>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className={labelClass}>Vigencia desde</label>
              <input type="date" {...register('vigencia_desde')} className={fieldClass} />
              {errors.vigencia_desde && (
                <p className={errorClass}>{errors.vigencia_desde.message}</p>
              )}
            </div>

            <div className="space-y-1">
              <label className={labelClass}>Vigencia hasta</label>
              <input type="date" {...register('vigencia_hasta')} className={fieldClass} />
              {errors.vigencia_hasta && (
                <p className={errorClass}>{errors.vigencia_hasta.message}</p>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center justify-end gap-3">
          <button
            type="button"
            onClick={() => navigate('/equipos')}
            className="rounded-lg border border-outline-variant px-4 py-2 text-label-sm font-medium text-on-surface transition-colors hover:bg-surface-container-low"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={isSubmitting}
            className="rounded-lg bg-primary px-4 py-2 text-label-sm font-medium text-on-primary transition-colors hover:bg-primary/90 disabled:opacity-50"
          >
            {isSubmitting ? 'Creando...' : 'Crear asignación'}
          </button>
        </div>
      </form>
    </div>
  );
}
