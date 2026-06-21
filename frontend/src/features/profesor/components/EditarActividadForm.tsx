/**
 * EditarActividadForm — form to edit an actividad's fecha_limite.
 *
 * Calls PATCH /api/v1/actividades/{actividad_id} via useMutationEditarActividad.
 * On success, dual invalidation (actividades + atrasados) is handled inside
 * the mutation's onSuccess callback (see useProfesor.ts, D3).
 */
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutationEditarActividad } from '../hooks/useProfesor';
import { Button } from '@/shared/components/ds';
import type { Actividad } from '../types';

const editarActividadSchema = z.object({
  fecha_limite: z.string().nullable().optional(),
});

type EditarActividadForm = z.infer<typeof editarActividadSchema>;

interface EditarActividadFormProps {
  actividad: Actividad;
  dictadoId: string;
  onClose: () => void;
}

export function EditarActividadForm({ actividad, dictadoId, onClose }: EditarActividadFormProps) {
  const mutation = useMutationEditarActividad(dictadoId);

  const { register, handleSubmit } = useForm<EditarActividadForm>({
    resolver: zodResolver(editarActividadSchema),
    defaultValues: {
      fecha_limite: actividad.fecha_limite ?? '',
    },
  });

  const onSubmit = async (values: EditarActividadForm) => {
    await mutation.mutateAsync({
      actividadId: actividad.id,
      data: { fecha_limite: values.fecha_limite || null },
    });
    onClose();
  };

  return (
    <div className="space-y-4">
      <h4 style={{ margin: 0, fontSize: 16, fontWeight: 600, color: 'var(--on-surface)' }}>
        Editar actividad: {actividad.nombre}
      </h4>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label
            htmlFor="editar-fecha-limite"
            style={{ fontSize: 13, color: 'var(--on-surface-variant)', display: 'block', marginBottom: 4 }}
          >
            Fecha límite
          </label>
          <input
            id="editar-fecha-limite"
            type="date"
            {...register('fecha_limite')}
            className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-label-sm text-on-surface outline-none focus:border-primary"
          />
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <Button type="submit" variant="primary" size="sm" disabled={mutation.isPending}>
            {mutation.isPending ? 'Guardando…' : 'Guardar'}
          </Button>
          <Button type="button" variant="secondary" size="sm" onClick={onClose}>
            Cancelar
          </Button>
        </div>
        {mutation.isError && (
          <p style={{ fontSize: 13, color: 'var(--error)' }}>Error al editar la actividad</p>
        )}
      </form>
    </div>
  );
}
