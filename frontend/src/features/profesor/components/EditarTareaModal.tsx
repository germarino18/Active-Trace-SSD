/**
 * EditarTareaModal — portal overlay modal for editing a tarea propia.
 *
 * Renders via ActividadOverlayModal (createPortal to document.body) to avoid
 * the position:absolute clipping bug inside overflow-x-auto tables.
 * Allows editing descripcion, estado, and materia_id.
 * Calls PATCH /api/v1/tareas/mias/{id} via useMutationEditarTareaPropia.
 */
import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { ActividadOverlayModal } from './ActividadOverlayModal';
import { Button } from '@/shared/components/ds';
import { useMutationEditarTareaPropia } from '../hooks/useProfesor';
import type { TareaProfesor } from '../types';

const ESTADO_OPTIONS = [
  { value: 'PENDIENTE', label: 'Pendiente' },
  { value: 'EN_PROGRESO', label: 'En progreso' },
  { value: 'RESUELTA', label: 'Resuelta' },
  { value: 'CANCELADA', label: 'Cancelada' },
];

const editarTareaSchema = z.object({
  descripcion: z.string().min(1, 'Requerido'),
  estado: z.string().min(1, 'Requerido'),
  materia_id: z.string().nullable().optional(),
});

type EditarTareaForm = z.infer<typeof editarTareaSchema>;

interface EditarTareaModalProps {
  open: boolean;
  tarea: TareaProfesor | null;
  onClose: () => void;
}

export function EditarTareaModal({ open, tarea, onClose }: EditarTareaModalProps) {
  const mutation = useMutationEditarTareaPropia();
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<EditarTareaForm>({
    resolver: zodResolver(editarTareaSchema),
    defaultValues: {
      descripcion: tarea?.descripcion ?? '',
      estado: tarea?.estado ?? 'PENDIENTE',
      materia_id: tarea?.materia_id ?? null,
    },
  });

  // Sync form values when the selected tarea changes
  useEffect(() => {
    if (tarea) {
      reset({
        descripcion: tarea.descripcion,
        estado: tarea.estado,
        materia_id: tarea.materia_id ?? null,
      });
    }
  }, [tarea, reset]);

  const onSubmit = async (values: EditarTareaForm) => {
    if (!tarea) return;
    await mutation.mutateAsync({
      tareaId: tarea.id,
      data: {
        descripcion: values.descripcion,
        estado: values.estado,
        materia_id: values.materia_id ?? null,
      },
    });
    onClose();
  };

  return (
    <ActividadOverlayModal open={open} onClose={onClose}>
      <div className="space-y-4">
        <h4 style={{ margin: 0, fontSize: 16, fontWeight: 600, color: 'var(--on-surface)' }}>
          Editar tarea
        </h4>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label
              htmlFor="editar-tarea-descripcion"
              style={{ fontSize: 12, color: 'var(--on-surface-variant)', display: 'block', marginBottom: 4 }}
            >
              Descripción *
            </label>
            <textarea
              id="editar-tarea-descripcion"
              {...register('descripcion')}
              rows={3}
              className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-label-sm text-on-surface outline-none focus:border-primary resize-none"
            />
            {errors.descripcion && (
              <p style={{ margin: '4px 0 0', fontSize: 12, color: 'var(--error)' }}>
                {errors.descripcion.message}
              </p>
            )}
          </div>
          <div>
            <label
              htmlFor="editar-tarea-estado"
              style={{ fontSize: 12, color: 'var(--on-surface-variant)', display: 'block', marginBottom: 4 }}
            >
              Estado *
            </label>
            <select
              id="editar-tarea-estado"
              {...register('estado')}
              className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-label-sm text-on-surface outline-none focus:border-primary"
            >
              {ESTADO_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
            {errors.estado && (
              <p style={{ margin: '4px 0 0', fontSize: 12, color: 'var(--error)' }}>
                {errors.estado.message}
              </p>
            )}
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
            <p style={{ fontSize: 13, color: 'var(--error)' }}>Error al guardar</p>
          )}
        </form>
      </div>
    </ActividadOverlayModal>
  );
}
