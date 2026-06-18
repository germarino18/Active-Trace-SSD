import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useCrearAviso } from '../hooks/useAvisos';
import { ScopeSelector } from '../components/ScopeSelector';
import type { AvisoScope } from '../types';

const avisoSchema = z.object({
  titulo: z.string().min(1, 'El título es requerido'),
  mensaje: z.string().min(1, 'El mensaje es requerido'),
  severidad: z.enum(['info', 'warning', 'critical']),
  vigencia_desde: z.string().min(1, 'La fecha de inicio es requerida'),
  vigencia_hasta: z.string().min(1, 'La fecha de fin es requerida'),
  requiere_ack: z.boolean(),
  orden: z.coerce.number().min(0, 'Debe ser un número positivo'),
});

type AvisoForm = z.infer<typeof avisoSchema>;

export function AvisoCrearPage() {
  const navigate = useNavigate();
  const crearAviso = useCrearAviso();
  const [scopeType, setScopeType] = useState<AvisoScope>('Global');
  const [scopeValue, setScopeValue] = useState('');

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<AvisoForm>({
    resolver: zodResolver(avisoSchema),
    defaultValues: {
      titulo: '',
      mensaje: '',
      severidad: 'info',
      vigencia_desde: '',
      vigencia_hasta: '',
      requiere_ack: false,
      orden: 0,
    },
  });

  const onSubmit = async (data: AvisoForm) => {
    try {
      await crearAviso.mutateAsync({
        ...data,
        scope: scopeType,
        scope_value: scopeValue || undefined,
      });
      navigate('/avisos');
    } catch {
      // handled by mutation error state
    }
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h2 className="font-headline-lg text-headline-lg text-on-surface">Crear Aviso</h2>
        <p className="text-body-md text-on-surface-variant mt-1">
          Creá un nuevo aviso o comunicación para el sistema.
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label className="mb-1 block text-label-sm text-on-surface-variant">Título</label>
          <input
            {...register('titulo')}
            placeholder="Ej: Recordatorio de carga de actas"
            className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none placeholder:text-outline focus:border-primary"
          />
          {errors.titulo && <p className="mt-1 text-label-xs text-error">{errors.titulo.message}</p>}
        </div>

        <div>
          <label className="mb-1 block text-label-sm text-on-surface-variant">Mensaje</label>
          <textarea
            {...register('mensaje')}
            rows={4}
            placeholder="Contenido del aviso..."
            className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none placeholder:text-outline focus:border-primary"
          />
          {errors.mensaje && <p className="mt-1 text-label-xs text-error">{errors.mensaje.message}</p>}
        </div>

        <ScopeSelector
          scopeType={scopeType}
          scopeValue={scopeValue}
          onScopeTypeChange={setScopeType}
          onScopeValueChange={setScopeValue}
        />

        <div>
          <label className="mb-1 block text-label-sm text-on-surface-variant">Severidad</label>
          <select
            {...register('severidad')}
            className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none focus:border-primary"
          >
            <option value="info">Info</option>
            <option value="warning">Advertencia</option>
            <option value="critical">Crítico</option>
          </select>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="mb-1 block text-label-sm text-on-surface-variant">Vigencia desde</label>
            <input
              type="date"
              {...register('vigencia_desde')}
              className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none focus:border-primary"
            />
            {errors.vigencia_desde && <p className="mt-1 text-label-xs text-error">{errors.vigencia_desde.message}</p>}
          </div>
          <div>
            <label className="mb-1 block text-label-sm text-on-surface-variant">Vigencia hasta</label>
            <input
              type="date"
              {...register('vigencia_hasta')}
              className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none focus:border-primary"
            />
            {errors.vigencia_hasta && <p className="mt-1 text-label-xs text-error">{errors.vigencia_hasta.message}</p>}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            {...register('requiere_ack')}
            id="requiere_ack"
            className="h-4 w-4 rounded border-outline-variant bg-surface-container-low text-primary focus:ring-primary"
          />
          <label htmlFor="requiere_ack" className="text-label-sm text-on-surface-variant">
            Requiere confirmación de lectura
          </label>
        </div>

        <div>
          <label className="mb-1 block text-label-sm text-on-surface-variant">Orden</label>
          <input
            type="number"
            {...register('orden')}
            min={0}
            className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none focus:border-primary"
          />
          {errors.orden && <p className="mt-1 text-label-xs text-error">{errors.orden.message}</p>}
        </div>

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={crearAviso.isPending}
            className="inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-2.5 text-label-sm font-medium text-on-primary transition-colors hover:bg-primary/90 disabled:opacity-50"
          >
            {crearAviso.isPending && (
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-on-primary/30 border-t-on-primary" />
            )}
            Crear Aviso
          </button>
          <button
            type="button"
            onClick={() => navigate('/avisos')}
            className="rounded-lg border border-outline-variant px-6 py-2.5 text-label-sm font-medium text-on-surface transition-colors hover:bg-surface-container-low"
          >
            Cancelar
          </button>
        </div>

        {crearAviso.isError && (
          <div className="rounded-xl border border-error/30 bg-error/5 p-4 text-body-sm text-error">
            Error al crear el aviso. Intentá de nuevo.
          </div>
        )}
      </form>
    </div>
  );
}
