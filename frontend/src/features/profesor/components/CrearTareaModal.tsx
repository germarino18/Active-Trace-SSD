/**
 * CrearTareaModal — portal overlay modal for creating a new tarea propia.
 *
 * Renders via ActividadOverlayModal (createPortal to document.body) so it
 * is never clipped by overflow-x-auto table containers.
 * Calls POST /api/v1/tareas/mias via useMutationCrearTareaPropia.
 */
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { ActividadOverlayModal } from './ActividadOverlayModal';
import { Button } from '@/shared/components/ds';
import { useMutationCrearTareaPropia } from '../hooks/useProfesor';

const crearTareaSchema = z.object({
  descripcion: z.string().min(1, 'Requerido'),
  materia_id: z.string().nullable().optional(),
});

type CrearTareaForm = z.infer<typeof crearTareaSchema>;

interface CrearTareaModalProps {
  open: boolean;
  onClose: () => void;
}

export function CrearTareaModal({ open, onClose }: CrearTareaModalProps) {
  const mutation = useMutationCrearTareaPropia();
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<CrearTareaForm>({
    resolver: zodResolver(crearTareaSchema),
    defaultValues: { descripcion: '', materia_id: null },
  });

  const onSubmit = async (values: CrearTareaForm) => {
    await mutation.mutateAsync({
      descripcion: values.descripcion,
      materia_id: values.materia_id ?? null,
    });
    reset();
    onClose();
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  return (
    <ActividadOverlayModal open={open} onClose={handleClose}>
      <div className="space-y-4">
        <h4 style={{ margin: 0, fontSize: 16, fontWeight: 600, color: 'var(--on-surface)' }}>
          Nueva tarea
        </h4>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label
              htmlFor="crear-tarea-descripcion"
              style={{ fontSize: 12, color: 'var(--on-surface-variant)', display: 'block', marginBottom: 4 }}
            >
              Descripción *
            </label>
            <textarea
              id="crear-tarea-descripcion"
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
              htmlFor="crear-tarea-materia"
              style={{ fontSize: 12, color: 'var(--on-surface-variant)', display: 'block', marginBottom: 4 }}
            >
              Materia (opcional)
            </label>
            <input
              id="crear-tarea-materia"
              {...register('materia_id')}
              placeholder="ID de materia (opcional)"
              className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-label-sm text-on-surface outline-none focus:border-primary"
            />
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <Button type="submit" variant="primary" size="sm" disabled={mutation.isPending}>
              {mutation.isPending ? 'Guardando…' : 'Guardar'}
            </Button>
            <Button type="button" variant="secondary" size="sm" onClick={handleClose}>
              Cancelar
            </Button>
          </div>
          {mutation.isError && (
            <p style={{ fontSize: 13, color: 'var(--error)' }}>Error al crear la tarea</p>
          )}
        </form>
      </div>
    </ActividadOverlayModal>
  );
}
