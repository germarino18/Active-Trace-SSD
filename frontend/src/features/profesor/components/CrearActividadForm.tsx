/**
 * CrearActividadForm — form to create a new actividad in a dictado.
 *
 * Extracted from ActividadesDictadoPage to keep each file under 200 LOC.
 * Calls POST /api/v1/actividades/dictados/{dictadoId} via useMutationCrearActividad.
 * On success, dual invalidation (actividades + atrasados) is handled inside
 * the mutation's onSuccess callback (see useProfesor.ts, invalidateDictadoDerived).
 */
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutationCrearActividad } from '../hooks/useProfesor';
import { Button } from '@/shared/components/ds';
import type { ActividadCreate } from '../types';

const actividadSchema = z.object({
  nombre: z.string().min(1, 'Requerido'),
  tipo: z.string().min(1, 'Requerido'),
  fecha_limite: z.string().optional(),
});

type ActividadForm = z.infer<typeof actividadSchema>;

interface CrearActividadFormProps {
  dictadoId: string;
  onClose: () => void;
}

export function CrearActividadForm({ dictadoId, onClose }: CrearActividadFormProps) {
  const mutation = useMutationCrearActividad(dictadoId);
  const { register, handleSubmit, formState: { errors } } = useForm<ActividadForm>({
    resolver: zodResolver(actividadSchema),
    defaultValues: { nombre: '', tipo: 'tarea', fecha_limite: '' },
  });

  const onSubmit = async (values: ActividadForm) => {
    const payload: ActividadCreate = {
      nombre: values.nombre,
      tipo: values.tipo,
      fecha_limite: values.fecha_limite || null,
    };
    await mutation.mutateAsync(payload);
    onClose();
  };

  return (
    <div className="space-y-4">
      <h4 style={{ margin: 0, fontSize: 16, fontWeight: 600, color: 'var(--on-surface)' }}>
        Nueva actividad
      </h4>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
          <div>
            <label
              htmlFor="crear-nombre"
              style={{ fontSize: 12, color: 'var(--on-surface-variant)', display: 'block', marginBottom: 4 }}
            >
              Nombre *
            </label>
            <input
              id="crear-nombre"
              {...register('nombre')}
              className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-label-sm text-on-surface outline-none focus:border-primary"
            />
            {errors.nombre && (
              <p style={{ margin: '4px 0 0', fontSize: 12, color: 'var(--error)' }}>{errors.nombre.message}</p>
            )}
          </div>
          <div>
            <label
              htmlFor="crear-tipo"
              style={{ fontSize: 12, color: 'var(--on-surface-variant)', display: 'block', marginBottom: 4 }}
            >
              Tipo *
            </label>
            <select
              id="crear-tipo"
              {...register('tipo')}
              className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-label-sm text-on-surface outline-none focus:border-primary"
            >
              <option value="tarea">Tarea</option>
              <option value="examen">Examen</option>
              <option value="tp">Trabajo Práctico</option>
              <option value="parcial">Parcial</option>
              <option value="coloquio">Coloquio</option>
              <option value="otro">Otro</option>
            </select>
            {errors.tipo && (
              <p style={{ margin: '4px 0 0', fontSize: 12, color: 'var(--error)' }}>{errors.tipo.message}</p>
            )}
          </div>
        </div>
        <div>
          <label
            htmlFor="crear-fecha-limite"
            style={{ fontSize: 12, color: 'var(--on-surface-variant)', display: 'block', marginBottom: 4 }}
          >
            Fecha límite
          </label>
          <input
            id="crear-fecha-limite"
            type="date"
            {...register('fecha_limite')}
            className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-label-sm text-on-surface outline-none focus:border-primary"
          />
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <Button type="submit" variant="primary" size="sm" disabled={mutation.isPending}>
            {mutation.isPending ? 'Guardando…' : 'Crear actividad'}
          </Button>
          <Button type="button" variant="secondary" size="sm" onClick={onClose}>
            Cancelar
          </Button>
        </div>
        {mutation.isError && (
          <p style={{ fontSize: 13, color: 'var(--error)' }}>Error al crear la actividad</p>
        )}
      </form>
    </div>
  );
}
