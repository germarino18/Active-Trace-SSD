import { useNavigate } from 'react-router-dom';
import { useFieldArray, useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useCrearConvocatoria } from '../hooks/useColoquios';
import { Button } from '@/shared/components/ds';

const diaSchema = z.object({
  fecha: z.string().min(1, 'La fecha es requerida'),
  hora_inicio: z.string().min(1, 'Requerido'),
  hora_fin: z.string().min(1, 'Requerido'),
  slots: z.number().min(1, 'Mínimo 1 slot'),
  cupo_por_slot: z.number().min(1, 'Mínimo 1 cupo'),
});

const formSchema = z.object({
  materia_id: z.string().min(1, 'Seleccioná una materia'),
  instancia: z.number().min(1, 'Número de instancia requerido'),
  dias: z.array(diaSchema).min(1, 'Agregá al menos un día'),
});

type FormValues = z.infer<typeof formSchema>;

export function ConvocatoriaCrearPage() {
  const navigate = useNavigate();
  const crearConvocatoria = useCrearConvocatoria();

  const {
    register,
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      materia_id: '',
      instancia: 1,
      dias: [
        { fecha: '', hora_inicio: '09:00', hora_fin: '12:00', slots: 4, cupo_por_slot: 3 },
      ],
    },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'dias',
  });

  const onSubmit = async (data: FormValues) => {
    try {
      await crearConvocatoria.mutateAsync(data);
      navigate('/coloquios');
    } catch {
      // handled by mutation error state
    }
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Nueva Convocatoria</h2>
        <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>
          Creá una convocatoria a coloquio con sus días y cupos.
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div className="space-y-4 rounded-xl border border-outline-variant bg-surface-container-lowest p-6">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block text-label-sm text-on-surface-variant">Materia</label>
              <input
                {...register('materia_id')}
                placeholder="ID de la materia"
                className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none placeholder:text-outline focus:border-primary"
              />
              {errors.materia_id && (
                <p className="mt-1 text-label-xs text-error">{errors.materia_id.message}</p>
              )}
            </div>
            <div>
              <label className="mb-1 block text-label-sm text-on-surface-variant">N° de Instancia</label>
              <input
                type="number"
                {...register('instancia', { valueAsNumber: true })}
                min={1}
                className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none focus:border-primary"
              />
              {errors.instancia && (
                <p className="mt-1 text-label-xs text-error">{errors.instancia.message}</p>
              )}
            </div>
          </div>
        </div>

        <div className="space-y-4 rounded-xl border border-outline-variant bg-surface-container-lowest p-6">
          <div className="flex items-center justify-between">
            <h3 className="font-headline-sm text-headline-sm text-on-surface">Días</h3>
            {errors.dias && (
              <p className="text-label-xs text-error">{errors.dias.message ?? errors.dias.root?.message}</p>
            )}
          </div>

          <div className="space-y-3">
            {fields.map((field, index) => (
              <div key={field.id} className="rounded-lg border border-outline-variant bg-surface-container p-4">
                <div className="mb-3 flex items-center justify-between">
                  <span className="text-label-sm font-medium text-on-surface-variant">Día {index + 1}</span>
                  {fields.length > 1 && (
                    <button
                      type="button"
                      onClick={() => remove(index)}
                      className="inline-flex items-center gap-1 text-label-xs text-error hover:underline"
                    >
                      <span className="material-symbols-outlined text-[14px]">delete</span>
                      Quitar
                    </button>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="mb-1 block text-label-xs text-on-surface-variant">Fecha</label>
                    <input
                      type="date"
                      {...register(`dias.${index}.fecha`)}
                      className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none focus:border-primary"
                    />
                    {errors.dias?.[index]?.fecha && (
                      <p className="mt-1 text-label-xs text-error">{errors.dias[index]?.fecha?.message}</p>
                    )}
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="mb-1 block text-label-xs text-on-surface-variant">Inicio</label>
                      <input
                        type="time"
                        {...register(`dias.${index}.hora_inicio`)}
                        className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none focus:border-primary"
                      />
                    </div>
                    <div>
                      <label className="mb-1 block text-label-xs text-on-surface-variant">Fin</label>
                      <input
                        type="time"
                        {...register(`dias.${index}.hora_fin`)}
                        className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none focus:border-primary"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="mb-1 block text-label-xs text-on-surface-variant">Slots</label>
                    <input
                      type="number"
                      {...register(`dias.${index}.slots`, { valueAsNumber: true })}
                      min={1}
                      className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none focus:border-primary"
                    />
                  </div>
                  <div>
                    <label className="mb-1 block text-label-xs text-on-surface-variant">Cupo por slot</label>
                    <input
                      type="number"
                      {...register(`dias.${index}.cupo_por_slot`, { valueAsNumber: true })}
                      min={1}
                      className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none focus:border-primary"
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>

          <button
            type="button"
            onClick={() => append({ fecha: '', hora_inicio: '09:00', hora_fin: '12:00', slots: 4, cupo_por_slot: 3 })}
            className="inline-flex items-center gap-2 rounded-lg border border-dashed border-outline-variant bg-surface-container-lowest px-4 py-2 text-label-sm text-on-surface-variant transition-colors hover:border-primary hover:text-primary"
          >
            <span className="material-symbols-outlined text-[18px]">add</span>
            Agregar día
          </button>
        </div>

        <div className="flex gap-3">
          <Button
            type="submit"
            variant="primary"
            disabled={crearConvocatoria.isPending}
          >
            Crear Convocatoria
          </Button>
          <Button
            type="button"
            variant="secondary"
            onClick={() => navigate('/coloquios')}
          >
            Cancelar
          </Button>
        </div>

        {crearConvocatoria.isError && (
          <p className="text-label-sm text-error">Error al crear la convocatoria. Intentalo de nuevo.</p>
        )}
      </form>
    </div>
  );
}
