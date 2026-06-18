import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useCrearTarea } from '../hooks/useTareas';

const tareaSchema = z.object({
  titulo: z.string().min(1, 'El título es requerido'),
  descripcion: z.string().min(1, 'La descripción es requerida'),
  asignado_id: z.string().min(1, 'Seleccioná un usuario asignado'),
  materia_id: z.string().optional(),
  cohorte_id: z.string().optional(),
});

type TareaForm = z.infer<typeof tareaSchema>;

export function TareaCrearPage() {
  const navigate = useNavigate();
  const crearTarea = useCrearTarea();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<TareaForm>({
    resolver: zodResolver(tareaSchema),
    defaultValues: {
      titulo: '',
      descripcion: '',
      asignado_id: '',
      materia_id: '',
      cohorte_id: '',
    },
  });

  const onSubmit = async (data: TareaForm) => {
    try {
      const tarea = await crearTarea.mutateAsync({
        ...data,
        materia_id: data.materia_id || undefined,
        cohorte_id: data.cohorte_id || undefined,
      });
      navigate(`/tareas/${tarea.id}`);
    } catch {
      // handled by mutation error state
    }
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h2 className="font-headline-lg text-headline-lg text-on-surface">Crear Tarea</h2>
        <p className="text-body-md text-on-surface-variant mt-1">
          Asigná una nueva tarea a un usuario del sistema.
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label className="mb-1 block text-label-sm text-on-surface-variant">Título</label>
          <input
            {...register('titulo')}
            placeholder="Ej: Revisar entregas del módulo 3"
            className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none placeholder:text-outline focus:border-primary"
          />
          {errors.titulo && <p className="mt-1 text-label-xs text-error">{errors.titulo.message}</p>}
        </div>

        <div>
          <label className="mb-1 block text-label-sm text-on-surface-variant">Descripción</label>
          <textarea
            {...register('descripcion')}
            rows={4}
            placeholder="Detalle de la tarea a realizar..."
            className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none placeholder:text-outline focus:border-primary"
          />
          {errors.descripcion && <p className="mt-1 text-label-xs text-error">{errors.descripcion.message}</p>}
        </div>

        <div>
          <label className="mb-1 block text-label-sm text-on-surface-variant">Asignado a (ID)</label>
          <input
            {...register('asignado_id')}
            placeholder="ID del usuario"
            className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none placeholder:text-outline focus:border-primary"
          />
          {errors.asignado_id && <p className="mt-1 text-label-xs text-error">{errors.asignado_id.message}</p>}
        </div>

        <div>
          <label className="mb-1 block text-label-sm text-on-surface-variant">Materia (opcional)</label>
          <input
            {...register('materia_id')}
            placeholder="ID de la materia"
            className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none placeholder:text-outline focus:border-primary"
          />
        </div>

        <div>
          <label className="mb-1 block text-label-sm text-on-surface-variant">Cohorte (opcional)</label>
          <input
            {...register('cohorte_id')}
            placeholder="ID de la cohorte"
            className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none placeholder:text-outline focus:border-primary"
          />
        </div>

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={crearTarea.isPending}
            className="inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-2.5 text-label-sm font-medium text-on-primary transition-colors hover:bg-primary/90 disabled:opacity-50"
          >
            {crearTarea.isPending && (
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-on-primary/30 border-t-on-primary" />
            )}
            Crear Tarea
          </button>
          <button
            type="button"
            onClick={() => navigate('/tareas')}
            className="rounded-lg border border-outline-variant px-6 py-2.5 text-label-sm font-medium text-on-surface transition-colors hover:bg-surface-container-low"
          >
            Cancelar
          </button>
        </div>

        {crearTarea.isError && (
          <div className="rounded-xl border border-error/30 bg-error/5 p-4 text-body-sm text-error">
            Error al crear la tarea. Intentá de nuevo.
          </div>
        )}
      </form>
    </div>
  );
}
