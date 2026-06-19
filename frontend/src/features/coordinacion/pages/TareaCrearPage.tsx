import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useCrearTarea } from '../hooks/useTareas';
import { Button } from '@/shared/components/ds';

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
        <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Crear Tarea</h2>
        <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>
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
          <Button
            type="submit"
            variant="primary"
            disabled={crearTarea.isPending}
          >
            Crear Tarea
          </Button>
          <Button
            type="button"
            variant="secondary"
            onClick={() => navigate('/tareas')}
          >
            Cancelar
          </Button>
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
