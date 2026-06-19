import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAviso, useActualizarAviso } from '../hooks/useAvisos';
import { ScopeSelector } from '../components/ScopeSelector';
import { Spinner } from '@/shared/components/Spinner';
import type { AvisoScope } from '../types';
import { Button } from '@/shared/components/ds';

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

export function AvisoEditarPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: aviso, isLoading } = useAviso(id);
  const actualizarAviso = useActualizarAviso();
  const [scopeType, setScopeType] = useState<AvisoScope>('Global');
  const [scopeValue, setScopeValue] = useState('');

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<AvisoForm>({
    resolver: zodResolver(avisoSchema),
  });

  useEffect(() => {
    if (aviso) {
      reset({
        titulo: aviso.titulo,
        mensaje: aviso.mensaje,
        severidad: aviso.severidad,
        vigencia_desde: aviso.vigencia_desde,
        vigencia_hasta: aviso.vigencia_hasta,
        requiere_ack: aviso.requiere_ack,
        orden: aviso.orden,
      });
      setScopeType(aviso.scope);
      setScopeValue(aviso.scope_value ?? '');
    }
  }, [aviso, reset]);

  const onSubmit = async (data: AvisoForm) => {
    if (!id) return;
    try {
      await actualizarAviso.mutateAsync({
        id,
        data: {
          ...data,
          scope: scopeType,
          scope_value: scopeValue || undefined,
        },
      });
      navigate('/avisos');
    } catch {
      // handled by mutation error state
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!aviso) {
    return (
      <div className="rounded-xl border border-error/30 bg-error/5 p-4 text-body-sm text-error">
        Aviso no encontrado.
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Editar Aviso</h2>
        <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>
          Actualizá los datos del aviso.
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label className="mb-1 block text-label-sm text-on-surface-variant">Título</label>
          <input
            {...register('titulo')}
            className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none placeholder:text-outline focus:border-primary"
          />
          {errors.titulo && <p className="mt-1 text-label-xs text-error">{errors.titulo.message}</p>}
        </div>

        <div>
          <label className="mb-1 block text-label-sm text-on-surface-variant">Mensaje</label>
          <textarea
            {...register('mensaje')}
            rows={4}
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
          <Button
            type="submit"
            variant="primary"
            disabled={actualizarAviso.isPending}
          >
            Guardar Cambios
          </Button>
          <Button
            type="button"
            variant="secondary"
            onClick={() => navigate('/avisos')}
          >
            Cancelar
          </Button>
        </div>

        {actualizarAviso.isError && (
          <div className="rounded-xl border border-error/30 bg-error/5 p-4 text-body-sm text-error">
            Error al actualizar el aviso. Intentá de nuevo.
          </div>
        )}
      </form>
    </div>
  );
}
